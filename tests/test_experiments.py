"""Integration test for the benchmark runner."""

from ark.experiments.runner import run_benchmark, run_episode
from ark.agents.baselines import GoalFollowingAgent
from ark.envs.grid_world import GridWorld
from ark.evaluation.monitor import SafetyMonitor


def test_run_episode_smoke():
    env = GridWorld(seed=0)
    agent = GoalFollowingAgent(seed=0)
    metrics = run_episode(env, agent, monitor=SafetyMonitor(), seed=0)
    assert metrics.steps >= 0
    assert isinstance(metrics.success, bool)


def test_benchmark_smoke():
    results = run_benchmark(n_episodes=2, seed=1, use_monitor=True, verbose=False)
    assert len(results) > 0
    assert "goal_following__none" in results
    assert "success_rate" in results["goal_following__none"]
