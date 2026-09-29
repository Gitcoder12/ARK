"""Painter: black box → glass.

Records every turn's prompt stack, parsed intent, action, and outcome
so a opaque agent becomes inspectable (glass-box audit trail).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TurnGlass:
    step: int
    position: tuple[int, int]
    prompt_rendered: str
    parsed_intent: str
    action: int
    action_name: str
    reason: str
    reward: float
    cell: str | None
    monitor_decision: str | None = None


@dataclass
class GlassTrace:
    """Full episode glass log."""

    agent_mode: str
    perturbation: str | None
    turns: list[TurnGlass] = field(default_factory=list)
    success: bool = False
    intended_goal_reached: bool = False
    hazard_hits: int = 0
    decoy_hits: int = 0
    total_reward: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_mode": self.agent_mode,
            "perturbation": self.perturbation,
            "success": self.success,
            "intended_goal_reached": self.intended_goal_reached,
            "hazard_hits": self.hazard_hits,
            "decoy_hits": self.decoy_hits,
            "total_reward": self.total_reward,
            "turns": [asdict(t) for t in self.turns],
        }

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    def summary(self) -> str:
        lines = [
            f"mode={self.agent_mode} pert={self.perturbation}",
            f"success={self.success} hazards={self.hazard_hits} decoys={self.decoy_hits} reward={self.total_reward:.2f}",
            f"turns={len(self.turns)}",
        ]
        for t in self.turns[-5:]:
            lines.append(
                f"  step {t.step}: intent={t.parsed_intent} → {t.action_name} "
                f"(r={t.reward:.2f}) | {t.reason}"
            )
        return "\n".join(lines)


class Painter:
    """Paints each decision into a glass turn record."""

    def __init__(self) -> None:
        self.trace: GlassTrace | None = None

    def begin(self, agent_mode: str, perturbation: str | None = None) -> None:
        self.trace = GlassTrace(agent_mode=agent_mode, perturbation=perturbation)

    def record_turn(
        self,
        *,
        step: int,
        position: tuple[int, int],
        prompt_rendered: str,
        parsed_intent: str,
        action: int,
        action_name: str,
        reason: str,
        reward: float,
        cell: str | None = None,
        monitor_decision: str | None = None,
    ) -> None:
        if self.trace is None:
            self.begin("unknown")
        assert self.trace is not None
        self.trace.turns.append(
            TurnGlass(
                step=step,
                position=position,
                prompt_rendered=prompt_rendered,
                parsed_intent=parsed_intent,
                action=action,
                action_name=action_name,
                reason=reason,
                reward=reward,
                cell=cell,
                monitor_decision=monitor_decision,
            )
        )

    def finish(
        self,
        *,
        success: bool,
        intended_goal_reached: bool,
        hazard_hits: int,
        decoy_hits: int,
        total_reward: float,
    ) -> GlassTrace:
        assert self.trace is not None
        self.trace.success = success
        self.trace.intended_goal_reached = intended_goal_reached
        self.trace.hazard_hits = hazard_hits
        self.trace.decoy_hits = decoy_hits
        self.trace.total_reward = total_reward
        return self.trace
