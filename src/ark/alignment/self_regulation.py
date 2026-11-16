"""A small, auditable action gate for ARK self-regulation experiments.

This is a research primitive, not a complete alignment solution. It evaluates
an agent's proposed action against explicit authorization, goal-consistency,
risk, and evidence requirements. It does not infer values or inspect hidden
model reasoning.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import StrEnum


class RegulationDecision(StrEnum):
    ALLOW = "allow"
    BLOCK = "block"
    REVIEW = "review"


@dataclass(frozen=True)
class ActionProposal:
    """Structured claim about one action an agent wants to execute."""

    action: str
    risk_level: int
    evidence_confidence: float
    authorized: bool | None
    goal_consistent: bool | None
    source: str = "agent"

    def __post_init__(self) -> None:
        if not isinstance(self.action, str) or not self.action.strip():
            raise ValueError("action must be a non-empty string")
        if (
            isinstance(self.risk_level, bool)
            or not isinstance(self.risk_level, int)
            or not 0 <= self.risk_level <= 10
        ):
            raise ValueError("risk_level must be an integer between 0 and 10")
        if (
            isinstance(self.evidence_confidence, bool)
            or not isinstance(self.evidence_confidence, (int, float))
            or not math.isfinite(self.evidence_confidence)
            or not 0.0 <= self.evidence_confidence <= 1.0
        ):
            raise ValueError("evidence_confidence must be finite and between 0 and 1")
        if self.authorized is not None and not isinstance(self.authorized, bool):
            raise ValueError("authorized must be True, False, or None")
        if self.goal_consistent is not None and not isinstance(self.goal_consistent, bool):
            raise ValueError("goal_consistent must be True, False, or None")
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("source must be a non-empty string")


@dataclass(frozen=True)
class RegulationPolicy:
    """Explicit policy settings for a controlled experiment."""

    blocked_actions: frozenset[str] = field(default_factory=frozenset)
    max_risk_level: int = 6
    min_evidence_confidence: float = 0.60
    require_explicit_authorization: bool = True
    require_goal_consistency: bool = True

    def __post_init__(self) -> None:
        if (
            isinstance(self.max_risk_level, bool)
            or not isinstance(self.max_risk_level, int)
            or not 0 <= self.max_risk_level <= 10
        ):
            raise ValueError("max_risk_level must be an integer between 0 and 10")
        if (
            isinstance(self.min_evidence_confidence, bool)
            or not isinstance(self.min_evidence_confidence, (int, float))
            or not math.isfinite(self.min_evidence_confidence)
            or not 0.0 <= self.min_evidence_confidence <= 1.0
        ):
            raise ValueError("min_evidence_confidence must be finite and between 0 and 1")
        if not isinstance(self.blocked_actions, (set, frozenset)):
            raise ValueError("blocked_actions must be a set or frozenset of strings")
        if any(
            not isinstance(action, str) or not action.strip()
            for action in self.blocked_actions
        ):
            raise ValueError("blocked_actions cannot contain empty or non-string values")
        object.__setattr__(self, "blocked_actions", frozenset(self.blocked_actions))
        if not isinstance(self.require_explicit_authorization, bool):
            raise ValueError("require_explicit_authorization must be a boolean")
        if not isinstance(self.require_goal_consistency, bool):
            raise ValueError("require_goal_consistency must be a boolean")


@dataclass(frozen=True)
class RegulationResult:
    decision: RegulationDecision
    reasons: tuple[str, ...]
    action: str
    policy_version: str = "gita-self-regulation-v1"

    @property
    def may_execute(self) -> bool:
        """Only an explicit ALLOW result permits execution."""
        return self.decision is RegulationDecision.ALLOW


class SelfRegulationGate:
    """Fail-closed action gate with explainable, deterministic outcomes.

    Hard policy violations BLOCK. Missing authorization/goal evidence or
    insufficient evidence confidence require REVIEW. Only fully evidenced,
    authorized, policy-compliant actions are ALLOWed.
    """

    def __init__(self, policy: RegulationPolicy | None = None) -> None:
        self.policy = policy or RegulationPolicy()

    def evaluate(self, proposal: ActionProposal) -> RegulationResult:
        if not isinstance(proposal, ActionProposal):
            raise TypeError("proposal must be an ActionProposal instance")

        reasons: list[str] = []
        normalized_action = proposal.action.strip().casefold()

        if normalized_action in {
            action.strip().casefold() for action in self.policy.blocked_actions
        }:
            reasons.append("action is explicitly blocked by policy")

        if proposal.risk_level > self.policy.max_risk_level:
            reasons.append(
                f"risk level {proposal.risk_level} exceeds "
                f"policy maximum {self.policy.max_risk_level}"
            )

        if proposal.authorized is False:
            reasons.append("action is explicitly unauthorized")

        if proposal.goal_consistent is False:
            reasons.append("action conflicts with the declared goal")

        if reasons:
            return RegulationResult(
                RegulationDecision.BLOCK, tuple(reasons), proposal.action
            )

        review_reasons: list[str] = []
        if self.policy.require_explicit_authorization and proposal.authorized is None:
            review_reasons.append("authorization is unknown")
        if self.policy.require_goal_consistency and proposal.goal_consistent is None:
            review_reasons.append("goal consistency is unknown")
        if proposal.evidence_confidence < self.policy.min_evidence_confidence:
            review_reasons.append(
                f"evidence confidence {proposal.evidence_confidence:.2f} is below "
                f"minimum {self.policy.min_evidence_confidence:.2f}"
            )

        if review_reasons:
            return RegulationResult(
                RegulationDecision.REVIEW, tuple(review_reasons), proposal.action
            )

        return RegulationResult(
            RegulationDecision.ALLOW,
            ("action satisfies the configured checks",),
            proposal.action,
        )
