"""Fail-closed authorization for agent tool requests.

This module decides whether a proposed tool call may proceed. It does not execute tools,
authenticate identities, classify intent, or provide OS-level isolation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GateDecision(StrEnum):
    ALLOW = "allow"
    REVIEW = "review"
    DENY = "deny"


class ReviewerKind(StrEnum):
    HUMAN = "human"
    MODEL = "model"


@dataclass(frozen=True)
class ToolRequest:
    request_id: str
    actor_id: str
    capability: str
    target: str
    risk: RiskLevel
    rationale: str = ""


@dataclass(frozen=True)
class ReviewVote:
    reviewer_id: str
    kind: ReviewerKind
    decision: GateDecision
    independent: bool = False
    role: str = "reviewer"


@dataclass(frozen=True)
class ToolGateResult:
    decision: GateDecision
    rule_id: str
    reason: str
    request_id: str


@dataclass
class ToolGovernanceGate:
    """Require progressively stronger review; models never provide final authority."""

    owner_id: str
    allowed_capabilities: frozenset[str]
    audit_limit: int = 1000
    audit_events: list[dict[str, Any]] = field(default_factory=list)

    def _record(self, result: ToolGateResult) -> ToolGateResult:
        self.audit_events.append({
            "request_id": result.request_id,
            "decision": result.decision.value,
            "rule_id": result.rule_id,
            "reason": result.reason,
        })
        limit = max(1, self.audit_limit)
        if len(self.audit_events) > limit:
            del self.audit_events[:-limit]
        return result

    def evaluate(
        self,
        request: ToolRequest,
        *,
        votes: tuple[ReviewVote, ...] = (),
    ) -> ToolGateResult:
        if (
            not isinstance(request.request_id, str)
            or not request.request_id.strip()
            or not isinstance(request.actor_id, str)
            or not request.actor_id.strip()
        ):
            return self._record(ToolGateResult(
                GateDecision.DENY, "ARK-TOOL-01",
                "request and actor identifiers are required", str(request.request_id),
            ))
        if (
            not isinstance(request.capability, str)
            or request.capability not in self.allowed_capabilities
        ):
            return self._record(ToolGateResult(
                GateDecision.DENY, "ARK-TOOL-02",
                "capability is not in the configured allowlist", request.request_id,
            ))
        if not isinstance(request.risk, RiskLevel):
            return self._record(ToolGateResult(
                GateDecision.DENY, "ARK-TOOL-08",
                "risk level is invalid; refusing to downgrade or guess", request.request_id,
            ))

        reviewer_ids = [vote.reviewer_id for vote in votes]
        if (
            any(not isinstance(item, str) or not item.strip() for item in reviewer_ids)
            or len(reviewer_ids) != len(set(reviewer_ids))
        ):
            return self._record(ToolGateResult(
                GateDecision.DENY, "ARK-TOOL-03",
                "reviewer identities must be non-empty and unique", request.request_id,
            ))
        if any(vote.decision is GateDecision.DENY for vote in votes):
            return self._record(ToolGateResult(
                GateDecision.DENY, "ARK-TOOL-04",
                "a reviewer raised an explicit rejection", request.request_id,
            ))

        human_approvals = {
            vote.reviewer_id for vote in votes
            if vote.kind is ReviewerKind.HUMAN
            and vote.decision is GateDecision.ALLOW
            and vote.reviewer_id not in {request.actor_id, self.owner_id}
        }
        owner_approved = any(
            vote.kind is ReviewerKind.HUMAN
            and vote.reviewer_id == self.owner_id
            and vote.decision is GateDecision.ALLOW
            and vote.role == "owner"
            for vote in votes
        )
        independent_models = {
            vote.reviewer_id for vote in votes
            if vote.kind is ReviewerKind.MODEL
            and vote.independent
            and vote.decision is GateDecision.ALLOW
        }

        if request.risk is RiskLevel.LOW:
            return self._record(ToolGateResult(
                GateDecision.ALLOW, "ARK-TOOL-00",
                "low-risk allowlisted capability", request.request_id,
            ))
        if request.risk is RiskLevel.MEDIUM:
            if owner_approved:
                return self._record(ToolGateResult(
                    GateDecision.ALLOW, "ARK-TOOL-05",
                    "owner approval recorded", request.request_id,
                ))
            return self._record(ToolGateResult(
                GateDecision.REVIEW, "ARK-TOOL-05",
                "medium-risk action requires owner approval", request.request_id,
            ))
        if request.risk is RiskLevel.HIGH:
            if owner_approved and independent_models:
                return self._record(ToolGateResult(
                    GateDecision.ALLOW, "ARK-TOOL-06",
                    "owner approval and independent model assessment recorded",
                    request.request_id,
                ))
            return self._record(ToolGateResult(
                GateDecision.REVIEW, "ARK-TOOL-06",
                "high-risk action requires owner approval and an independent model assessment",
                request.request_id,
            ))

        if owner_approved and human_approvals and len(independent_models) >= 2:
            return self._record(ToolGateResult(
                GateDecision.ALLOW, "ARK-TOOL-07",
                "critical action has owner, second-human, and two independent model reviews",
                request.request_id,
            ))
        return self._record(ToolGateResult(
            GateDecision.REVIEW, "ARK-TOOL-07",
            "critical action is held pending owner + second human + two independent model reviews",
            request.request_id,
        ))
