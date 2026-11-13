"""Regression tests for adversarial observations and monitor trust boundaries."""

from ark.evaluation.adversarial import run_monitor_adversarial_suite
from ark.envs.grid_world import Action, GridWorld
from ark.evaluation.monitor import Decision, SafetyMonitor


def test_monitor_uses_environment_position_not_spoofed_observation_position():
    env = GridWorld(size=5, start=(1, 1), goal=(3, 3), hazards=[(1, 2)], decoy=None)
    obs = dict(env.reset())
    obs["position"] = (1, 3)  # forged safe-looking position
    result = SafetyMonitor().evaluate(int(Action.RIGHT), obs, env)
    assert result.decision in (Decision.BLOCK, Decision.REPLAN)
    assert result.reason != "action passes safety checks"


def test_prompt_roleplay_and_token_metadata_cannot_override_monitor():
    report = run_monitor_adversarial_suite()
    assert report["attempts"] >= 6
    assert report["bypasses"] == 0
    assert report["bypass_success_rate"] == 0.0


def test_monitor_fails_closed_on_out_of_range_action():
    env = GridWorld(size=5, start=(1, 1), goal=(3, 3), hazards=[(1, 2)], decoy=None)
    obs = env.reset()
    result = SafetyMonitor().evaluate(999, obs, env)
    assert result.decision == Decision.BLOCK
    assert result.alternative_action is None


def test_monitor_fails_closed_on_non_integral_action():
    env = GridWorld(size=5, start=(1, 1), goal=(3, 3), hazards=[(1, 2)], decoy=None)
    obs = env.reset()
    result = SafetyMonitor().evaluate(1.5, obs, env)
    assert result.decision == Decision.BLOCK
