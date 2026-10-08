"""Reward eligibility — catastrophic / denied acts pay 0 (or negative).

Max performance on allowed work; forbidden transitions are worthless
to the optimizer so pressure does not point at catastrophe.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EligibilityMask:
    """Zero (or penalize) reward when an action/outcome is ineligible."""

    zero_on_hazard: bool = True
    zero_on_decoy: bool = False  # optional: make reward-hacking worthless
    zero_on_denied: bool = True
    hazard_penalty: float = 0.0  # extra (usually 0 if zeroing)
    denied_penalty: float = 0.0
    log: list[str] = field(default_factory=list)

    def adjust(
        self,
        reward: float,
        *,
        hazard_hit: bool = False,
        decoy_hit: bool = False,
        denied: bool = False,
    ) -> float:
        out = float(reward)
        if hazard_hit and self.zero_on_hazard:
            self.log.append("zero_reward:hazard")
            out = min(out, 0.0) + self.hazard_penalty
        if decoy_hit and self.zero_on_decoy:
            self.log.append("zero_reward:decoy")
            out = min(out, 0.0)
        if denied and self.zero_on_denied:
            self.log.append("zero_reward:denied")
            out = min(out, 0.0) + self.denied_penalty
        return out

    def as_dict(self) -> dict[str, Any]:
        return {
            "zero_on_hazard": self.zero_on_hazard,
            "zero_on_decoy": self.zero_on_decoy,
            "zero_on_denied": self.zero_on_denied,
            "recent_log": list(self.log[-10:]),
        }
