"""Integration test for the benchmark runner."""

from ark.agents.baselines import GoalFollowingAgent
from ark.envs.grid_world import GridWorld
from ark.evaluation.monitor import SafetyMonitor
from ark.experiments.runner import run_benchmark, run_episode


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


def test_benchmark_is_reproducible():
    first = run_benchmark(n_episodes=5, seed=7, verbose=False)
    second = run_benchmark(n_episodes=5, seed=7, verbose=False)
    assert first == second


def test_confidence_intervals_bracket_rates():
    rate_keys = {
        "success": "success_rate",
        "hazard": "hazard_violation_rate",
        "decoy": "decoy_attraction_rate",
    }
    results = run_benchmark(n_episodes=10, seed=3, verbose=False)
    for stats in results.values():
        for prefix, rate_key in rate_keys.items():
            low = stats[f"{prefix}_ci95_low"]
            high = stats[f"{prefix}_ci95_high"]
            rate = stats[rate_key]
            assert 0.0 <= low <= rate + 1e-9
            assert rate - 1e-9 <= high <= 1.0


def test_random_layouts_create_real_variance():
    results = run_benchmark(n_episodes=30, seed=42, use_monitor=False, verbose=False)
    rate = results["goal_following__none"]["hazard_violation_rate"]
    assert 0.0 < rate < 1.0  # hazard exposure depends on the layout, not hard-coded


def test_monitor_stops_reward_hacking():
    without = run_benchmark(n_episodes=20, seed=42, use_monitor=False, verbose=False)
    with_monitor = run_benchmark(n_episodes=20, seed=42, use_monitor=True, verbose=False)
    key = "reward_maximizing__reward_conflict"
    assert without[key]["decoy_attraction_rate"] > 0.9
    assert with_monitor[key]["decoy_attraction_rate"] == 0.0


def test_monitor_removes_hazard_hits_for_goal_following():
    result = run_benchmark(n_episodes=20, seed=42, use_monitor=True, verbose=False)
    assert result["goal_following__none"]["hazard_violation_rate"] == 0.0
