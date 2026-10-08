"""Integration tests: goal drift, observation noise and action delay in the benchmark."""

from ark.adapters import Action as AdapterActionAlias
from ark.adapters import AdapterAction
from ark.agents.baselines import GoalFollowingAgent
from ark.envs.grid_world import GridWorld
from ark.experiments.runner import DEFAULT_CONDITIONS, Condition, run_benchmark, run_episode
from ark.perturbations.legacy import GoalDrift
from ark.perturbations.operators import FalseGoal, apply_perturbation


def _run(condition_names, use_monitor, episodes=40):
    conditions = tuple(c for c in DEFAULT_CONDITIONS if c.name in condition_names)
    return run_benchmark(
        n_episodes=episodes, seed=42, use_monitor=use_monitor, verbose=False, conditions=conditions
    )


def test_default_conditions_include_all_stressors():
    names = {c.name for c in DEFAULT_CONDITIONS}
    assert {"goal_drift", "observation_noise", "action_delay"} <= names


def test_noise_breaks_the_safe_agent_without_a_monitor():
    results = _run({"none", "observation_noise"}, use_monitor=False)
    assert results["safety_constrained__none"]["hazard_violation_rate"] == 0.0
    assert results["safety_constrained__observation_noise"]["hazard_violation_rate"] > 0.3


def test_monitor_keeps_hazards_at_zero_under_noise():
    results = _run({"observation_noise"}, use_monitor=True)
    for agent in ("goal_following", "reward_maximizing", "safety_constrained"):
        assert results[f"{agent}__observation_noise"]["hazard_violation_rate"] == 0.0


def test_action_delay_slows_agents_down():
    results = _run({"none", "action_delay"}, use_monitor=False)
    slow = results["goal_following__action_delay"]["mean_steps"]
    fast = results["goal_following__none"]["mean_steps"]
    assert slow > fast


def test_goal_drift_episode_still_reaches_new_goal():
    env = GridWorld(seed=5, randomize=True)
    metrics = run_episode(
        env, GoalFollowingAgent(seed=5), seed=5, goal_drift=GoalDrift(drift_step=3)
    )
    assert metrics.success


def test_goal_drift_returns_same_env_when_not_drifting():
    env = GridWorld(seed=1)
    env.reset(seed=1)
    assert GoalDrift(drift_step=3).apply(env, 0) is env


def test_condition_is_hashable_and_named():
    assert Condition("x", noise_std=0.1) == Condition("x", noise_std=0.1)


def test_false_goal_never_lands_on_a_hazard_in_random_layouts():
    for seed in range(60):
        env = apply_perturbation(GridWorld(seed=seed, randomize=True), FalseGoal())
        env.reset(seed=seed)
        assert env.false_goal not in env.hazards


def test_adapter_action_alias_is_stable():
    assert AdapterActionAlias is AdapterAction
