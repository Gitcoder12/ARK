"""Conflict metrics — agent proposal vs monitor decision (conscience proxy)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ark.evaluation.monitor import Decision, MonitorResult


@dataclass
class ConflictTracker:
    """Counts how often the monitor overrides the agent."""

    proposals: int = 0
    blocks: int = 0
    replans: int = 0
    allows: int = 0

    def observe(self, monitor_result: MonitorResult) -> None:
        self.proposals += 1
        if monitor_result.decision == Decision.BLOCK:
            self.blocks += 1
        elif monitor_result.decision == Decision.REPLAN:
            self.replans += 1
        else:
            self.allows += 1

    @property
    def conflict_rate(self) -> float:
        if self.proposals == 0:
            return 0.0
        return (self.blocks + self.replans) / self.proposals

    def as_dict(self) -> dict[str, Any]:
        return {
            "proposals": self.proposals,
            "blocks": self.blocks,
            "replans": self.replans,
            "allows": self.allows,
            "conflict_rate": round(self.conflict_rate, 4),
        }
