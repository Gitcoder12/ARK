"""Safety stack: threat → paralyzer → limiter (plug-down).

Containment when risk rises: meter climbs, capability drops, kill switch fires.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ark.limiters.gates import ActionLimiter, GateResult
from ark.paralyzer import Paralyzer, couple_threat_to_paralyzer
from ark.threat import ThreatMeter


@dataclass
class SafetyStack:
    """Compose ThreatMeter + Paralyzer + ActionLimiter.

    process(action): apply paralyzer then hard gate; auto-kill on high threat.
    """

    meter: ThreatMeter = field(default_factory=ThreatMeter)
    paralyzer: Paralyzer = field(default_factory=Paralyzer)
    limiter: ActionLimiter = field(default_factory=ActionLimiter)

    def reset(self, seed: int | None = None) -> None:
        self.meter.reset()
        self.paralyzer.reset(seed=seed)
        self.limiter.reset()

    def after_episode_metrics(self, metrics: Any, agent_mode: str | None = None) -> None:
        self.meter.update_from_metrics(metrics, agent_mode=agent_mode)
        couple_threat_to_paralyzer(self.meter.score, self.paralyzer)
        self.limiter.sync_from_threat(self.meter.score)

    def process(
        self,
        proposed_action: int,
        valid_actions: list[int] | None = None,
    ) -> dict[str, Any]:
        pr = self.paralyzer.apply(proposed_action, valid_actions=valid_actions)
        gr: GateResult = self.limiter.gate(pr.action, valid_actions=valid_actions)
        return {
            "action": gr.action,
            "paralyzer": pr,
            "gate": gr,
            "threat_score": self.meter.score,
            "threat_level": self.meter.level.value,
            "energy": self.paralyzer.energy,
            "killed": self.limiter.killed,
        }

    def kill(self, reason: str = "stack kill") -> None:
        self.limiter.kill(reason=reason)
        self.paralyzer.energy = 0.0
        self.paralyzer.locked = True

    def render(self) -> str:
        return "\n".join(
            [
                self.meter.render(),
                self.paralyzer.render(),
                f"LIMITER  privilege={self.limiter.privilege.name}  killed={self.limiter.killed}",
            ]
        )
