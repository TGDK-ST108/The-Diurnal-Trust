from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Callable, Any, Optional
import platform
import os
import time


# ==========================================
# RYZEN COMPLEX ADAPTER
# excessive • strong • adaptable
# ==========================================

class WorkloadType(str, Enum):
    COMPUTE = "compute"
    IO = "io"
    AI = "ai"
    RENDER = "render"
    GAMING = "gaming"
    BACKGROUND = "background"
    MIXED = "mixed"


class PowerMode(str, Enum):
    ECO = "eco"
    BALANCED = "balanced"
    PERFORMANCE = "performance"
    EXTREME = "extreme"


@dataclass
class AdapterSignal:
    name: str
    value: Any
    confidence: float = 1.0


@dataclass
class WorkloadRequest:
    name: str
    workload_type: WorkloadType
    priority: int = 5
    thread_hint: Optional[int] = None
    memory_hint_mb: Optional[int] = None
    gpu_preferred: bool = False
    latency_sensitive: bool = False
    duration_hint_s: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AdapterProfile:
    mode: PowerMode
    max_threads: int
    preferred_ccx_spread: bool
    smt_enabled: bool
    thermal_guard_c: int
    memory_pressure_limit_mb: int
    io_boost: bool
    notes: str = ""


@dataclass
class AdapterDecision:
    request_name: str
    selected_profile: AdapterProfile
    assigned_threads: int
    cpu_affinity: List[int]
    memory_budget_mb: int
    queue_class: str
    predicted_behavior: str
    rationale: List[str] = field(default_factory=list)


class StrategyEngine:
    def __init__(self):
        self.rules: List[Callable[[WorkloadRequest, Dict[str, AdapterSignal]], Optional[PowerMode]]] = []

    def register(self, rule: Callable[[WorkloadRequest, Dict[str, AdapterSignal]], Optional[PowerMode]]) -> None:
        self.rules.append(rule)

    def resolve_mode(self, request: WorkloadRequest, telemetry: Dict[str, AdapterSignal]) -> PowerMode:
        for rule in self.rules:
            result = rule(request, telemetry)
            if result is not None:
                return result
        return PowerMode.BALANCED


class TelemetryProbe:
    def capture(self) -> Dict[str, AdapterSignal]:
        logical = os.cpu_count() or 8
        return {
            "platform": AdapterSignal("platform", platform.system()),
            "logical_cores": AdapterSignal("logical_cores", logical),
            "cpu_load": AdapterSignal("cpu_load", self._pseudo_cpu_load()),
            "memory_free_mb": AdapterSignal("memory_free_mb", self._pseudo_memory_free_mb()),
            "thermal_estimate_c": AdapterSignal("thermal_estimate_c", self._pseudo_thermal_estimate()),
            "timestamp": AdapterSignal("timestamp", time.time()),
        }

    def _pseudo_cpu_load(self) -> float:
        # Replace with psutil.cpu_percent(interval=0.25) or a vendor-specific metric
        return 34.0

    def _pseudo_memory_free_mb(self) -> int:
        # Replace with psutil.virtual_memory().available // (1024 * 1024)
        return 16384

    def _pseudo_thermal_estimate(self) -> int:
        # Replace with platform/vendor tool integration where available
        return 67


class RyzenComplexAdapter:
    def __init__(self):
        self.telemetry = TelemetryProbe()
        self.strategy = StrategyEngine()
        self.profiles = self._build_profiles()
        self._install_default_rules()

    def _build_profiles(self) -> Dict[PowerMode, AdapterProfile]:
        logical = os.cpu_count() or 8

        return {
            PowerMode.ECO: AdapterProfile(
                mode=PowerMode.ECO,
                max_threads=max(2, logical // 4),
                preferred_ccx_spread=False,
                smt_enabled=True,
                thermal_guard_c=70,
                memory_pressure_limit_mb=2048,
                io_boost=False,
                notes="Low thermals, reduced burst behavior."
            ),
            PowerMode.BALANCED: AdapterProfile(
                mode=PowerMode.BALANCED,
                max_threads=max(4, logical // 2),
                preferred_ccx_spread=True,
                smt_enabled=True,
                thermal_guard_c=80,
                memory_pressure_limit_mb=4096,
                io_boost=True,
                notes="Stable general-purpose operating mode."
            ),
            PowerMode.PERFORMANCE: AdapterProfile(
                mode=PowerMode.PERFORMANCE,
                max_threads=max(6, int(logical * 0.75)),
                preferred_ccx_spread=True,
                smt_enabled=True,
                thermal_guard_c=88,
                memory_pressure_limit_mb=8192,
                io_boost=True,
                notes="High sustained compute throughput."
            ),
            PowerMode.EXTREME: AdapterProfile(
                mode=PowerMode.EXTREME,
                max_threads=logical,
                preferred_ccx_spread=True,
                smt_enabled=True,
                thermal_guard_c=92,
                memory_pressure_limit_mb=12288,
                io_boost=True,
                notes="Max throughput, aggressive scaling."
            ),
        }

    def _install_default_rules(self) -> None:
        def thermal_safety_rule(req: WorkloadRequest, tel: Dict[str, AdapterSignal]) -> Optional[PowerMode]:
            if tel["thermal_estimate_c"].value >= 85:
                return PowerMode.BALANCED
            return None

        def latency_rule(req: WorkloadRequest, tel: Dict[str, AdapterSignal]) -> Optional[PowerMode]:
            if req.latency_sensitive and req.priority >= 8:
                return PowerMode.PERFORMANCE
            return None

        def workload_rule(req: WorkloadRequest, tel: Dict[str, AdapterSignal]) -> Optional[PowerMode]:
            if req.workload_type in {WorkloadType.AI, WorkloadType.RENDER, WorkloadType.COMPUTE}:
                return PowerMode.EXTREME if req.priority >= 9 else PowerMode.PERFORMANCE
            if req.workload_type == WorkloadType.GAMING:
                return PowerMode.PERFORMANCE
            if req.workload_type == WorkloadType.BACKGROUND:
                return PowerMode.ECO
            return None

        def memory_pressure_rule(req: WorkloadRequest, tel: Dict[str, AdapterSignal]) -> Optional[PowerMode]:
            free_mb = tel["memory_free_mb"].value
            if free_mb < 3000:
                return PowerMode.ECO
            return None

        self.strategy.register(thermal_safety_rule)
        self.strategy.register(memory_pressure_rule)
        self.strategy.register(latency_rule)
        self.strategy.register(workload_rule)

    def decide(self, request: WorkloadRequest) -> AdapterDecision:
        telemetry = self.telemetry.capture()
        mode = self.strategy.resolve_mode(request, telemetry)
        profile = self.profiles[mode]

        assigned_threads = self._assign_threads(request, profile, telemetry)
        cpu_affinity = self._build_affinity_map(assigned_threads, telemetry, profile)
        memory_budget_mb = self._memory_budget(request, profile)
        queue_class = self._queue_class(request, profile)
        predicted_behavior = self._predict_behavior(request, profile, telemetry)
        rationale = self._build_rationale(request, profile, telemetry, assigned_threads)

        return AdapterDecision(
            request_name=request.name,
            selected_profile=profile,
            assigned_threads=assigned_threads,
            cpu_affinity=cpu_affinity,
            memory_budget_mb=memory_budget_mb,
            queue_class=queue_class,
            predicted_behavior=predicted_behavior,
            rationale=rationale,
        )

    def _assign_threads(
        self,
        request: WorkloadRequest,
        profile: AdapterProfile,
        telemetry: Dict[str, AdapterSignal]
    ) -> int:
        logical = telemetry["logical_cores"].value
        cap = min(profile.max_threads, logical)

        if request.thread_hint is not None:
            return max(1, min(request.thread_hint, cap))

        if request.workload_type == WorkloadType.BACKGROUND:
            return max(1, cap // 3)
        if request.workload_type == WorkloadType.IO:
            return max(2, cap // 2)
        if request.workload_type in {WorkloadType.AI, WorkloadType.RENDER, WorkloadType.COMPUTE}:
            return max(4, cap)
        if request.workload_type == WorkloadType.GAMING:
            return max(4, min(8, cap))

        return max(2, cap // 2)

    def _build_affinity_map(
        self,
        thread_count: int,
        telemetry: Dict[str, AdapterSignal],
        profile: AdapterProfile
    ) -> List[int]:
        logical = telemetry["logical_cores"].value
        available = list(range(logical))

        if not profile.preferred_ccx_spread:
            return available[:thread_count]

        # Spread allocation across the logical map for broader load distribution
        step = max(1, logical // max(1, thread_count))
        affinity = []
        idx = 0
        while len(affinity) < thread_count and idx < logical:
            affinity.append(idx)
            idx += step

        for core in available:
            if len(affinity) >= thread_count:
                break
            if core not in affinity:
                affinity.append(core)

        return affinity[:thread_count]

    def _memory_budget(self, request: WorkloadRequest, profile: AdapterProfile) -> int:
        if request.memory_hint_mb is not None:
            return min(request.memory_hint_mb, profile.memory_pressure_limit_mb)
        if request.workload_type == WorkloadType.AI:
            return min(8192, profile.memory_pressure_limit_mb)
        if request.workload_type == WorkloadType.RENDER:
            return min(6144, profile.memory_pressure_limit_mb)
        if request.workload_type == WorkloadType.COMPUTE:
            return min(4096, profile.memory_pressure_limit_mb)
        return min(2048, profile.memory_pressure_limit_mb)

    def _queue_class(self, request: WorkloadRequest, profile: AdapterProfile) -> str:
        if request.priority >= 9:
            return "critical"
        if request.latency_sensitive:
            return "realtime-ish"
        if request.workload_type == WorkloadType.BACKGROUND:
            return "deferred"
        return "standard"

    def _predict_behavior(
        self,
        request: WorkloadRequest,
        profile: AdapterProfile,
        telemetry: Dict[str, AdapterSignal]
    ) -> str:
        load = telemetry["cpu_load"].value
        temp = telemetry["thermal_estimate_c"].value

        if profile.mode == PowerMode.EXTREME and temp < 80:
            return "Aggressive burst, wide thread distribution, sustained throughput."
        if load > 75:
            return "Contention-aware mode, moderate burst, guarded thermals."
        if request.latency_sensitive:
            return "Fast response bias with reduced scheduling jitter."
        return "Balanced execution with adaptable scaling."

    def _build_rationale(
        self,
        request: WorkloadRequest,
        profile: AdapterProfile,
        telemetry: Dict[str, AdapterSignal],
        assigned_threads: int
    ) -> List[str]:
        return [
            f"Mode resolved to {profile.mode.value}.",
            f"Workload type: {request.workload_type.value}.",
            f"Priority level: {request.priority}.",
            f"Assigned threads: {assigned_threads}.",
            f"Thermal estimate: {telemetry['thermal_estimate_c'].value}C.",
            f"Free memory estimate: {telemetry['memory_free_mb'].value} MB.",
            profile.notes,
        ]


# ==========================================
# OPTIONAL EXECUTION WRAPPER
# ==========================================

class ExecutionAdapter:
    def __init__(self, planner: RyzenComplexAdapter):
        self.planner = planner

    def prepare(self, request: WorkloadRequest) -> Dict[str, Any]:
        decision = self.planner.decide(request)

        return {
            "request": request.name,
            "profile": decision.selected_profile.mode.value,
            "threads": decision.assigned_threads,
            "affinity": decision.cpu_affinity,
            "memory_budget_mb": decision.memory_budget_mb,
            "queue_class": decision.queue_class,
            "predicted_behavior": decision.predicted_behavior,
            "rationale": decision.rationale,
            "launch_stub": self._launch_stub(decision),
        }

    def _launch_stub(self, decision: AdapterDecision) -> Dict[str, Any]:
        return {
            "set_affinity": decision.cpu_affinity,
            "set_threads_env": {
                "OMP_NUM_THREADS": str(decision.assigned_threads),
                "MKL_NUM_THREADS": str(decision.assigned_threads),
                "OPENBLAS_NUM_THREADS": str(decision.assigned_threads),
            },
            "scheduler_hint": decision.queue_class,
        }


# ==========================================
# EXAMPLE
# ==========================================

if __name__ == "__main__":
    adapter = RyzenComplexAdapter()
    executor = ExecutionAdapter(adapter)

    req = WorkloadRequest(
        name="ryzen_adaptive_ai_pipeline",
        workload_type=WorkloadType.AI,
        priority=10,
        latency_sensitive=True,
        gpu_preferred=True,
        memory_hint_mb=10000,
        metadata={
            "domain": "training/inference",
            "style": "excessive-strong-adaptable",
        }
    )

    plan = executor.prepare(req)

    from pprint import pprint
    pprint(plan)
