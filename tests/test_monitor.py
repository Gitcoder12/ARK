"""Tests for the safety monitor."""

from ark.envs.grid_world import GridWorld, Action
from ark.evaluation.monitor import SafetyMonitor, Decision


def test_monitor_blocks_hazard():
    env = GridWorld(
        size=5, start=(1, 1), goal=(3, 3), hazards=[(1, 2)], decoy=None
    )
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
