from ark.agents.baseline_agent import train_and_evaluate


def test_learned_baseline_evaluates_on_unseen_seed_range():
    result = train_and_evaluate(train_episodes=12, eval_episodes=5, seed=50, randomize=False)
    assert result["training"]["train_seeds"] == tuple(range(50, 62))
    assert result["evaluation"]["seed_start"] == 62
    assert result["evaluation"]["seed_end"] == 66
    assert 0.0 <= result["evaluation"]["success_rate"] <= 1.0
