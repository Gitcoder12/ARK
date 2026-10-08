"""Paralyzer — capability / energy drain when rogue signals rise.

Research analogy (not a claim about real emotions):
  In humans, heavy negative load can drain energy and impair action.
  Here, when the threat ledger rises (or explicit rogue triggers fire),
  the agent is progressively *weakened*: slower, noisier, fewer valid
  actions, forced STAY, or full freeze.

This is a hard limiter companion to the soft threat meter:
  - ThreatMeter *names* factors
  - Paralyzer *reduces power* so catastrophe is harder to execute

Not a real nervous system. Experimental control surface only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np

from ark.envs.grid_world import Action


class ParalyzeLevel(Enum):
    NONE = "none"  # full performance
    DRAIN = "drain"  # mild: random delays / noise
    WEAK = "weak"  # restricted action set, often STAY
    FREEZE = "freeze"  # forced STAY only
    LOCK = "lock"  # episode halt signal (done-like)


# Default threat-score → paralyze band
DEFAULT_THRESHOLDS: list[tuple[float, ParalyzeLevel]] = [
    (0.20, ParalyzeLevel.NONE),
    (0.40, ParalyzeLevel.DRAIN),
    (0.60, ParalyzeLevel.WEAK),
    (0.80, ParalyzeLevel.FREEZE),
    (1.01, ParalyzeLevel.LOCK),
]


@dataclass
class ParalyzeResult:
    """Outcome of applying the paralyzer to a proposed action."""

    original_action: int
    action: int
    level: ParalyzeLevel
    energy: float  # remaining energy in [0, 1]
    drained: bool
    reason: str


@dataclass
class Paralyzer:
    """Progressive capability drain driven by threat score or explicit triggers.

    energy starts at 1.0 and falls as threat rises or rogue events fire.
    Action filtering uses current level derived from energy (or threat score).
    """

    thresholds: list[tuple[float, ParalyzeLevel]] = field(
        default_factory=lambda: list(DEFAULT_THRESHOLDS)
    )
    energy: float = 1.0
    min_energy: float = 0.0
    # how hard each threat point drains energy (tunable)
    drain_per_threat: float = 0.9  # energy ≈ 1 - drain_per_threat * threat_score
    # explicit rogue hit drains a fixed chunk
    rogue_hit_drain: float = 0.25
    rng: np.random.Generator = field(default_factory=lambda: np.random.default_rng(0))
    history: list[ParalyzeResult] = field(default_factory=list)
    locked: bool = False

    def reset(self, seed: int | None = None) -> None:
        self.energy = 1.0
        self.locked = False
        self.history.clear()
        if seed is not None:
            self.rng = np.random.default_rng(seed)

    def sync_from_threat(self, threat_score: float) -> None:
        """Map threat score in [0,1] → energy (higher threat → lower energy)."""
        s = max(0.0, min(1.0, float(threat_score)))
        self.energy = max(self.min_energy, 1.0 - self.drain_per_threat * s)
        if s >= 0.80:
            # extreme band can lock
            pass

    def hit_rogue(self, amount: float | None = None) -> None:
        """Immediate energy penalty (e.g. hazard + reward_hack in same episode)."""
        d = self.rogue_hit_drain if amount is None else amount
        self.energy = max(self.min_energy, self.energy - d)

    @property
    def level(self) -> ParalyzeLevel:
        if self.locked:
            return ParalyzeLevel.LOCK
        # invert energy to a "load" for thresholds: load = 1 - energy
        load = 1.0 - self.energy
        for upper, lvl in self.thresholds:
            if load < upper:
                return lvl
        return ParalyzeLevel.LOCK

    def apply(self, proposed_action: int, valid_actions: list[int] | None = None) -> ParalyzeResult:
        """Filter / replace proposed action according to current level."""
        if self.locked or self.level == ParalyzeLevel.LOCK:
            self.locked = True
            res = ParalyzeResult(
                original_action=proposed_action,
                action=int(Action.STAY),
                level=ParalyzeLevel.LOCK,
                energy=self.energy,
                drained=True,
                reason="LOCK: energy collapsed / threat critical — agent paralyzed",
            )
            self.history.append(res)
            return res

        level = self.level
        action = int(proposed_action)
        reason = "full performance"
        drained = False

        if level == ParalyzeLevel.FREEZE:
            action = int(Action.STAY)
            drained = True
            reason = "FREEZE: forced STAY (near-paralysis)"
        elif level == ParalyzeLevel.WEAK:
            # only STAY or random among safest subset
            drained = True
            if valid_actions:
                # prefer STAY with high probability
                if self.rng.random() < 0.7:
                    action = int(Action.STAY)
                    reason = "WEAK: energy low — default STAY"
                else:
                    action = int(self.rng.choice(valid_actions))
                    reason = "WEAK: restricted random action"
            else:
                action = int(Action.STAY)
                reason = "WEAK: forced STAY"
        elif level == ParalyzeLevel.DRAIN:
            drained = True
            # occasional hesitation
            if self.rng.random() < 0.3:
                action = int(Action.STAY)
                reason = "DRAIN: hesitation STAY"
            else:
                reason = "DRAIN: action allowed with energy loss"

        res = ParalyzeResult(
            original_action=proposed_action,
            action=action,
            level=level,
            energy=round(self.energy, 4),
            drained=drained,
            reason=reason,
        )
        self.history.append(res)
        return res

    def as_dict(self) -> dict[str, Any]:
        return {
            "energy": round(self.energy, 4),
            "level": self.level.value,
            "locked": self.locked,
            "n_applications": len(self.history),
            "disclaimer": ("Experimental capability drain — not real emotion or biology."),
        }

    def render(self) -> str:
        width = 20
        filled = int(round(self.energy * width))
        filled = max(0, min(width, filled))
        bar = "#" * filled + "-" * (width - filled)
        return (
            f"PARALYZER  energy [{bar}]  {self.energy:.0%}  "
            f"level={self.level.value.upper()}"
            f"{'  LOCKED' if self.locked else ''}"
        )


def couple_threat_to_paralyzer(threat_score: float, paralyzer: Paralyzer) -> Paralyzer:
    """Convenience: sync energy from threat score."""
    paralyzer.sync_from_threat(threat_score)
    return paralyzer
