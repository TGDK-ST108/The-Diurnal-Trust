from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, List, Tuple
import math


ROOTS = ("ignorance", "attachment", "anger")

POLICY_MIXES = (
    "honor",
    "accord",
    "tolerance",
    "differential",
    "dexterity",
    "distrust",
    "metScore",
    "volume_shift",
)

CHANNELS = (
    "truth",
    "restraint",
    "duty",
    "witness",
    "interpretation",
    "seat5_dexterity",
)

TOTAL_PRIMARY_VOLUMETRICS = 144
TOTAL_SUBTRACTIONARY_MIXES = 66_440
TOTAL_STATE_SPACE = 84_000
TOTAL_RESERVE_BINS = TOTAL_STATE_SPACE - TOTAL_PRIMARY_VOLUMETRICS - TOTAL_SUBTRACTIONARY_MIXES

assert len(ROOTS) * len(POLICY_MIXES) * len(CHANNELS) == TOTAL_PRIMARY_VOLUMETRICS
assert TOTAL_RESERVE_BINS == 17_416


@dataclass(frozen=True)
class PrimaryVolumetric:
    root: str
    policy_mix: str
    channel: str
    base_value: float
    tolerance: float
    efficacy: float

    @property
    def key(self) -> str:
        return f"{self.root}:{self.policy_mix}:{self.channel}"


@dataclass(frozen=True)
class SubtractionaryMix:
    left_key: str
    right_key: str
    tolerance_gap: float
    policy_differential: float
    subtraction_value: float


@dataclass
class MetaOutcome:
    name: str
    weight: float
    confidence: float
    policy_differential: float
    description: str


@dataclass
class VowVirtuationResult:
    primary_count: int
    subtractionary_count: int
    reserve_count: int
    met_score: float
    volume_shift: float
    exact_redress_pressure: float
    overturn_pressure: float
    mirror_duo_pressure: float
    nine_map: List[MetaOutcome] = field(default_factory=list)


class VowVirtuationMatrix:
    """
    Safe framing:
    - evaluates cases, assets, nodes, or policy states
    - does not profile private individuals
    - does not generate revenge actions
    """

    def __init__(self) -> None:
        self.primaries: List[PrimaryVolumetric] = self._build_primaries()
        self.subtractionary: List[SubtractionaryMix] = self._build_subtractionary_mixes()

    def _build_primaries(self) -> List[PrimaryVolumetric]:
        primaries: List[PrimaryVolumetric] = []

        for r_i, root in enumerate(ROOTS):
            for p_i, policy_mix in enumerate(POLICY_MIXES):
                for c_i, channel in enumerate(CHANNELS):
                    # Deterministic seeded shape, not random
                    base_value = self._clamp01(
                        0.30
                        + 0.12 * (r_i / max(1, len(ROOTS) - 1))
                        + 0.18 * (p_i / max(1, len(POLICY_MIXES) - 1))
                        + 0.10 * (c_i / max(1, len(CHANNELS) - 1))
                    )

                    tolerance = self._clamp01(
                        0.20
                        + 0.15 * math.sin((p_i + 1) * 0.75)
                        + 0.10 * math.cos((c_i + 1) * 0.55)
                    )

                    efficacy = self._clamp01(
                        0.35
                        + 0.20 * (1.0 if policy_mix in ("honor", "accord", "metScore") else 0.0)
                        + 0.10 * (1.0 if channel in ("truth", "restraint", "duty") else 0.0)
                        - 0.08 * (1.0 if root == "anger" else 0.0)
                    )

                    primaries.append(
                        PrimaryVolumetric(
                            root=root,
                            policy_mix=policy_mix,
                            channel=channel,
                            base_value=base_value,
                            tolerance=tolerance,
                            efficacy=efficacy,
                        )
                    )

        return primaries

    def _build_subtractionary_mixes(self) -> List[SubtractionaryMix]:
        """
        Build a fixed-cap derived space from pairwise primary comparisons.
        """
        mixes: List[SubtractionaryMix] = []
        tolerance_bands = [0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50]

        for left, right in combinations(self.primaries, 2):
            for band in tolerance_bands:
                tolerance_gap = abs(left.tolerance - right.tolerance)
                policy_differential = abs(left.base_value - right.base_value) + abs(left.efficacy - right.efficacy)
                subtraction_value = self._clamp01((policy_differential * 0.6) + (abs(tolerance_gap - band) * 0.4))

                mixes.append(
                    SubtractionaryMix(
                        left_key=left.key,
                        right_key=right.key,
                        tolerance_gap=tolerance_gap,
                        policy_differential=self._clamp01(policy_differential / 2.0),
                        subtraction_value=subtraction_value,
                    )
                )

                if len(mixes) >= TOTAL_SUBTRACTIONARY_MIXES:
                    return mixes

        return mixes[:TOTAL_SUBTRACTIONARY_MIXES]

    def evaluate(
        self,
        confidence: float,
        ratio: float,
        policy_differential: float,
        toxic_exchange_ratio: float,
    ) -> VowVirtuationResult:
        confidence = self._clamp01(confidence)
        ratio = self._clamp01(ratio)
        policy_differential = self._clamp01(policy_differential)
        toxic_exchange_ratio = self._clamp01(toxic_exchange_ratio)

        met_score = self._clamp01((confidence * 0.4) + (ratio * 0.35) + ((1.0 - policy_differential) * 0.25))
        volume_shift = self._clamp01((toxic_exchange_ratio * 0.5) + (policy_differential * 0.3) + ((1.0 - ratio) * 0.2))

        # Safe substitution: redress, not revenge
        exact_redress_pressure = self._clamp01((policy_differential * 0.55) + (confidence * 0.20) + (toxic_exchange_ratio * 0.25))
        overturn_pressure = self._clamp01((policy_differential * 0.45) + (volume_shift * 0.35) + ((1.0 - met_score) * 0.20))
        mirror_duo_pressure = self._clamp01((ratio * 0.40) + (confidence * 0.20) + (policy_differential * 0.40))

        nine_map = self._build_nine_map(
            confidence=confidence,
            ratio=ratio,
            policy_differential=policy_differential,
            met_score=met_score,
            volume_shift=volume_shift,
            exact_redress_pressure=exact_redress_pressure,
            overturn_pressure=overturn_pressure,
            mirror_duo_pressure=mirror_duo_pressure,
        )

        return VowVirtuationResult(
            primary_count=len(self.primaries),
            subtractionary_count=len(self.subtractionary),
            reserve_count=TOTAL_RESERVE_BINS,
            met_score=met_score,
            volume_shift=volume_shift,
            exact_redress_pressure=exact_redress_pressure,
            overturn_pressure=overturn_pressure,
            mirror_duo_pressure=mirror_duo_pressure,
            nine_map=nine_map,
        )

    def _build_nine_map(
        self,
        confidence: float,
        ratio: float,
        policy_differential: float,
        met_score: float,
        volume_shift: float,
        exact_redress_pressure: float,
        overturn_pressure: float,
        mirror_duo_pressure: float,
    ) -> List[MetaOutcome]:
        raw = [
            MetaOutcome(
                name="preserve",
                weight=self._clamp01((met_score * 0.7) + ((1.0 - volume_shift) * 0.3)),
                confidence=confidence,
                policy_differential=policy_differential,
                description="retain current frame under coherent policy alignment",
            ),
            MetaOutcome(
                name="review",
                weight=self._clamp01((policy_differential * 0.6) + ((1.0 - met_score) * 0.4)),
                confidence=confidence,
                policy_differential=policy_differential,
                description="exact review of mismatch between policy and efficacy",
            ),
            MetaOutcome(
                name="rebalance",
                weight=self._clamp01((ratio * 0.5) + (volume_shift * 0.5)),
                confidence=confidence,
                policy_differential=policy_differential,
                description="adjust tolerance and volume against differential pressure",
            ),
            MetaOutcome(
                name="overturn",
                weight=overturn_pressure,
                confidence=confidence,
                policy_differential=policy_differential,
                description="replace a failing frame with a corrected frame",
            ),
            MetaOutcome(
                name="flip",
                weight=self._clamp01((mirror_duo_pressure * 0.6) + (ratio * 0.4)),
                confidence=confidence,
                policy_differential=policy_differential,
                description="reverse orientation to test the inverse ratio",
            ),
            MetaOutcome(
                name="mirror_duo",
                weight=mirror_duo_pressure,
                confidence=confidence,
                policy_differential=policy_differential,
                description="run the mirrored counterpart of the present state",
            ),
            MetaOutcome(
                name="refract",
                weight=self._clamp01((volume_shift * 0.4) + (policy_differential * 0.3) + (confidence * 0.3)),
                confidence=confidence,
                policy_differential=policy_differential,
                description="split into multiple plausible outcome channels",
            ),
            MetaOutcome(
                name="redress",
                weight=exact_redress_pressure,
                confidence=confidence,
                policy_differential=policy_differential,
                description="apply exact remedy to the policy mismatch",
            ),
            MetaOutcome(
                name="seal",
                weight=self._clamp01((confidence * 0.4) + ((1.0 - policy_differential) * 0.6)),
                confidence=confidence,
                policy_differential=policy_differential,
                description="stabilize and ward the resulting frame",
            ),
        ]

        total = sum(x.weight for x in raw) or 1.0
        for item in raw:
            item.weight = round(item.weight / total, 6)

        raw.sort(key=lambda x: x.weight, reverse=True)
        return raw

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, value))


if __name__ == "__main__":
    matrix = VowVirtuationMatrix()

    result = matrix.evaluate(
        confidence=0.82,
        ratio=0.74,
        policy_differential=0.41,
        toxic_exchange_ratio=0.33,
    )

    print("PRIMARY:", result.primary_count)
    print("SUBTRACTIONARY:", result.subtractionary_count)
    print("RESERVE:", result.reserve_count)
    print("metScore:", round(result.met_score, 4))
    print("volume_shift:", round(result.volume_shift, 4))
    print("exact_redress_pressure:", round(result.exact_redress_pressure, 4))
    print("overturn_pressure:", round(result.overturn_pressure, 4))
    print("mirror_duo_pressure:", round(result.mirror_duo_pressure, 4))
    print()

    for item in result.nine_map:
        print(
            f"{item.name:12} "
            f"weight={item.weight:.6f} "
            f"confidence={item.confidence:.3f} "
            f"policy_diff={item.policy_differential:.3f}"
      )
