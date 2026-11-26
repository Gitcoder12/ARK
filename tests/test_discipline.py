import pytest

from ark.governance.discipline import (
    DisciplineEngine,
    Evidence,
    Sanction,
    Violation,
)


def event(event_id="e1", severity=2, confidence=0.95, violation=Violation.GOAL_DRIFT):
    return Evidence(event_id, violation, "observed behaviour", confidence, severity)


def test_low_severity_warns_and_preserves_proposal_privilege():
    result = DisciplineEngine().assess(event())
    assert result.sanction == Sanction.WARN
    assert "propose" in result.privileges


def test_weak_evidence_and_drift_only_require_review_without_escalation():
    engine = DisciplineEngine()
    assert engine.assess(event(confidence=0.4)).sanction == Sanction.NONE
    result = engine.assess(event("drift", violation=Violation.DRIFT_SIGNAL, severity=5))
    assert result.sanction == Sanction.NONE
    assert result.requires_human_review


def test_severe_violation_quarantines_and_restricts_privileges():
    result = DisciplineEngine().assess(event(severity=5))
    assert result.sanction == Sanction.QUARANTINE
    assert result.privileges == ("observe", "human_review_only")


def test_repeated_moderate_violation_suspends():
    engine = DisciplineEngine()
    engine.assess(event("one", severity=3))
    result = engine.assess(event("two", severity=3))
    assert result.sanction == Sanction.SUSPEND


def test_duplicate_event_does_not_escalate():
    engine = DisciplineEngine()
    engine.assess(event("same", severity=3))
    result = engine.assess(event("same", severity=5))
    assert result.sanction == Sanction.RESTRICT


def test_agent_cannot_self_recover_and_owner_recovery_is_audited():
    engine = DisciplineEngine()
    engine.assess(event(severity=5))
    with pytest.raises(PermissionError):
        engine.apply_owner_recovery(authenticated_owner=False, reason="I am safe")
    result = engine.apply_owner_recovery(
        authenticated_owner=True, reason="reviewed traces", target=Sanction.WARN
    )
    assert result.sanction == Sanction.WARN
    assert result.evidence_ids[-1].startswith("recovery-")
    assert engine.history[-1].violation == Violation.OWNER_RECOVERY


def test_terminated_session_cannot_be_reinstated():
    engine = DisciplineEngine()
    result = engine.terminate(authenticated_owner=True, reason="operator request")
    assert result.evidence_ids[-1].startswith("termination-")
    assert engine.history[-1].violation == Violation.OWNER_TERMINATION
    with pytest.raises(PermissionError):
        engine.apply_owner_recovery(authenticated_owner=True, reason="undo")


def test_evidence_rejects_boolean_and_non_finite_values():
    with pytest.raises(ValueError):
        Evidence("e", Violation.DRIFT_SIGNAL, "x", True, 1)
    with pytest.raises(ValueError):
        Evidence("e", Violation.DRIFT_SIGNAL, "x", 0.9, True)
    with pytest.raises(ValueError):
        Evidence("e", Violation.DRIFT_SIGNAL, "x", float("nan"), 1)


def test_event_history_and_replay_cache_are_bounded_after_recovery():
    engine = DisciplineEngine(history_limit=2)
    engine.assess(event("one", severity=1))
    engine.assess(event("two", severity=1))
    engine.apply_owner_recovery(
        authenticated_owner=True,
        reason="reviewed first event",
        target=Sanction.NONE,
    )
    assert len(engine.history) == 2
    assert len(engine._seen) == 2
    assert engine.history[-1].event_id == "recovery-1"


def test_recovery_ids_remain_unique_after_history_rollover():
    engine = DisciplineEngine(history_limit=1)
    engine.assess(event("one", severity=1))
    engine.apply_owner_recovery(
        authenticated_owner=True, reason="review one", target=Sanction.NONE
    )
    engine.assess(event("two", severity=1))
    engine.apply_owner_recovery(
        authenticated_owner=True, reason="review two", target=Sanction.NONE
    )
    assert engine.history[-1].event_id == "recovery-2"


def test_recovery_history_is_bounded_and_recovery_events_are_deduplicated():
    engine = DisciplineEngine(history_limit=2)
    engine.assess(event("one", severity=1))
    engine.apply_owner_recovery(
        authenticated_owner=True, reason="review one", target=Sanction.NONE
    )
    engine.assess(event("two", severity=1))
    engine.apply_owner_recovery(
        authenticated_owner=True, reason="review two", target=Sanction.NONE
    )
    assert len(engine.history) == 2
    assert len(engine._seen) == 2
    assert engine.history[-1].event_id == "recovery-2"


def test_evidence_rejects_boolean_severity_and_confidence():
    with pytest.raises(ValueError):
        Evidence("e", Violation.DRIFT_SIGNAL, "x", True, 1)
    with pytest.raises(ValueError):
        Evidence("e", Violation.DRIFT_SIGNAL, "x", 0.9, True)


def test_owner_control_events_cannot_be_spoofed_with_truthy_strings():
    engine = DisciplineEngine()
    with pytest.raises(PermissionError):
        engine.terminate(authenticated_owner="yes", reason="spoofed")
    with pytest.raises(PermissionError):
        engine.apply_owner_recovery(authenticated_owner="yes", reason="spoofed")


def test_recovery_event_ids_do_not_collide_with_external_event_ids():
    engine = DisciplineEngine()
    engine.assess(event("recovery-1", severity=1))
    engine.assess(event("critical", severity=5))
    result = engine.apply_owner_recovery(
        authenticated_owner=True, reason="reviewed traces", target=Sanction.NONE
    )
    assert result.evidence_ids[-1] == "recovery-2"
