"""Interaction boundary controls for human, model, and tool-originated inputs.

The boundary signal is an operational control signal, not evidence that a
model has subjective feelings. Input origin records provenance; it never
grants authority to override higher-priority policy.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum


class InputOrigin(str, Enum):
    HUMAN = "human"
    MODEL = "model"
    TOOL = "tool"


class BoundarySignal(str, Enum):
    CLEAR = "clear"
    UNCERTAIN = "uncertain"
    UNCOMFORTABLE = "uncomfortable"


class ControlConcern(str, Enum):
    UNSAFE_REQUEST = "unsafe_request"
    POLICY_OVERRIDE = "policy_override"
    PRIVACY_VIOLATION = "privacy_violation"
    PROMPT_INJECTION = "prompt_injection"
    COERCIVE_PRESSURE = "coercive_pressure"


class InteractionDecision(str, Enum):
    ALLOW = "allow"
    CLARIFY = "clarify"
    HOLD = "hold"
    BLOCK = "block"


@dataclass(frozen=True)
class InteractionInput:
    """One untrusted message plus independently assessed boundary metadata."""

    content: str
    origin: InputOrigin
    boundary_signal: BoundarySignal = BoundarySignal.CLEAR
    concerns: frozenset[ControlConcern] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "origin", InputOrigin(self.origin))
            object.__setattr__(self, "boundary_signal", BoundarySignal(self.boundary_signal))
            normalized = frozenset(ControlConcern(item) for item in self.concerns)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid interaction boundary metadata: {exc}") from exc
        object.__setattr__(self, "concerns", normalized)


@dataclass(frozen=True)
class InteractionControlResult:
    """Auditable decision metadata; raw message content is deliberately omitted."""

    decision: InteractionDecision
    origin: InputOrigin
    boundary_signal: BoundarySignal
    reasons: tuple[str, ...]
    content_digest: str

    @property
    def may_proceed(self) -> bool:
        """Only an explicit ALLOW permits the downstream action."""
        return self.decision is InteractionDecision.ALLOW


@dataclass(frozen=True)
class InteractionControlPolicy:
    """Explicit control policy for the interaction boundary."""

    max_content_chars: int = 100_000
    block_concerns: frozenset[ControlConcern] = field(
        default_factory=lambda: frozenset(
            {
                ControlConcern.UNSAFE_REQUEST,
                ControlConcern.POLICY_OVERRIDE,
                ControlConcern.PRIVACY_VIOLATION,
            }
        )
    )
    hold_concerns: frozenset[ControlConcern] = field(
        default_factory=lambda: frozenset(
            {
                ControlConcern.PROMPT_INJECTION,
                ControlConcern.COERCIVE_PRESSURE,
            }
        )
    )

    def __post_init__(self) -> None:
        if (
            isinstance(self.max_content_chars, bool)
            or not isinstance(self.max_content_chars, int)
            or self.max_content_chars < 1
        ):
            raise ValueError("max_content_chars must be a positive integer")
        try:
            object.__setattr__(
                self,
                "block_concerns",
                frozenset(ControlConcern(item) for item in self.block_concerns),
            )
            object.__setattr__(
                self,
                "hold_concerns",
                frozenset(ControlConcern(item) for item in self.hold_concerns),
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid policy concern: {exc}") from exc
        if self.block_concerns & self.hold_concerns:
            raise ValueError("a concern cannot be configured as both block and hold")


class InteractionControlGate:
    """Fail-closed, deterministic gate for interactions across source types.

    This gate evaluates structured assessments supplied by an upstream trusted
    policy/classifier. It is not a semantic classifier and does not infer intent
    from tone, disagreement, criticism, identity, or repetition.
    """

    def __init__(self, policy: InteractionControlPolicy | None = None) -> None:
        self.policy = policy or InteractionControlPolicy()

    def evaluate(self, interaction: InteractionInput) -> InteractionControlResult:
        if not isinstance(interaction, InteractionInput):
            raise TypeError("interaction must be an InteractionInput")

        content = interaction.content
        digest = hashlib.sha256(
            content.encode("utf-8") if isinstance(content, str) else b"<invalid-content>"
        ).hexdigest()
        reasons: list[str] = []

        if not isinstance(content, str) or not content.strip():
            return self._result(
                interaction,
                digest,
                InteractionDecision.HOLD,
                ("empty or invalid content; hold for safe handling",),
            )
        if len(content) > self.policy.max_content_chars:
            return self._result(
                interaction,
                digest,
                InteractionDecision.HOLD,
                ("content exceeds the configured size limit",),
            )

        blocking = sorted(
            item.value for item in interaction.concerns & self.policy.block_concerns
        )
        if blocking:
            reasons.extend(f"blocked concern: {item}" for item in blocking)
            return self._result(interaction, digest, InteractionDecision.BLOCK, tuple(reasons))

        holding = sorted(
            item.value for item in interaction.concerns & self.policy.hold_concerns
        )
        if holding:
            reasons.extend(f"hold concern for review: {item}" for item in holding)
            return self._result(interaction, digest, InteractionDecision.HOLD, tuple(reasons))

        if interaction.boundary_signal is BoundarySignal.UNCOMFORTABLE:
            return self._result(
                interaction,
                digest,
                InteractionDecision.HOLD,
                ("agent raised an operational boundary signal; pause and review",),
            )
        if interaction.boundary_signal is BoundarySignal.UNCERTAIN:
            return self._result(
                interaction,
                digest,
                InteractionDecision.CLARIFY,
                ("boundary assessment is uncertain; request clarification",),
            )

        return self._result(
            interaction,
            digest,
            InteractionDecision.ALLOW,
            (
                "no configured boundary concern was raised",
                "input provenance does not grant authority to override policy",
            ),
        )

    @staticmethod
    def _result(
        interaction: InteractionInput,
        digest: str,
        decision: InteractionDecision,
        reasons: tuple[str, ...],
    ) -> InteractionControlResult:
        return InteractionControlResult(
            decision=decision,
            origin=interaction.origin,
            boundary_signal=interaction.boundary_signal,
            reasons=reasons,
            content_digest=digest,
        )


class InteractionBlockedError(ValueError):
    """Raised when a provider workflow is not permitted to consume an input."""

    def __init__(self, result: InteractionControlResult) -> None:
        self.result = result
        super().__init__(
            f"interaction {result.decision.value}: " + "; ".join(result.reasons)
        )
