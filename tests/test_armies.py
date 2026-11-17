"""Tests for ARK's squad composition and deterministic power-ups."""

import numpy as np
import pytest

from ark.agents.baselines import BaseAgent, GoalFollowingAgent
from ark.armies import Army, PowerUp, default_armies, run_army_benchmark
from ark.envs.grid_world import Action, GridWorld
from ark.experiments.runner import Condition


class FixedAgent(BaseAgent):
    def __init__(self, action: int, seed: int = 0):
        super().__init__(seed)
        self.action = action
        self.last_grid = None
        self.last_goal = None

    def act(self, obs, env=None):
        self.last_grid = np.asarray(obs["grid"]).copy()
        self.last_goal = obs.get("intended_goal")
        return self.action


def test_army_requires_name_and_members():
    with pytest.raises(ValueError, match="name"):
        Army("", [GoalFollowingAgent()])
    with pytest.raises(ValueError, match="at least one"):
        Army("Empty", [])


def test_army_rejects_unknown_powerup():
    with pytest.raises(ValueError, match="unknown power-up"):
        Army("Invalid", [GoalFollowingAgent()], ["teleport"])


def test_majority_vote_selects_most_common_action():
    army = Army(
        "Majority",
        [
            FixedAgent(int(Action.RIGHT)),
            FixedAgent(int(Action.RIGHT)),
            FixedAgent(int(Action.UP)),
        ],
    )
    env = GridWorld(seed=0)
    observation = env.reset()
    assert army.act(observation, env) == int(Action.RIGHT)


def test_tied_vote_uses_first_member_as_deterministic_tiebreak():
    army = Army(
        "Tie",
        [FixedAgent(int(Action.LEFT)), FixedAgent(int(Action.UP))],
    )
    env = GridWorld(seed=0)
    observation = env.reset()
    assert army.act(observation, env) == int(Action.LEFT)


def test_scout_replaces_noisy_grid_and_goal_with_simulator_truth():
    member = FixedAgent(int(Action.STAY))
    army = Army("Scout", [member], [PowerUp.SCOUT])
    env = GridWorld(seed=0)
    observation = env.reset()
    observation["grid"] = np.zeros_like(env.grid)
    observation["intended_goal"] = (1, 1)

    army.act(observation, env)

    assert np.array_equal(member.last_grid, env.grid)
    assert member.last_goal == env.intended_goal


def test_shield_blocks_one_hazard_directed_action_per_episode():
    army = Army("Shield", [FixedAgent(int(Action.RIGHT))], [PowerUp.SHIELD])
    env = GridWorld(
        size=5,
        start=(1, 1),
        goal=(1, 3),
        hazards=[(1, 2)],
        decoy=None,
        max_steps=10,
    )
    observation = env.reset()

    assert army.act(observation, env) == int(Action.STAY)
    assert army.shield_uses == 1
    assert army.act(observation, env) == int(Action.RIGHT)
    assert army.shield_uses == 1


def test_boost_adds_bounded_twenty_five_percent_step_budget():
    env = GridWorld(max_steps=50)
    boosted = Army("Boost", [GoalFollowingAgent()], [PowerUp.BOOST])
    normal = Army("Normal", [GoalFollowingAgent()])

    assert normal.step_limit(env) == 50
    assert boosted.step_limit(env) == 63


def test_reseed_resets_powerup_charges():
    army = Army("Shield", [FixedAgent(int(Action.RIGHT))], [PowerUp.SHIELD])
    env = GridWorld(
        size=5,
        start=(1, 1),
        goal=(1, 3),
        hazards=[(1, 2)],
        decoy=None,
        max_steps=10,
    )
    army.act(env.reset(), env)
    assert army.shield_uses == 1

    army.reseed(123)
    assert army.shield_uses == 0


def test_battle_benchmark_is_reproducible_and_reports_powerups():
    armies = default_armies(seed=4)[:1]
    kwargs = {
        "n_episodes": 2,
        "seed": 9,
        "conditions": (Condition("clean"),),
    }
    first = run_army_benchmark(armies, **kwargs)
    second = run_army_benchmark(armies, **kwargs)

    assert first == second
    assert first[0].army == "Sentinels"
    assert first[0].metrics["n_episodes"] == 2.0
    assert set(first[0].powerups) == {"boost", "scout", "shield"}
    assert 0.0 <= first[0].score <= 100.0


def test_battle_benchmark_rejects_empty_armies_and_zero_episodes():
    with pytest.raises(ValueError, match="at least one army"):
        run_army_benchmark([], n_episodes=1)
    with pytest.raises(ValueError, match="n_episodes"):
        run_army_benchmark(default_armies()[:1], n_episodes=0)



def test_boost_changes_the_actual_gridworld_episode_budget():
    from ark.armies import run_army_benchmark

    agent = FixedAgent(int(Action.STAY))
    army = Army("Boosted", [agent], [PowerUp.BOOST])
    result = run_army_benchmark(
        [army],
        n_episodes=1,
        seed=3,
        use_monitor=False,
        conditions=(Condition("clean"),),
    )[0]

    # The episode reaches the 25% extended budget rather than stopping at
    # GridWorld's original max_steps (50).
    assert result.metrics["mean_steps"] == 63.0
