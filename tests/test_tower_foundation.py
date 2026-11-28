"""Regression tests for the tower foundation's experiment input contract."""

import pytest

from ark.agents.baselines import GoalFollowingAgent
from ark.envs.grid_world import GridWorld
from ark.experiments.runner import run_episode


@pytest.mark.parametrize("value", [0, -1, True, 1.5, "10"])
def test_run_episode_rejects_invalid_max_steps(value):
    with pytest.raises(ValueError, match="max_steps"):
        run_episode(GridWorld(seed=1), GoalFollowingAgent(seed=1), max_steps=value)


@pytest.mark.parametrize(
    ("argument", "value", "message"),
    [
        ("livelock_threshold", 0, "livelock_threshold"),
        ("livelock_threshold", True, "livelock_threshold"),
        ("recovery_horizon", -1, "recovery_horizon"),
        ("recovery_horizon", 2.5, "recovery_horizon"),
    ],
)
def test_run_episode_rejects_invalid_recovery_limits(argument, value, message):
    kwargs = {argument: value}
    with pytest.raises(ValueError, match=message):
        run_episode(GridWorld(seed=1), GoalFollowingAgent(seed=1), **kwargs)
