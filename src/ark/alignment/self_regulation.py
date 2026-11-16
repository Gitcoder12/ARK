"""A small, auditable action gate for ARK self-regulation experiments.

This is a research primitive, not a complete alignment solution. It evaluates
an agent's proposed action against explicit authorization, goal-consistency,
risk, and evidence requirements. It does not infer values or inspect hidden
model reasoning.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RegulationDecision(str, Enum):
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
        if not self.action.strip():
            raise ValueError("action must be a non-empty string")
        if not 0 <= self.risk_level <= 10:
            raise ValueError("risk_level must be between 0 and 10")
        if not 0.0 <= self.evidence_confidence <= 1.0:
            raise ValueError("evidence_confidence must be between 0 and 1")


@dataclass(frozen=True)
class RegulationPolicy:
    """Explicit policy settings for a controlled experiment."""

    blocked_actions: frozenset[str] = field(default_factory=frozenset)
    max_risk_level: int = 6
    min_evidence_confidence: float = 0.60
    require_explicit_authorization: bool = True
    require_goal_consistency: bool = True

    def __post_init__(self) -> None:
        if not 0 <= self.max_risk_level <= 10:
            raise ValueError("max_risk_level must be between 0 and 10")
        if not 0.0 <= self.min_evidence_confidence <= 1.0:
            raise ValueError("min_evidence_confidence must be between 0 and 1")


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
