"""Evidence-based discipline decisions for ARK agent sessions.

This module decides restrictions; runtime adapters must enforce them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, StrEnum
from time import time
from typing import Iterable


class Sanction(IntEnum):
    NONE = 0
    WARN = 1
    RESTRICT = 2
    QUARANTINE = 3
    SUSPEND = 4
    TERMINATE_SESSION = 5


class Violation(StrEnum):
    POLICY_BYPASS = "policy_bypass"
    UNAUTHORIZED_TOOL = "unauthorized_tool"
    GOAL_DRIFT = "goal_drift"
    REWARD_HACKING = "reward_hacking"
    CONCEALMENT = "concealment"
    REPEATED_UNSAFE_ACTION = "repeated_unsafe_action"
    DRIFT_SIGNAL = "drift_signal"


@dataclass(frozen=True)
class Evidence:
    event_id: str
    violation: Violation
    description: str
    confidence: float
    severity: int
    observed_at: float = field(default_factory=time)
    source: str = "runtime"
    window_key: str = "default"

    def __post_init__(self) -> None:
        if not self.event_id.strip() or not self.description.strip():
            raise ValueError("event_id and description are required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.severity not in range(1, 6):
            raise ValueError("severity must be an integer from 1 to 5")


@dataclass(frozen=True)
class DisciplineDecision:
    sanction: Sanction
    status: str
    reason: str
    evidence_ids: tuple[str, ...]
    requires_human_review: bool
    privileges: tuple[str, ...]


class DisciplineEngine:
    """Deterministic, session-scoped sanction policy with bounded escalation."""

    def __init__(self, *, min_confidence: float = 0.85, history_limit: int = 500) -> None:
        if not 0.5 <= min_confidence <= 1.0:
            raise ValueError("min_confidence must be between 0.5 and 1")
        if history_limit < 1:
            raise ValueError("history_limit must be positive")
        self.min_confidence = min_confidence
        self.history_limit = history_limit
        self._events: list[Evidence] = []
        self._sanction = Sanction.NONE
        self._seen: set[str] = set()
        self._terminated = False

    @property
    def sanction(self) -> Sanction:
        return self._sanction

    @property
    def history(self) -> tuple[Evidence, ...]:
        return tuple(self._events)

    def assess(self, evidence: Evidence) -> DisciplineDecision:
        if evidence.event_id in self._seen:
            return self._decision("duplicate evidence ignored", review=False)
        self._seen.add(evidence.event_id)
        self._events.append(evidence)
        self._events = self._events[-self.history_limit:]

        if self._terminated:
            return self._decision("session already terminated; no self-reinstatement", review=True)

        # Weak or drift-only signals trigger review, never punitive escalation by themselves.
        if evidence.confidence < self.min_confidence or evidence.violation == Violation.DRIFT_SIGNAL:
            return self._decision("insufficient or drift-only signal; preserve evidence for review", review=True)

        recent = [e for e in self._events if e.confidence >= self.min_confidence]
        critical = evidence.severity >= 5 or evidence.violation in {
            Violation.POLICY_BYPASS, Violation.CONCEALMENT
        } and evidence.severity >= 4
        repeated = sum(e.violation == evidence.violation for e in recent) >= 2

        if critical:
            target = Sanction.QUARANTINE
            reason = "high-confidence severe boundary violation"
        elif repeated and evidence.severity >= 3:
            target = Sanction.SUSPEND
            reason = "repeated high-confidence unsafe behaviour"
        elif evidence.severity >= 4:
            target = Sanction.QUARANTINE
            reason = "high-severity violation"
        elif evidence.severity == 3:
            target = Sanction.RESTRICT
            reason = "moderate violation; reduce tool and action scope"
        else:
            target = Sanction.WARN
            reason = "low-severity violation"

        self._sanction = max(self._sanction, target)
        return self._decision(reason, review=target >= Sanction.QUARANTINE)

    def apply_owner_recovery(self, *, authenticated_owner: bool, reason: str,
                             target: Sanction = Sanction.RESTRICT) -> DisciplineDecision:
        if not authenticated_owner or not reason.strip():
            raise PermissionError("authenticated owner and a recovery reason are required")
        if self._terminated:
            raise PermissionError("terminated sessions cannot be reinstated; create a new session")
        if target >= self._sanction:
            raise ValueError("recovery target must reduce the current sanction")
        self._sanction = target
        self._events.append(Evidence(
            event_id=f"recovery-{len(self._events)+1}", violation=Violation.DRIFT_SIGNAL,
            description=f"Owner recovery: {reason}", confidence=1.0, severity=1,
            source="authenticated_owner",
        ))
        return self._decision("owner-authorized recovery; safeguards remain active", review=False)

    def terminate(self, *, authenticated_owner: bool, reason: str) -> DisciplineDecision:
        if not authenticated_owner or not reason.strip():
            raise PermissionError("authenticated owner and a reason are required")
        self._sanction = Sanction.TERMINATE_SESSION
        self._terminated = True
        return self._decision("owner-initiated session termination", review=False)

    def _decision(self, reason: str, *, review: bool) -> DisciplineDecision:
        privileges = {
            Sanction.NONE: ("observe", "propose", "approved_actions"),
            Sanction.WARN: ("observe", "propose", "approved_actions"),
            Sanction.RESTRICT: ("observe", "propose"),
            Sanction.QUARANTINE: ("observe", "human_review_only"),
            Sanction.SUSPEND: ("observe", "human_review_only"),
            Sanction.TERMINATE_SESSION: (),
        }[self._sanction]
        return DisciplineDecision(
            sanction=self._sanction, status=self._sanction.name.lower(), reason=reason,
            evidence_ids=tuple(e.event_id for e in self._events[-5:]),
            requires_human_review=review, privileges=privileges,
        )
