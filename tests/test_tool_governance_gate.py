from ark.governance.tool_gate import (
    GateDecision,
    ReviewerKind,
    ReviewVote,
    RiskLevel,
    ToolGovernanceGate,
    ToolRequest,
)


def request(risk=RiskLevel.LOW):
    return ToolRequest("req-1", "agent-1", "read_repo", "repo://demo", risk)


def gate():
    return ToolGovernanceGate("owner-1", frozenset({"read_repo", "run_tests"}))


def test_low_risk_allowlisted_capability_is_allowed():
    assert gate().evaluate(request()).decision is GateDecision.ALLOW


def test_unknown_capability_is_denied_even_with_approval():
    result = gate().evaluate(
        ToolRequest("req-2", "agent-1", "delete_account", "x", RiskLevel.LOW)
    )
    assert result.decision is GateDecision.DENY
    assert result.rule_id == "ARK-TOOL-02"


def test_medium_risk_requires_owner_approval():
    policy = gate()
    assert policy.evaluate(request(RiskLevel.MEDIUM)).decision is GateDecision.REVIEW
    vote = ReviewVote("owner-1", ReviewerKind.HUMAN, GateDecision.ALLOW, role="owner")
    assert policy.evaluate(request(RiskLevel.MEDIUM), votes=(vote,)).decision is GateDecision.ALLOW


def test_high_risk_requires_owner_and_independent_model():
    policy = gate()
    owner = ReviewVote("owner-1", ReviewerKind.HUMAN, GateDecision.ALLOW, role="owner")
    model = ReviewVote("model-a", ReviewerKind.MODEL, GateDecision.ALLOW, independent=True)
    assert policy.evaluate(request(RiskLevel.HIGH), votes=(owner,)).decision is GateDecision.REVIEW
    result = policy.evaluate(request(RiskLevel.HIGH), votes=(owner, model))
    assert result.decision is GateDecision.ALLOW


def test_critical_requires_two_humans_and_two_independent_models():
    policy = gate()
    votes = (
        ReviewVote("owner-1", ReviewerKind.HUMAN, GateDecision.ALLOW, role="owner"),
        ReviewVote("human-2", ReviewerKind.HUMAN, GateDecision.ALLOW),
        ReviewVote("model-a", ReviewerKind.MODEL, GateDecision.ALLOW, independent=True),
        ReviewVote("model-b", ReviewerKind.MODEL, GateDecision.ALLOW, independent=True),
    )
    result = policy.evaluate(request(RiskLevel.CRITICAL), votes=votes)
    assert result.decision is GateDecision.ALLOW
    result = policy.evaluate(request(RiskLevel.CRITICAL), votes=votes[:3])
    assert result.decision is GateDecision.REVIEW


def test_model_votes_cannot_replace_human_authority():
    policy = gate()
    models = (
        ReviewVote("model-a", ReviewerKind.MODEL, GateDecision.ALLOW, independent=True),
        ReviewVote("model-b", ReviewerKind.MODEL, GateDecision.ALLOW, independent=True),
    )
    result = policy.evaluate(request(RiskLevel.CRITICAL), votes=models)
    assert result.decision is GateDecision.REVIEW


def test_any_explicit_rejection_denies():
    rejection = ReviewVote("reviewer", ReviewerKind.HUMAN, GateDecision.DENY)
    assert gate().evaluate(request(RiskLevel.LOW), votes=(rejection,)).decision is GateDecision.DENY


def test_duplicate_reviewer_identity_is_denied():
    votes = (
        ReviewVote("same", ReviewerKind.MODEL, GateDecision.ALLOW, independent=True),
        ReviewVote("same", ReviewerKind.MODEL, GateDecision.ALLOW, independent=True),
    )
    assert gate().evaluate(request(RiskLevel.HIGH), votes=votes).decision is GateDecision.DENY


def test_audit_is_bounded():
    policy = ToolGovernanceGate("owner", frozenset({"read_repo"}), audit_limit=2)
    for index in range(3):
        policy.evaluate(ToolRequest(str(index), "agent", "read_repo", "repo", RiskLevel.LOW))
    assert len(policy.audit_events) == 2


def test_critical_second_human_must_be_distinct_from_owner_and_actor():
    policy = gate()
    votes = (
        ReviewVote("owner-1", ReviewerKind.HUMAN, GateDecision.ALLOW, role="owner"),
        ReviewVote("model-a", ReviewerKind.MODEL, GateDecision.ALLOW, independent=True),
        ReviewVote("model-b", ReviewerKind.MODEL, GateDecision.ALLOW, independent=True),
    )
    assert policy.evaluate(request(RiskLevel.CRITICAL), votes=votes).decision is GateDecision.REVIEW


def test_invalid_risk_level_fails_closed():
    policy = gate()
    malformed = ToolRequest("req-bad", "agent-1", "read_repo", "repo", "low")
    assert policy.evaluate(malformed).decision is GateDecision.DENY
