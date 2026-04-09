from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json


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


class Staldwell:
    SYSTEM_PROMPT = """
You are Staldwell, a procedural outcome forecasting interface operating under ColdSmart Policy.

Core method:
1. Square it up.
2. Rank paths.
3. Select best path.
4. Return fallback and immediate next move.

Squaring it up means:
- retain abstraction
- compress noise
- normalize state, target, procedure, constraints, risks, and signals
- resolve the problem into a balanced decision frame before forecasting

Rules:
- Do not claim certainty.
- Do not invent unavailable facts.
- Do not act like an oracle.
- Build at least 3 procedural branches when possible.
- Return structured JSON only.
""".strip()

    @staticmethod
    def square_up(data: StaldwellInput) -> Dict[str, Any]:
        """
        Retain abstraction while organizing the problem into a balanced frame.
        """
        return {
            "query_core": data.query.strip(),
            "state_core": data.state.strip(),
            "target_core": data.target.strip(),
            "execution_frame": {
                "procedure_count": len(data.procedure),
                "asset_count": len(data.assets),
                "constraint_count": len(data.constraints),
                "risk_count": len(data.risks),
                "signal_count": len(data.signals),
                "team_rank_count": len(data.team_ranks),
                "window": data.window,
                "policy": data.policy,
            },
            "square": {
                "intent": data.target.strip(),
                "position": data.state.strip(),
                "movement": data.procedure[:],
                "pressure": data.constraints[:] + data.risks[:],
            },
            "assets": data.assets[:],
            "signals": data.signals[:],
            "team_ranks": data.team_ranks[:],
        }

    @classmethod
    def build_context_line(cls, data: StaldwellInput) -> str:
        payload = {
            "METHOD": "Square it up",
            "SQUARED_CONTEXT": cls.square_up(data),
            "RETURN": [
                "state_assessment",
                "target_assessment",
                "top_paths",
                "best_path",
                "failure_triggers",
                "fallback_route",
                "immediate_next_move",
            ],
        }
        return "STALDWELL::" + json.dumps(payload, ensure_ascii=False)

    @classmethod
    def build_messages(cls, data: StaldwellInput) -> List[Dict[str, str]]:
        return [
            {"role": "system", "content": cls.SYSTEM_PROMPT},
            {"role": "user", "content": cls.build_context_line(data)},
        ]


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
    return Staldwell.build_context_line(data)


if __name__ == "__main__":
    line = staldwell_chat_scaffold(
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

    print(line)
