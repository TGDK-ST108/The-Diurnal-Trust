from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import List, Dict, Any


# =========================
# VECTOR CORE
# =========================

@dataclass
class Vec3:
    x: float
    y: float
    z: float

    def __add__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> "Vec3":
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    __rmul__ = __mul__

    def __truediv__(self, scalar: float) -> "Vec3":
        if scalar == 0:
            return Vec3(0.0, 0.0, 0.0)
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)

    def magnitude(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normalized(self) -> "Vec3":
        mag = self.magnitude()
        if mag == 0:
            return Vec3(0.0, 0.0, 0.0)
        return self / mag

    def to_tuple(self):
        return (self.x, self.y, self.z)


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


# =========================
# CONFIG
# =========================

@dataclass
class LoopConfig:
    # Pyramid bounds
    base_half_width: float = 1.0
    height: float = 1.5

    # Figure-8 path scale
    loop_scale: float = 0.55

    # Valve lives outside the structure
    valve_pos: Vec3 = field(default_factory=lambda: Vec3(0.0, -1.15, 0.35))
    valve_gain: float = 1.35
    valve_sigma: float = 0.75

    # PMZ / control
    pmz_memory: float = 0.93
    pmz_gain: float = 0.60

    # Dynamics
    accel: float = 3.20
    drag: float = 0.90
    theta_rate: float = 1.80
    dt: float = 0.02
    steps: int = 3200

    # Resolver
    target_residual: float = 0.0102
    max_speed: float = 0.18


@dataclass
class LoopState:
    position: Vec3 = field(default_factory=lambda: Vec3(0.0, -0.40, 0.25))
    velocity: Vec3 = field(default_factory=lambda: Vec3(0.0, 0.0, 0.0))
    theta: float = 0.0
    pmz: float = 0.0
    enso: float = 0.0
    ratio_secondary: float = 1.0
    oxygen_flux: float = 0.0
    epoch: int = 0


# =========================
# GEOMETRY
# =========================

def pyramid_clip(p: Vec3, cfg: LoopConfig) -> Vec3:
    """
    Square pyramid clip:
    allowed X/Y shrinks linearly as Z approaches apex.
    """
    z = clamp(p.z, 0.0, cfg.height)
    allowed_xy = cfg.base_half_width * (1.0 - (z / cfg.height))
    allowed_xy = max(0.0, allowed_xy)

    x = clamp(p.x, -allowed_xy, allowed_xy)
    y = clamp(p.y, -allowed_xy, allowed_xy)
    return Vec3(x, y, z)


def pyramid_violation(p: Vec3, cfg: LoopConfig) -> float:
    clipped = pyramid_clip(p, cfg)
    delta = p - clipped
    return delta.magnitude()


def figure8_target(theta: float, cfg: LoopConfig) -> Vec3:
    """
    Figure-8 infinitizer inside a pyramid field.
    """
    x = cfg.loop_scale * math.sin(theta)
    y = 0.5 * cfg.loop_scale * math.sin(2.0 * theta)

    # Internal rise/fall inside the pyramid
    z = 0.18 * cfg.height + 0.48 * cfg.height * (1.0 - abs(math.sin(2.0 * theta)))

    return pyramid_clip(Vec3(x, y, z), cfg)


def enso_target(pos: Vec3, cfg: LoopConfig) -> Vec3:
    """
    Circular closure target: the paradox circumferential.
    """
    phi = math.atan2(pos.y, pos.x)
    r = cfg.loop_scale * 0.80
    return Vec3(
        r * math.cos(phi),
        r * math.sin(phi),
        0.33 * cfg.height
    )


def circumferential_vector(pos: Vec3) -> Vec3:
    """
    Tangential swirl around the center axis.
    """
    return Vec3(-pos.y, pos.x, 0.0).normalized()


def phase_index(theta: float) -> int:
    phase = int((theta % (2.0 * math.pi)) // (math.pi / 2.0))
    return max(0, min(3, phase))


def phase_name(index: int) -> str:
    return ["inhale", "rise", "paradox", "resolve"][index]


# =========================
# ENGINE
# =========================

class TrideotaxisQuaitrideotaxisPMZEngine:
    def __init__(self, cfg: LoopConfig):
        self.cfg = cfg
        self.state = LoopState()
        self.history: List[Dict[str, Any]] = []

    def oxygen_inflow(self, pos: Vec3, phase: int) -> float:
        """
        Symbolic oxygen flux from an external valve.
        This is a simulation signal, not hardware control.
        """
        valve_vec = self.cfg.valve_pos - pos
        dist = valve_vec.magnitude()

        # Strongest during inhale, weaker in later phases
        phase_gate = [1.00, 0.55, 0.20, 0.10][phase]

        flux = self.cfg.valve_gain * phase_gate * math.exp(
            -(dist * dist) / (2.0 * self.cfg.valve_sigma * self.cfg.valve_sigma)
        )
        return flux

    def control_vector(self, target: Vec3, target_next: Vec3, phase: int) -> Vec3:
        pos = self.state.position
        vel = self.state.velocity

        error_vec = target - pos
        tangent_vec = (target_next - target).normalized()
        apex_vec = (Vec3(0.0, 0.0, self.cfg.height) - pos).normalized()
        circle_vec = (enso_target(pos, self.cfg) - pos)
        swirl_vec = circumferential_vector(pos)
        valve_vec = (self.cfg.valve_pos - pos).normalized()

        oxygen_flux = self.state.oxygen_flux

        if phase == 0:  # inhale
            ctrl = (
                error_vec * 1.30 +
                tangent_vec * 0.45 +
                valve_vec * (1.15 * oxygen_flux)
            )
        elif phase == 1:  # rise
            ctrl = (
                error_vec * 0.90 +
                tangent_vec * 0.55 +
                apex_vec * 0.75
            )
        elif phase == 2:  # paradox
            ctrl = (
                error_vec * 0.40 +
                tangent_vec * 0.40 +
                swirl_vec * 1.25 +
                circle_vec.normalized() * 0.85
            )
        else:  # resolve
            ctrl = (
                circle_vec * 1.35 +
                error_vec * 0.75 -
                vel * 0.60
            )

        return ctrl

    def update_pmz(self, oxygen_flux: float) -> None:
        self.state.pmz = (
            self.cfg.pmz_memory * self.state.pmz +
            (1.0 - self.cfg.pmz_memory) * oxygen_flux
        )

    def step(self) -> None:
        cfg = self.cfg
        st = self.state

        phase = phase_index(st.theta)
        target = figure8_target(st.theta, cfg)
        target_next = figure8_target(st.theta + 0.05, cfg)

        oxygen_flux = self.oxygen_inflow(st.position, phase)
        st.oxygen_flux = oxygen_flux

        self.update_pmz(oxygen_flux)
        gain = 1.0 + (cfg.pmz_gain * st.pmz)

        ctrl = self.control_vector(target, target_next, phase)

        # Integrate velocity / position
        st.velocity = st.velocity * cfg.drag + ctrl * (cfg.accel * cfg.dt * gain)

        speed = st.velocity.magnitude()
        if speed > cfg.max_speed:
            st.velocity = st.velocity.normalized() * cfg.max_speed

        raw_pos = st.position + st.velocity
        wall_pressure = pyramid_violation(raw_pos, cfg)
        st.position = pyramid_clip(raw_pos, cfg)

        # Advance loop epoch
        st.theta += cfg.theta_rate * cfg.dt * gain

        # Resolver metrics
        tracking_error = (target - st.position).magnitude()
        circle_error = (enso_target(st.position, cfg) - st.position).magnitude()
        total_error = tracking_error + circle_error + (wall_pressure * 2.0)

        # Enso closure rises as the path becomes more circular / stable
        st.enso = 1.0 / (1.0 + total_error)

        # Converges toward 1:0.0102
        decay = math.exp(-0.002 * st.epoch)
        st.ratio_secondary = cfg.target_residual + decay * (
            tracking_error * 0.12 + circle_error * 0.08 + wall_pressure * 0.15
        )

        st.epoch += 1

        self.history.append({
            "epoch": st.epoch,
            "phase": phase_name(phase),
            "theta": st.theta,
            "x": st.position.x,
            "y": st.position.y,
            "z": st.position.z,
            "oxygen_flux": st.oxygen_flux,
            "pmz": st.pmz,
            "enso": st.enso,
            "ratio_primary": 1.0,
            "ratio_secondary": st.ratio_secondary,
            "tracking_error": tracking_error,
            "circle_error": circle_error,
            "wall_pressure": wall_pressure,
        })

    def run(self) -> List[Dict[str, Any]]:
        for _ in range(self.cfg.steps):
            self.step()
        return self.history

    def summary(self) -> str:
        if not self.history:
            return "Engine has not been run."

        final = self.history[-1]
        return (
            f"epoch={final['epoch']}\n"
            f"phase={final['phase']}\n"
            f"position=({final['x']:.4f}, {final['y']:.4f}, {final['z']:.4f})\n"
            f"oxygen_flux={final['oxygen_flux']:.6f}\n"
            f"pmz={final['pmz']:.6f}\n"
            f"enso={final['enso']:.6f}\n"
            f"resolution_ratio={final['ratio_primary']:.0f}:{final['ratio_secondary']:.4f}\n"
            f"tracking_error={final['tracking_error']:.6f}\n"
            f"circle_error={final['circle_error']:.6f}\n"
            f"wall_pressure={final['wall_pressure']:.6f}"
        )


# =========================
# OPTIONAL VISUALIZATION
# =========================

def plot_history(history: List[Dict[str, Any]]) -> None:
    try:
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    except ImportError:
        print("matplotlib is not installed. Run: pip install matplotlib")
        return

    xs = [h["x"] for h in history]
    ys = [h["y"] for h in history]
    zs = [h["z"] for h in history]

    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")

    ax.plot(xs, ys, zs, linewidth=1.2, label="Trideotaxis/PMZ Loop")
    ax.scatter([0], [0], [0], s=40, label="Base Center")
    ax.scatter([0], [-1.15], [0.35], s=60, label="External Valve")

    # Draw a simple pyramid wireframe
    b = 1.0
    h = 1.5
    base = [(-b, -b, 0), (b, -b, 0), (b, b, 0), (-b, b, 0), (-b, -b, 0)]
    apex = (0, 0, h)

    bx = [p[0] for p in base]
    by = [p[1] for p in base]
    bz = [p[2] for p in base]
    ax.plot(bx, by, bz, alpha=0.5)

    for corner in base[:-1]:
        ax.plot([corner[0], apex[0]], [corner[1], apex[1]], [corner[2], apex[2]], alpha=0.5)

    ax.set_title("Figure-8 Infinitizer in Pyramid Constraint")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.legend()
    plt.tight_layout()
    plt.show()


# =========================
# RUN
# =========================

if __name__ == "__main__":
    cfg = LoopConfig(
        base_half_width=1.0,
        height=1.5,
        loop_scale=0.55,
        target_residual=0.0102,
        steps=3200
    )

    engine = TrideotaxisQuaitrideotaxisPMZEngine(cfg)
    history = engine.run()

    print(engine.summary())

    # Uncomment to visualize
    # plot_history(history)
