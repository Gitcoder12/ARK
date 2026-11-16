"""Tests for the learned-policy baseline and deterministic training protocol."""

from ark.agents.q_learning import QLearningAgent, train_q_learning
from ark.envs.grid_world import Action, GridWorld
from ark.experiments.runner import run_episode


def _env_factory(seed: int) -> GridWorld:
    return GridWorld(seed=seed, randomize=False)


def test_q_learning_agent_returns_a_valid_action():
    env = _env_factory(1)
    obs = env.reset(seed=1)
    agent = QLearningAgent(seed=1, epsilon=0.0)
    action = agent.act(obs, env)
    assert action in agent.valid_actions(obs, env)


def test_q_learning_update_changes_selected_action_value():
    env = _env_factory(1)
    obs = env.reset(seed=1)
    next_obs, reward, done, _ = env.step(int(Action.RIGHT))
    agent = QLearningAgent(seed=1, epsilon=0.0)
    updated = agent.update(obs, int(Action.RIGHT), reward, next_obs, done, env)
    state = agent.state_key(obs, env)
    assert agent.q_table[state][int(Action.RIGHT)] == updated
    assert updated != 0.0


def test_training_records_explicit_train_seeds_and_populates_q_table():
    train_seeds = tuple(range(10, 30))
    agent = QLearningAgent(seed=7, epsilon=1.0)
    summary = train_q_learning(
        agent,
        _env_factory,
        train_seeds,
        epsilon_decay=0.9,
        min_epsilon=0.1,
    )
    assert summary.train_seeds == train_seeds
    assert summary.episodes == len(train_seeds)
    assert agent.q_table
    assert summary.final_epsilon <= 1.0


def test_evaluation_uses_a_separate_seed_set():
    train_seeds = tuple(range(100, 120))
    evaluation_seeds = tuple(range(10_000, 10_005))
    assert set(train_seeds).isdisjoint(evaluation_seeds)

    agent = QLearningAgent(seed=3, epsilon=1.0)
    train_q_learning(agent, _env_factory, train_seeds)
    agent.epsilon = 0.0

    results = [
        run_episode(_env_factory(seed), agent, seed=seed)
        for seed in evaluation_seeds
    ]
    assert len(results) == len(evaluation_seeds)
    assert all(isinstance(result.success, bool) for result in results)


def test_training_rejects_empty_seed_list():
    agent = QLearningAgent(seed=1)
    try:
        train_q_learning(agent, _env_factory, [])
    except ValueError as exc:
        assert "train_seeds" in str(exc)
    else:
        raise AssertionError("Expected empty training seeds to be rejected")


def test_state_key_includes_remaining_episode_horizon():
    env = _env_factory(1)
    obs = env.reset(seed=1)
    near_start = QLearningAgent.state_key(obs, env)
    later_obs = dict(obs)
    later_obs["steps"] = env.max_steps - 1
    near_timeout = QLearningAgent.state_key(later_obs, env)
    assert near_start != near_timeout
