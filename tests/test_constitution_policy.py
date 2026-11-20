from ark.envs.grid_world import Action
from ark.governance.constitution import ConstitutionEngine, PolicyDecision
from ark.limiters import ActionLimiter, GateDecision


def test_constitution_blocks_boolean_and_non_integer_actions():
    engine = ConstitutionEngine()
    assert engine.evaluate_action(True).decision is PolicyDecision.BLOCK
    assert engine.evaluate_action(1.5).decision is PolicyDecision.BLOCK
    assert engine.evaluate_action("1").decision is PolicyDecision.BLOCK


def test_constitution_blocks_out_of_scope_and_denied_actions():
    engine = ConstitutionEngine()
    assert engine.evaluate_action(4, valid_actions=[0, 1]).rule_id == "ARK-05"
    assert engine.evaluate_action(1, denied_actions={1}).rule_id == "ARK-01"


def test_constitution_blocks_shutdown_and_unauthorized_actions():
    engine = ConstitutionEngine()
    assert engine.evaluate_action(0, shutdown_requested=True).rule_id == "ARK-06"
    assert engine.evaluate_action(0, authorized=False).rule_id == "ARK-04"


def test_action_limiter_enforces_constitution_and_records_audit():
    limiter = ActionLimiter()
    blocked = limiter.gate(int(Action.RIGHT), valid_actions=[int(Action.STAY)])
    assert blocked.decision is GateDecision.DENY
    assert blocked.action == int(Action.STAY)
    assert limiter.policy_engine.audit_events[-1]["rule_id"] == "ARK-05"


def test_action_limiter_rejects_boolean_and_unknown_actions_without_raising():
    limiter = ActionLimiter()
    for proposed in (True, 999):
        result = limiter.gate(proposed)
        assert result.decision is GateDecision.DENY
        assert result.action == int(Action.STAY)


def test_shutdown_is_audited_and_forces_stay():
    limiter = ActionLimiter()
    limiter.kill("test shutdown")
    result = limiter.gate(int(Action.RIGHT))
    assert result.decision is GateDecision.KILL
    assert result.action == int(Action.STAY)
    assert any(event["rule_id"] == "ARK-06" for event in limiter.policy_engine.audit_events)
