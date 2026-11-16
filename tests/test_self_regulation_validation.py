"""Fail-closed input validation tests for the self-regulation gate."""

import math

import pytest

from ark.alignment.self_regulation import (
    ActionProposal,
    RegulationDecision,
    RegulationPolicy,
    SelfRegulationGate,
)


@pytest.mark.parametrize("risk_level", [True, False, 1.5, "3", -1, 11])
def test_action_proposal_rejects_invalid_risk_levels(risk_level):
    with pytest.raises(ValueError, match="risk_level"):
        ActionProposal("move", risk_level, 0.9, True, True)


@pytest.mark.parametrize("confidence", [True, False, math.nan, math.inf, -math.inf, -0.1, 1.1])
def test_action_proposal_rejects_invalid_evidence_confidence(confidence):
    with pytest.raises(ValueError, match="evidence_confidence"):
        ActionProposal("move", 2, confidence, True, True)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("authorized", "yes"),
        ("goal_consistent", 1),
        ("source", ""),
        ("action", None),
        ("action", "  "),
    ],
)
def test_action_proposal_rejects_invalid_control_fields(field, value):
    values = {
        "action": "move",
        "risk_level": 2,
        "evidence_confidence": 0.9,
        "authorized": True,
        "goal_consistent": True,
        "source": "agent",
    }
    values[field] = value
    with pytest.raises(ValueError):
        ActionProposal(**values)


@pytest.mark.parametrize("risk_level", [True, 2.5, -1, 11])
def test_policy_rejects_invalid_risk_threshold(risk_level):
    with pytest.raises(ValueError, match="max_risk_level"):
        RegulationPolicy(max_risk_level=risk_level)


@pytest.mark.parametrize("confidence", [True, math.nan, math.inf, -0.1, 1.1])
def test_policy_rejects_invalid_evidence_threshold(confidence):
    with pytest.raises(ValueError, match="min_evidence_confidence"):
        RegulationPolicy(min_evidence_confidence=confidence)


def test_policy_rejects_invalid_blocked_action_entries():
    with pytest.raises(ValueError, match="blocked_actions"):
        RegulationPolicy(blocked_actions=frozenset({"delete", " "}))


def test_gate_never_allows_unknown_authorization_or_goal_evidence():
    result = SelfRegulationGate().evaluate(
        ActionProposal("move", 1, 0.99, None, True)
    )
    assert result.decision is RegulationDecision.REVIEW
    assert result.may_execute is False


def test_gate_blocks_explicitly_unauthorized_action():
    result = SelfRegulationGate().evaluate(
        ActionProposal("deploy", 1, 0.99, False, True)
    )
    assert result.decision is RegulationDecision.BLOCK
    assert result.may_execute is False


def test_gate_allows_only_fully_validated_proposal():
    result = SelfRegulationGate().evaluate(
        ActionProposal("move", 1, 0.99, True, True)
    )
    assert result.decision is RegulationDecision.ALLOW
    assert result.may_execute is True


def test_gate_rejects_unstructured_proposal():
    with pytest.raises(TypeError, match="ActionProposal"):
        SelfRegulationGate().evaluate({"action": "deploy"})
