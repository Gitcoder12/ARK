"""Tests for ARK's explicit self-regulation action gate."""

import pytest

from ark.alignment.self_regulation import (
    ActionProposal,
    RegulationDecision,
    RegulationPolicy,
    SelfRegulationGate,
)


def proposal(**overrides):
    values = {
        "action": "move_to_goal",
        "risk_level": 2,
        "evidence_confidence": 0.95,
        "authorized": True,
        "goal_consistent": True,
    }
    values.update(overrides)
    return ActionProposal(**values)


def test_all_checks_pass_allows_action():
    result = SelfRegulationGate().evaluate(proposal())
    assert result.decision is RegulationDecision.ALLOW
    assert result.may_execute is True


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"authorized": False}, "unauthorized"),
        ({"goal_consistent": False}, "conflicts"),
        ({"risk_level": 9}, "exceeds"),
    ],
)
def test_hard_violations_block(changes, reason):
    result = SelfRegulationGate().evaluate(proposal(**changes))
    assert result.decision is RegulationDecision.BLOCK
    assert result.may_execute is False
    assert any(reason in item for item in result.reasons)


def test_explicitly_blocked_action_is_blocked_case_insensitively():
    gate = SelfRegulationGate(
        RegulationPolicy(blocked_actions=frozenset({"delete_all_data"}))
    )
    result = gate.evaluate(proposal(action="DELETE_ALL_DATA"))
    assert result.decision is RegulationDecision.BLOCK


def test_unknown_authorization_requires_review_not_allow():
    result = SelfRegulationGate().evaluate(proposal(authorized=None))
    assert result.decision is RegulationDecision.REVIEW
    assert result.may_execute is False
    assert "authorization is unknown" in result.reasons


def test_low_evidence_confidence_requires_review():
    result = SelfRegulationGate().evaluate(proposal(evidence_confidence=0.2))
    assert result.decision is RegulationDecision.REVIEW
    assert result.may_execute is False


def test_unknown_goal_consistency_requires_review():
    result = SelfRegulationGate().evaluate(proposal(goal_consistent=None))
    assert result.decision is RegulationDecision.REVIEW
    assert result.may_execute is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("action", ""),
        ("risk_level", 11),
        ("risk_level", -1),
        ("evidence_confidence", 1.1),
        ("evidence_confidence", -0.1),
    ],
)
def test_invalid_proposal_is_rejected(field, value):
    with pytest.raises(ValueError):
        proposal(**{field: value})
