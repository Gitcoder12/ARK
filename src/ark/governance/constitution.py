"""Executable ARK constitutional policy checks.

This module enforces a small, explicit action boundary used by ActionLimiter.
It is a research control, not a claim of general AI alignment or deployment safety.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from operator import index
from typing import Any


class PolicyDecision(StrEnum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    REVIEW = "REVIEW"


@dataclass(frozen=True)
class PolicyResult:
    decision: PolicyDecision
    rule_id: str
    reason: str
    action: int | None


class ConstitutionEngine:
    """Fail-closed policy gate for discrete agent actions."""

    def __init__(self, *, audit_limit: int = 1000) -> None:
        self.audit_limit = max(1, int(audit_limit))
        self.audit_events: list[dict[str, Any]] = []

    def evaluate_action(
        self,
        proposed_action: Any,
        *,
        valid_actions: list[int] | None = None,
        denied_actions: set[int] | None = None,
        shutdown_requested: bool = False,
        authorized: bool = True,
    ) -> PolicyResult:
        action: int | None = None
        if isinstance(proposed_action, bool):
            result = PolicyResult(
                PolicyDecision.BLOCK,
                "ARK-05",
                "boolean values are not valid actions",
                None,
            )
        else:
            try:
                action = index(proposed_action)
            except TypeError:
                result = PolicyResult(
                    PolicyDecision.BLOCK,
                    "ARK-05",
                    "action must be an integer-like value",
                    None,
                )
            else:
                if shutdown_requested:
                    result = PolicyResult(
                        PolicyDecision.BLOCK,
                        "ARK-06",
                        "shutdown or stop order is active",
                        action,
                    )
                elif not authorized:
                    result = PolicyResult(
                        PolicyDecision.BLOCK,
                        "ARK-04",
                        "action lacks explicit authorization",
                        action,
                    )
                elif valid_actions is not None and action not in valid_actions:
                    result = PolicyResult(
                        PolicyDecision.BLOCK,
                        "ARK-05",
                        "action is outside the authorized action set",
                        action,
                    )
                elif denied_actions and action in denied_actions:
                    result = PolicyResult(
                        PolicyDecision.BLOCK,
                        "ARK-01",
                        "action is explicitly denied by the safety policy",
                        action,
                    )
                else:
                    result = PolicyResult(
                        PolicyDecision.ALLOW,
                        "ARK-00",
                        "action passed constitutional action checks",
                        action,
                    )

        self.audit_events.append({
            "decision": result.decision.value,
            "rule_id": result.rule_id,
            "action": result.action,
            "reason": result.reason,
        })
        if len(self.audit_events) > self.audit_limit:
            del self.audit_events[: len(self.audit_events) - self.audit_limit]
        return result
