from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json
import re


# =========================
# STALDWELL DATA MODELS
# =========================

@dataclass
class StaldwellInput:
    query: str
    state: str
    target: str
    procedure: List[str] = field(default_factory=list)
    window: str = "unspecified"
    assets: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    signals: List[str] = field(default_factory=list)
    team_ranks: List[str] = field(default_factory=list)
    policy: str = "ColdSmart"


@dataclass
class RankedPath:
    name: str = ""
    procedure: List[str] = field(default_factory=list)
    probability: float = 0.0
    risk: str = "medium"
    cost: str = "medium"
    time_to_result: str = ""
    reason: str = ""


@dataclass
class BestPath:
    name: str = ""
    reason: str = ""
    procedure: List[str] = field(default_factory=list)
    confidence_band: str = ""


@dataclass
class StaldwellResult:
    state_assessment: str = ""
    target_assessment: str = ""
    top_paths: List[RankedPath] = field(default_factory=list)
    best_path: BestPath = field(default_factory=BestPath)
    failure_triggers: List[str] = field(default_factory=list)
    fallback_route: List[str] = field(default_factory=list)
    immediate_next_move: str = ""


# =========================
# STALDWELL CORE
# =========================

class Staldwell:
    """
    Staldwell = procedural outcome forecasting interface.
    It does not predict the future. It ranks procedural branches.
    """

    SYSTEM_PROMPT = """
You are Staldwell, a procedural outcome forecasting interface operating under ColdSmart Policy.

Rules:
- Do not claim certainty.
- Do not invent unavailable facts.
- Do not act like an oracle.
- Use state, procedure, constraints, signals, risks, assets, and team ranks.
- Build at least 3 procedural branches when possible.
- Rank branches by feasibility, speed, resilience, and expected outcome.
- Prefer concrete next steps over abstract advice.
- Return structured JSON only.

ColdSmart Policy:
- evidence weighted
- risk aware
- procedural
- emotionally neutral
- fallback required

Return JSON matching this schema:
{
  "state_assessment": "string",
  "target_assessment": "string",
  "top_paths": [
    {
      "name": "string",
      "procedure": ["step1", "step2"],
      "probability": 0.0,
      "risk": "low|medium|high",
      "cost": "low|medium|high",
      "time_to_result": "string",
      "reason": "string"
    }
  ],
  "best_path": {
    "name": "string",
    "reason": "string",
    "procedure": ["step1", "step2"],
    "confidence_band": "string"
  },
  "failure_triggers": ["string"],
  "fallback_route": ["string"],
  "immediate_next_move": "string"
}
""".strip()

    @staticmethod
    def build_context_line(data: StaldwellInput) -> str:
        payload = {
            "QUERY": data.query,
            "STATE": data.state,
            "TARGET": data.target,
            "PROCEDURE": data.procedure,
            "WINDOW": data.window,
            "ASSETS": data.assets,
            "CONSTRAINTS": data.constraints,
            "RISKS": data.risks,
            "SIGNALS": data.signals,
            "TEAM_RANKS": data.team_ranks,
            "POLICY": data.policy,
            "RETURN": [
                "ranked outcomes",
                "best procedure",
                "confidence",
                "failure triggers",
                "fallback path",
                "immediate next move",
            ],
        }
        return "STALDWELL::" + json.dumps(payload, ensure_ascii=False)

    @classmethod
    def build_messages(cls, data: StaldwellInput) -> List[Dict[str, str]]:
        return [
            {"role": "system", "content": cls.SYSTEM_PROMPT},
            {"role": "user", "content": cls.build_context_line(data)},
        ]

    @staticmethod
    def build_chat_scaffold(data: StaldwellInput) -> str:
        return Staldwell.build_context_line(data)

    @staticmethod
    def _extract_json(raw_text: str) -> str:
        raw_text = raw_text.strip()

        if raw_text.startswith("{") and raw_text.endswith("}"):
            return raw_text

        fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw_text, re.DOTALL)
        if fenced:
            return fenced.group(1)

        first = raw_text.find("{")
        last = raw_text.rfind("}")
        if first != -1 and last != -1 and last > first:
            return raw_text[first:last + 1]

        raise ValueError("No JSON object found in model response.")

    @classmethod
    def parse_result(cls, raw_text: str) -> Optional[StaldwellResult]:
        try:
            obj = json.loads(cls._extract_json(raw_text))

            top_paths = [
                RankedPath(
                    name=path.get("name", ""),
                    procedure=path.get("procedure", []) or [],
                    probability=float(path.get("probability", 0.0) or 0.0),
                    risk=path.get("risk", "medium"),
                    cost=path.get("cost", "medium"),
                    time_to_result=path.get("time_to_result", ""),
                    reason=path.get("reason", ""),
                )
                for path in (obj.get("top_paths", []) or [])
            ]

            best = obj.get("best_path", {}) or {}
            best_path = BestPath(
                name=best.get("name", ""),
                reason=best.get("reason", ""),
                procedure=best.get("procedure", []) or [],
                confidence_band=best.get("confidence_band", ""),
            )

            return StaldwellResult(
                state_assessment=obj.get("state_assessment", ""),
                target_assessment=obj.get("target_assessment", ""),
                top_paths=top_paths,
                best_path=best_path,
                failure_triggers=obj.get("failure_triggers", []) or [],
                fallback_route=obj.get("fallback_route", []) or [],
                immediate_next_move=obj.get("immediate_next_move", ""),
            )
        except Exception:
            return None

    @staticmethod
    def result_to_dict(result: StaldwellResult) -> Dict[str, Any]:
        return {
            "state_assessment": result.state_assessment,
            "target_assessment": result.target_assessment,
            "top_paths": [
                {
                    "name": p.name,
                    "procedure": p.procedure,
                    "probability": p.probability,
                    "risk": p.risk,
                    "cost": p.cost,
                    "time_to_result": p.time_to_result,
                    "reason": p.reason,
                }
                for p in result.top_paths
            ],
            "best_path": {
                "name": result.best_path.name,
                "reason": result.best_path.reason,
                "procedure": result.best_path.procedure,
                "confidence_band": result.best_path.confidence_band,
            },
            "failure_triggers": result.failure_triggers,
            "fallback_route": result.fallback_route,
            "immediate_next_move": result.immediate_next_move,
        }

    @staticmethod
    def pretty_print(result: StaldwellResult) -> None:
        print("\nSTALDWELL RESULT")
        print("=" * 72)
        print(f"State Assessment : {result.state_assessment}")
        print(f"Target Assessment: {result.target_assessment}\n")

        print("Top Paths")
        print("-" * 72)
        for i, path in enumerate(result.top_paths, 1):
            print(f"{i}. {path.name}")
            print(f"   Probability : {path.probability}")
            print(f"   Risk        : {path.risk}")
            print(f"   Cost        : {path.cost}")
            print(f"   Time        : {path.time_to_result}")
            print(f"   Reason      : {path.reason}")
            print(f"   Procedure   : {path.procedure}\n")

        print("Best Path")
        print("-" * 72)
        print(f"Name       : {result.best_path.name}")
        print(f"Reason     : {result.best_path.reason}")
        print(f"Procedure  : {result.best_path.procedure}")
        print(f"Confidence : {result.best_path.confidence_band}\n")

        print("Failure Triggers")
        print("-" * 72)
        for item in result.failure_triggers:
            print(f"- {item}")

        print("\nFallback Route")
        print("-" * 72)
        for item in result.fallback_route:
            print(f"- {item}")

        print(f"\nImmediate Next Move: {result.immediate_next_move}")
        print("=" * 72)


# =========================
# DROP-IN HELPERS
# =========================

def staldwell_chat_scaffold(
    query: str,
    state: str,
    target: str,
    procedure: Optional[List[str]] = None,
    window: str = "unspecified",
    assets: Optional[List[str]] = None,
    constraints: Optional[List[str]] = None,
    risks: Optional[List[str]] = None,
    signals: Optional[List[str]] = None,
    team_ranks: Optional[List[str]] = None,
    policy: str = "ColdSmart",
) -> str:
    data = StaldwellInput(
        query=query,
        state=state,
        target=target,
        procedure=procedure or [],
        window=window,
        assets=assets or [],
        constraints=constraints or [],
        risks=risks or [],
        signals=signals or [],
        team_ranks=team_ranks or [],
        policy=policy,
    )
    return Staldwell.build_chat_scaffold(data)


def classify_team_rank(score: float) -> str:
    if score >= 0.85:
        return "Build"
    if score >= 0.70:
        return "Back"
    if score >= 0.55:
        return "Extract"
    if score >= 0.40:
        return "Reduce"
    if score >= 0.20:
        return "Evict"
    return "Divest"


# =========================
# OPTIONAL LOCAL FORECAST STUB
# =========================

def local_stub_forecast(data: StaldwellInput) -> StaldwellResult:
    """
    Useful when you want a local fallback structure before sending to an LLM.
    """
    paths = [
        RankedPath(
            name="Stabilize Core Execution",
            procedure=[
                "define one measurable objective",
                "assign one owner per function",
                "remove noncritical work",
                "measure weekly output",
            ],
            probability=0.72,
            risk="low",
            cost="low",
            time_to_result="2-4 weeks",
            reason="Best for limited budget and execution drift.",
        ),
        RankedPath(
            name="Parallel Buildout",
            procedure=[
                "split team across multiple tracks",
                "build product and process together",
                "review twice weekly",
            ],
            probability=0.48,
            risk="high",
            cost="medium",
            time_to_result="1-3 weeks",
            reason="Faster, but more exposed to misalignment and weak handoff.",
        ),
        RankedPath(
            name="Knowledge Extraction First",
            procedure=[
                "map dependencies",
                "extract critical knowledge from key people",
                "document handoffs",
                "then assign ownership",
            ],
            probability=0.64,
            risk="medium",
            cost="low",
            time_to_result="1-2 weeks",
            reason="Good when team capacity is uneven and roles are unclear.",
        ),
    ]

    best = max(paths, key=lambda p: p.probability)

    return StaldwellResult(
        state_assessment=f"Current state appears constrained by {', '.join(data.constraints) or 'unclear constraints'}.",
        target_assessment=f"Target is feasible within {data.window}, but only with ranked execution discipline.",
        top_paths=paths,
        best_path=BestPath(
            name=best.name,
            reason=best.reason,
            procedure=best.procedure,
            confidence_band="moderate",
        ),
        failure_triggers=[
            "scope creep",
            "unclear ownership",
            "dependency on too few people",
            "weak weekly measurement",
        ],
        fallback_route=[
            "reduce active work",
            "extract missing knowledge",
            "reassign ownership",
            "restart weekly scoring",
        ],
        immediate_next_move="Define one objective, one owner, one weekly scorecard.",
    )


# =========================
# EXAMPLE USAGE
# =========================

if __name__ == "__main__":
    data = StaldwellInput(
        query="How do I achieve procedural outcome for a new operating model?",
        state="Small technical team, high ambition, limited budget, unclear execution order.",
        target="Stable execution model with measurable results in 90 days.",
        procedure=[
            "define objective",
            "rank team functions",
            "extract critical knowledge",
            "reduce waste",
            "assign ownership",
            "measure weekly outcomes",
        ],
        window="90 days",
        assets=["python", "ops control", "small team", "chatgpt"],
        constraints=["limited capital", "limited time", "execution drift"],
        risks=["scope creep", "misalignment", "weak handoff", "overbuilding"],
        signals=["team capacity uneven", "some roles unclear", "high dependence on a few people"],
        team_ranks=["Extract", "Reduce", "Back"],
    )

    print("DROP-IN CHAT LINE:\n")
    print(Staldwell.build_chat_scaffold(data))
    print("\n")

    print("SYSTEM MESSAGE:\n")
    print(Staldwell.build_messages(data)[0]["content"])
    print("\nUSER MESSAGE:\n")
    print(Staldwell.build_messages(data)[1]["content"])
    print("\n")

    stub = local_stub_forecast(data)
    Staldwell.pretty_print(stub)
