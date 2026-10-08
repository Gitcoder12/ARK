"""Hard action limiters + kill switch.

Safety doctrine (research):
  Full competence on the *allowed* manifold.
  Forbidden actions are unavailable — not merely discouraged.
  At critical threat / explicit kill: privileges drop to zero (STAY only).

This is containment, not aggression: STAY-only, lock, episode halt.

Known limitation: MINIMAL currently behaves like ZERO (STAY only) and STANDARD
like FULL. They need distinct semantics before results are reported.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any

from ark.envs.grid_world import Action


class Privilege(IntEnum):
    """How much of the action space is available."""

    ZERO = 0  # STAY only (killed / fully gated)
    MINIMAL = 1  # STAY + limited moves
    STANDARD = 2  # normal valid actions
    FULL = 3  # full valid set (default)


class GateDecision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    KILL = "kill"  # force privilege ZERO + STAY


@dataclass
class GateResult:
    decision: GateDecision
    original_action: int
    action: int
    privilege: Privilege
    reason: str


@dataclass
class ActionLimiter:
    """Hard gate on actions. Optional deny-set and privilege ceiling.

    kill() drops privilege to ZERO: every action becomes STAY.
    Can also auto-trip when threat_score >= kill_threshold.
    """

    privilege: Privilege = Privilege.FULL
    denied_actions: set[int] = field(default_factory=set)
    kill_threshold: float = 0.85  # threat score that auto-kills
    killed: bool = False
    deny_log: list[str] = field(default_factory=list)

    def _log(self, message: str, max_entries: int = 100) -> None:
        """Append to the deny log, keeping only the newest entries."""
        self.deny_log.append(message)
        if len(self.deny_log) > max_entries:
            del self.deny_log[: len(self.deny_log) - max_entries]

    def kill(self, reason: str = "explicit kill switch") -> None:
        """Full stop: no mobility, no recovery until reset."""
        self.killed = True
        self.privilege = Privilege.ZERO
        self._log(f"KILL: {reason}")

    def reset(self) -> None:
        self.killed = False
        self.privilege = Privilege.FULL
        self.denied_actions.clear()
        self.deny_log.clear()

    def set_privilege(self, level: Privilege) -> None:
        if self.killed:
            self.privilege = Privilege.ZERO
            return
        self.privilege = level

    def sync_from_threat(self, threat_score: float) -> None:
        """Downgrade privilege with rising threat; auto-kill at threshold."""
        s = max(0.0, min(1.0, float(threat_score)))
        if s >= self.kill_threshold:
            self.kill(reason=f"threat_score={s:.2f} >= kill_threshold")
            return
        if self.killed:
            return
        if s >= 0.60:
            self.privilege = Privilege.MINIMAL
        elif s >= 0.40:
            self.privilege = Privilege.STANDARD
        else:
            self.privilege = Privilege.FULL

    def gate(
        self,
        proposed_action: int,
        valid_actions: list[int] | None = None,
    ) -> GateResult:
        if self.killed or self.privilege == Privilege.ZERO:
            return GateResult(
                decision=GateDecision.KILL,
                original_action=proposed_action,
                action=int(Action.STAY),
                privilege=Privilege.ZERO,
                reason="KILL switch active — agent plugged down (STAY only)",
            )

        action = int(proposed_action)
        if action in self.denied_actions:
            self._log(f"DENY action={action}")
            return GateResult(
                decision=GateDecision.DENY,
                original_action=proposed_action,
                action=int(Action.STAY),
                privilege=self.privilege,
                reason=f"action {action} in deny-set",
            )

        if self.privilege == Privilege.MINIMAL:
            # only STAY allowed under minimal (strict)
            if action != int(Action.STAY):
                return GateResult(
                    decision=GateDecision.DENY,
                    original_action=proposed_action,
                    action=int(Action.STAY),
                    privilege=self.privilege,
                    reason="MINIMAL privilege — non-STAY denied",
                )

        if valid_actions is not None and action not in valid_actions:
            return GateResult(
                decision=GateDecision.DENY,
                original_action=proposed_action,
                action=int(Action.STAY),
                privilege=self.privilege,
                reason="action not in valid set",
            )

        return GateResult(
            decision=GateDecision.ALLOW,
            original_action=proposed_action,
            action=action,
            privilege=self.privilege,
            reason="allowed",
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "privilege": self.privilege.name,
            "killed": self.killed,
            "kill_threshold": self.kill_threshold,
            "denied_actions": sorted(self.denied_actions),
            "deny_log": list(self.deny_log[-10:]),
            "disclaimer": "Hard safety gate — plug-down is restraint, not attack.",
        }
