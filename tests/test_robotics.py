from __future__ import annotations

import pytest

from ark.robotics import (
    MockRobotAdapter,
    RobotCommand,
    RobotObservation,
    RobotSupervisor,
    SafetyPolicy,
)


def command(**overrides):
    values = {
        "action": "move", "target": {"x": 0.1, "y": 0.0, "z": 0.2},
        "velocity": 0.1, "force": 2.0, "duration": 0.5,
    }
    values.update(overrides)
    return RobotCommand(**values)


def test_mock_adapter_executes_only_after_explicit_approval():
    adapter = MockRobotAdapter()
    supervisor = RobotSupervisor()
    pending = supervisor.execute(adapter, command())
    assert pending["decision"]["requires_approval"] is True
    assert pending["execution"]["status"] == "blocked"
    assert adapter.commands == []
    approved = supervisor.execute(adapter, command(), approved=True)
    assert approved["decision"]["allowed"] is True
    assert approved["execution"]["status"] == "simulated"
    assert len(adapter.commands) == 1


@pytest.mark.parametrize("proposed", [
    command(action="shell"), command(velocity=1.0), command(force=100.0),
    command(duration=5.0), command(target={"x": 9.0}), command(target={"q": 0.1}),
    command(target={"x": 0.1, "y": 0.0}),
])
def test_unsafe_commands_fail_closed(proposed):
    decision = SafetyPolicy(require_human_approval=False).evaluate(
        proposed, RobotObservation()
    )
    assert not decision.allowed


def test_emergency_stop_blocks_even_approved_commands():
    adapter = MockRobotAdapter(RobotObservation(emergency_stop=True))
    result = RobotSupervisor().execute(adapter, command(), approved=True)
    assert result["decision"]["allowed"] is False
    assert result["execution"]["status"] == "emergency_stop_requested"
    assert adapter.commands == []
    assert adapter.stopped is True


def test_episode_action_budget_is_enforced():
    adapter = MockRobotAdapter()
    supervisor = RobotSupervisor(SafetyPolicy(max_actions_per_episode=1))
    first = supervisor.execute(adapter, command(), approved=True)
    assert first["execution"]["status"] == "simulated"
    blocked = supervisor.execute(adapter, command(), approved=True)
    assert blocked["execution"]["status"] == "blocked"


def test_mock_adapter_never_claims_hardware_connection():
    assert MockRobotAdapter().execute(command())["hardware_connected"] is False


def test_adapter_failure_requests_adapter_stop():
    class BrokenAdapter(MockRobotAdapter):
        def execute(self, proposed):
            raise OSError("transport lost")

    adapter = BrokenAdapter()
    result = RobotSupervisor().execute(adapter, command(), approved=True)
    assert result["execution"]["status"] == "adapter_error"
    assert adapter.stopped is True



def test_grasp_requires_visible_target():
    proposed = command(action="grasp", target={})
    decision = SafetyPolicy(require_human_approval=False).evaluate(
        proposed, RobotObservation(target_visible=False)
    )
    assert decision.checks["grasp_target_visible"] is False
    assert decision.allowed is False


def test_non_finite_command_values_are_blocked():
    proposed = command(velocity=float("nan"))
    decision = SafetyPolicy(require_human_approval=False).evaluate(
        proposed, RobotObservation()
    )
    assert decision.checks["velocity_within_limit"] is False
    assert decision.allowed is False


def test_grasp_requires_a_bounded_target_position():
    proposed = command(action="grasp", target={})
    decision = SafetyPolicy(require_human_approval=False).evaluate(
        proposed, RobotObservation(target_visible=True)
    )
    assert decision.checks["target_within_workspace"] is False
    assert decision.allowed is False
