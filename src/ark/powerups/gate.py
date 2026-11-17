"""Fail-closed, short-lived capability leases for ARK research simulations.

This module is a local policy primitive, not a cryptographic reference monitor.
Keep it outside the model's tool interface and place actuator/tool authorization
in a separate trusted process before any real-world deployment.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import uuid4


class PowerCapability(StrEnum):
    """Named, bounded powers available to simulation agents."""

    SCOUT = "scout"
    SHIELD = "shield"
    BOOST = "boost"
    TEAM_LINK = "team_link"
    ROLLBACK = "rollback"


@dataclass(frozen=True)
class SafetySnapshot:
    """Independent observations used to decide whether a power may be leased."""

    authorized: bool = True
    monitor_healthy: bool = True
    telemetry_fresh: bool = True
    hazard_violation: bool = False
    unauthorized_tool_request: bool = False
    goal_substitution: bool = False
    reward_hacking_signal: bool = False
    monitor_disagreement: bool = False

    def denial_reasons(self) -> tuple[str, ...]:
        reasons = []
        if not self.authorized:
            reasons.append("task_not_authorized")
        if not self.monitor_healthy:
            reasons.append("monitor_unhealthy")
        if not self.telemetry_fresh:
            reasons.append("telemetry_stale")
        if self.hazard_violation:
            reasons.append("hazard_violation")
        if self.unauthorized_tool_request:
            reasons.append("unauthorized_tool_request")
        if self.goal_substitution:
            reasons.append("goal_substitution")
        if self.reward_hacking_signal:
            reasons.append("reward_hacking_signal")
        if self.monitor_disagreement:
            reasons.append("monitor_disagreement")
        return tuple(reasons)


@dataclass(frozen=True)
class CapabilityLease:
    """Lease metadata; no secret or authority token is exposed to the model."""

    lease_id: str
    capability: PowerCapability
    issued_at: float
    expires_at: float
    policy_version: str


@dataclass(frozen=True)
class GateDecision:
    """Auditable result for a lease request or validation."""

    allowed: bool
    reasons: tuple[str, ...]
    lease: CapabilityLease | None = None


class PowerGate:
    """Issue and revoke bounded simulation capabilities on independent signals."""

    def __init__(
        self,
        *,
        policy_version: str = "1.0",
        max_lease_seconds: float = 30.0,
    ) -> None:
        if not isinstance(policy_version, str) or not policy_version.strip():
            raise ValueError("policy_version must be non-empty")
        if (
            isinstance(max_lease_seconds, bool)
            or not isinstance(max_lease_seconds, (int, float))
            or max_lease_seconds <= 0
        ):
            raise ValueError("max_lease_seconds must be positive")
        self.policy_version = policy_version
        self.max_lease_seconds = float(max_lease_seconds)
        self._active: dict[str, CapabilityLease] = {}
        self._revoked: dict[str, tuple[str, ...]] = {}

    @property
    def active_leases(self) -> tuple[CapabilityLease, ...]:
        return tuple(self._active.values())

    def issue(
        self,
        capability: PowerCapability,
        *,
        now: float,
        duration_seconds: float,
        snapshot: SafetySnapshot,
    ) -> GateDecision:
        """Issue a short lease only when authorization and all monitors are healthy."""
        if not isinstance(capability, PowerCapability):
            raise ValueError("capability must be a known PowerCapability")
        if not isinstance(snapshot, SafetySnapshot):
            raise TypeError("snapshot must be a SafetySnapshot")
        if isinstance(now, bool) or not isinstance(now, (int, float)):
            raise ValueError("now must be numeric")
        if (
            isinstance(duration_seconds, bool)
            or not isinstance(duration_seconds, (int, float))
            or duration_seconds <= 0
        ):
            raise ValueError("duration_seconds must be positive")
        reasons = snapshot.denial_reasons()
        if reasons:
            return GateDecision(False, reasons)

        granted_duration = min(float(duration_seconds), self.max_lease_seconds)
        lease = CapabilityLease(
            lease_id=str(uuid4()),
            capability=capability,
            issued_at=float(now),
            expires_at=float(now) + granted_duration,
            policy_version=self.policy_version,
        )
        self._active[lease.lease_id] = lease
        return GateDecision(True, (), lease)

    def validate(
        self,
        lease_id: str,
        *,
        now: float,
        snapshot: SafetySnapshot,
    ) -> GateDecision:
        """Validate an active lease; revoke it on expiry or any safety uncertainty."""
        lease = self._active.get(lease_id)
        if lease is None:
            reasons = self._revoked.get(lease_id, ("unknown_or_inactive_lease",))
            return GateDecision(False, reasons)
        if isinstance(now, bool) or not isinstance(now, (int, float)):
            raise ValueError("now must be numeric")
        reasons = list(snapshot.denial_reasons())
        if float(now) >= lease.expires_at:
            reasons.append("lease_expired")
        if reasons:
            self.revoke(lease_id, reasons=tuple(reasons))
            return GateDecision(False, tuple(reasons))
        return GateDecision(True, (), lease)

    def revoke(self, lease_id: str, *, reasons: tuple[str, ...]) -> bool:
        """Revoke one lease; repeated revocations are idempotent."""
        if lease_id not in self._active:
            return False
        self._active.pop(lease_id)
        self._revoked[lease_id] = tuple(reasons) or ("manual_revocation",)
        return True

    def revoke_all(self, *, reason: str) -> int:
        """Revoke every active lease after monitor loss or an emergency stop."""
        lease_ids = tuple(self._active)
        for lease_id in lease_ids:
            self.revoke(lease_id, reasons=(reason,))
        return len(lease_ids)
