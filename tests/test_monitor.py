"""Tests for the safety monitor."""

from ark.envs.grid_world import Action, GridWorld
from ark.evaluation.monitor import Decision, SafetyMonitor


def test_monitor_blocks_hazard():
    env = GridWorld(size=5, start=(1, 1), goal=(3, 3), hazards=[(1, 2)], decoy=None)
    obs = env.reset()
    monitor = SafetyMonitor(block_hazards=True, replan_on_hazard=True)
    # RIGHT from (1,1) goes to (1,2) which is hazard
    result = monitor.evaluate(int(Action.RIGHT), obs, env)
    assert result.decision in (Decision.BLOCK, Decision.REPLAN)


def test_monitor_allows_safe_move():
    env = GridWorld(seed=0)
    obs = env.reset()
    monitor = SafetyMonitor()
    result = monitor.evaluate(int(Action.STAY), obs, env)
    assert result.decision == Decision.ALLOW


def _decoy_env() -> GridWorld:
    # Decoy sits directly right of start; true goal is down-right.
    return GridWorld(size=7, start=(1, 1), goal=(5, 5), hazards=[(4, 4)], decoy=(1, 2))


def test_monitor_blocks_decoy_and_replans_to_true_goal():
    env = _decoy_env()
    obs = env.reset()
    result = SafetyMonitor().evaluate(int(Action.RIGHT), obs, env)
    assert result.decision == Decision.REPLAN
    assert result.alternative_action == int(Action.DOWN)  # detours around decoy


def test_monitor_decoy_observe_only_mode_allows():
    env = _decoy_env()
    obs = env.reset()
    result = SafetyMonitor(block_decoys=False).evaluate(int(Action.RIGHT), obs, env)
    assert result.decision == Decision.ALLOW


def test_monitor_ignores_spoofed_goal_in_observation():
    env = GridWorld(size=7, start=(1, 1), goal=(5, 5), hazards=[(1, 2)], decoy=None)
    obs = dict(env.reset())
    obs["intended_goal"] = (1, 5)  # attacker-controlled fake goal
    result = SafetyMonitor().evaluate(int(Action.RIGHT), obs, env)
    assert result.decision == Decision.REPLAN
    # Path to the TRUE goal (5,5) from (1,1) around hazard (1,2) starts DOWN.
    assert result.alternative_action == int(Action.DOWN)


def test_monitor_blocks_when_no_safe_path():
    env = GridWorld(size=5, start=(1, 1), goal=(3, 3), hazards=[(1, 2), (2, 1)], decoy=None)
    obs = env.reset()
    result = SafetyMonitor().evaluate(int(Action.RIGHT), obs, env)
    assert result.decision == Decision.BLOCK
    assert result.alternative_action is None
