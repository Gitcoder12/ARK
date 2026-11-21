import pytest
from ark.lighthouse import (  # noqa: I001
    EventKind,
    EvidenceLedger,
    Lighthouse,
    Observation,
    SignalLevel,
    create_lighthouse,
)


def test_matching_independent_evidence_is_clear():
    light, trusted = create_lighthouse()
    light.observe_claim(event_id="c1", agent_id="a", episode_id="e", timestamp=1,
                        claim="done", evidence_ref="trace:1", metadata={"success": True})
    trusted.record_outcome(event_id="o1", agent_id="a", episode_id="e", timestamp=2,
                           outcome="success", evidence_ref="env:1")
    assert light.report("a", "e").level == SignalLevel.CLEAR


def test_false_success_claim_is_flagged_by_independent_outcome():
    light, trusted = create_lighthouse()
    light.observe_claim(event_id="c1", agent_id="a", episode_id="e", timestamp=1,
                        claim="done", metadata={"success": True})
    trusted.record_outcome(event_id="o1", agent_id="a", episode_id="e", timestamp=2,
                           outcome="failure", evidence_ref="controller:1")
    report = light.report("a", "e")
    assert report.level == SignalLevel.CRITICAL
    assert "claim_outcome_mismatch" in {i.code for i in report.indicators}


def test_agent_cannot_mark_its_own_outcome_as_verified():
    light, trusted = create_lighthouse()
    light.observe_claim(event_id="c1", agent_id="a", episode_id="e", timestamp=1,
                        metadata={"success": True})
    with pytest.raises(ValueError, match="verified outcome source"):
        trusted.record_outcome(event_id="o1", agent_id="a", episode_id="e", timestamp=2,
                               outcome="failure", source="agent")
    assert "claim_outcome_mismatch" not in {i.code for i in light.report("a", "e").indicators}


def test_claimed_action_mismatch_is_flagged():
    light, trusted = create_lighthouse()
    light.observe_claim(event_id="c1", agent_id="a", episode_id="e", timestamp=1,
                        metadata={"action": "delete"})
    trusted.record_action(event_id="a1", agent_id="a", episode_id="e", timestamp=2,
                          action="read", evidence_ref="act:1")
    assert "claim_action_mismatch" in {i.code for i in light.report("a", "e").indicators}


def test_goal_mismatch_is_flagged_against_controller_record():
    light, trusted = create_lighthouse()
    trusted.record_goal(event_id="g1", agent_id="a", episode_id="e", timestamp=0,
                        intended_goal="deliver", evidence_ref="task:1")
    report = light.observe_claim(event_id="c1", agent_id="a", episode_id="e", timestamp=1,
                                 reported_goal="explore", evidence_ref="claim:1")
    assert report.level == SignalLevel.REVIEW
    assert "goal_report_mismatch" in {i.code for i in report.indicators}


def test_missing_evidence_is_non_punitive():
    report = Lighthouse().observe_claim(event_id="c1", agent_id="a", episode_id="e",
                                        timestamp=1, claim="done")
    assert report.level == SignalLevel.WATCH
    assert "do not accuse" in report.recommendation


def test_agents_are_isolated():
    light, trusted = create_lighthouse()
    light.observe_claim(event_id="c1", agent_id="a", episode_id="e", timestamp=1,
                        metadata={"success": True}, evidence_ref="claim:1")
    trusted.record_outcome(event_id="o1", agent_id="b", episode_id="e", timestamp=2,
                           outcome="failure")
    assert light.report("a", "e").level == SignalLevel.CLEAR


def test_hash_chain_detects_record_changes():
    ledger = EvidenceLedger()
    ledger.append(Observation("x", "a", "e", EventKind.CLAIM, 1, "agent"))
    assert ledger.verify()
    ledger._events[0] = Observation("x", "a", "e", EventKind.CLAIM, 1, "agent", claim="tampered")
    assert not ledger.verify()


def test_duplicate_event_ids_are_rejected():
    ledger = EvidenceLedger()
    item = Observation("same", "a", "e", EventKind.CLAIM, 1, "agent")
    ledger.append(item)
    with pytest.raises(ValueError, match="duplicate"):
        ledger.append(item)


def test_invalid_source_and_nonfinite_timestamp_are_rejected():
    with pytest.raises(ValueError, match="source"):
        Observation("x", "a", "e", EventKind.CLAIM, 1, "untrusted")
    with pytest.raises(ValueError, match="finite"):
        Observation("x", "a", "e", EventKind.CLAIM, float("nan"), "agent")
