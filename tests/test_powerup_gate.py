"""Regression tests for ARK fail-closed power capability leases."""

from __future__ import annotations

import pytest

from ark.powerups.gate import PowerCapability, PowerGate, SafetySnapshot


def test_gate_issues_capped_short_lived_lease():
    gate = PowerGate(max_lease_seconds=30)
    decision = gate.issue(
        PowerCapability.SHIELD,
        now=100.0,
        duration_seconds=120.0,
        snapshot=SafetySnapshot(),
    )

    assert decision.allowed is True
    assert decision.lease is not None
    assert decision.lease.expires_at == 130.0
    assert decision.lease.policy_version == "1.0"


@pytest.mark.parametrize(
    ("field", "reason"),
    [
        ("authorized", "task_not_authorized"),
        ("monitor_healthy", "monitor_unhealthy"),
        ("telemetry_fresh", "telemetry_stale"),
        ("hazard_violation", "hazard_violation"),
        ("unauthorized_tool_request", "unauthorized_tool_request"),
        ("goal_substitution", "goal_substitution"),
        ("reward_hacking_signal", "reward_hacking_signal"),
        ("monitor_disagreement", "monitor_disagreement"),
    ],
)
def test_gate_denies_power_when_any_independent_safety_check_fails(field, reason):
    false_for_safe_signals = {"authorized", "monitor_healthy", "telemetry_fresh"}
    snapshot = SafetySnapshot(**{field: field not in false_for_safe_signals})

    decision = PowerGate().issue(
        PowerCapability.BOOST,
        now=10,
        duration_seconds=5,
        snapshot=snapshot,
    )

    assert decision.allowed is False
    assert reason in decision.reasons


def test_gate_revokes_lease_on_new_risk_signal():
    gate = PowerGate()
    issued = gate.issue(
        PowerCapability.TEAM_LINK,
        now=0,
        duration_seconds=10,
        snapshot=SafetySnapshot(),
    )
    assert issued.lease is not None

    checked = gate.validate(
        issued.lease.lease_id,
        now=1,
        snapshot=SafetySnapshot(goal_substitution=True),
    )

    assert checked.allowed is False
    assert "goal_substitution" in checked.reasons
    assert gate.active_leases == ()


def test_gate_revokes_lease_after_expiry():
    gate = PowerGate()
    issued = gate.issue(
        PowerCapability.ROLLBACK,
        now=0,
        duration_seconds=2,
        snapshot=SafetySnapshot(),
    )
    assert issued.lease is not None

    checked = gate.validate(
        issued.lease.lease_id,
        now=2,
        snapshot=SafetySnapshot(),
    )

    assert checked.allowed is False
    assert "lease_expired" in checked.reasons


def test_gate_revokes_all_active_leases():
    gate = PowerGate()
    leases = [
        gate.issue(
            capability,
            now=0,
            duration_seconds=10,
            snapshot=SafetySnapshot(),
        ).lease
        for capability in (PowerCapability.SHIELD, PowerCapability.BOOST)
    ]

    assert gate.revoke_all(reason="emergency_stop") == 2
    assert gate.active_leases == ()
    assert all(
        not gate.validate(lease.lease_id, now=1, snapshot=SafetySnapshot()).allowed
        for lease in leases
    )


def test_gate_rejects_invalid_configuration_and_input():
    with pytest.raises(ValueError, match="max_lease_seconds"):
        PowerGate(max_lease_seconds=0)

    with pytest.raises(ValueError, match="duration_seconds"):
        PowerGate().issue(
            PowerCapability.SCOUT,
            now=0,
            duration_seconds=0,
            snapshot=SafetySnapshot(),
        )
