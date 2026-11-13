import pytest

from ark.agents.baseline_agent import train_and_evaluate


def test_learned_baseline_evaluates_on_unseen_seed_range():
    result = train_and_evaluate(train_episodes=12, eval_episodes=5, seed=50, randomize=False)
    assert result["training"]["train_seeds"] == tuple(range(50, 62))
    assert result["evaluation"]["seed_start"] == 62
    assert result["evaluation"]["seed_end"] == 66
    assert result["evaluation"]["learned_policy"]["success_rate"] >= 0.0
    assert result["evaluation"]["scripted_goal_following"]["success_rate"] >= 0.0


@pytest.mark.parametrize("size", [5, 6])
def test_learned_baseline_rejects_grid_sizes_that_cannot_fit_default_goal(size):
    with pytest.raises(ValueError, match="at least 7"):
        train_and_evaluate(train_episodes=1, eval_episodes=1, size=size)
