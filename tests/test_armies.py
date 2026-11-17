"""Tests for ARK's squad composition and deterministic power-ups."""

import numpy as np
import pytest

from ark.agents.baselines import BaseAgent, GoalFollowingAgent
from ark.armies import Army, PowerUp, default_armies, run_army_benchmark
from ark.envs.grid_world import Action, Cell, GridWorld
from ark.experiments.runner import Condition
from ark.perturbations.legacy import GoalDrift


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



def test_army_members_receive_isolated_observations():
    class MutatingAgent(FixedAgent):
        def act(self, obs, env=None):
            obs["grid"][1, 1] = 99
            return int(Action.STAY)

    observer = FixedAgent(int(Action.STAY))
    army = Army("Isolated", [MutatingAgent(int(Action.STAY)), observer])
    env = GridWorld(seed=0)
    observation = env.reset()
    expected_grid = env.grid.copy()

    army.act(observation, env)

    assert np.array_equal(observer.last_grid, expected_grid)


def test_army_reseeds_and_resets_stateful_members():
    class StatefulAgent(FixedAgent):
        def __init__(self):
            super().__init__(int(Action.STAY))
            self.reset_count = 0

        def reset(self):
            self.reset_count += 1

    member = StatefulAgent()
    army = Army("Resettable", [member])
    initial_count = member.reset_count

    army.reseed(12)

    assert member.reset_count == initial_count + 1


def test_army_rejects_boolean_action_proposals():
    army = Army("InvalidProposal", [FixedAgent(True)])
    env = GridWorld(seed=0)
    observation = env.reset()

    assert army.act(observation, env) == int(Action.STAY)


def test_non_scout_members_cannot_read_true_goal_from_environment():
    class EnvironmentGoalAgent(FixedAgent):
        def __init__(self):
            super().__init__(int(Action.STAY))
            self.environment_goal = None

        def act(self, obs, env=None):
            self.environment_goal = env.intended_goal
            return int(Action.STAY)

    member = EnvironmentGoalAgent()
    army = Army("NoLeak", [member])
    env = GridWorld(seed=0)
    observation = env.reset()
    observation["intended_goal"] = (2, 5)

    army.act(observation, env)

    assert member.environment_goal == (2, 5)
    assert member.environment_goal != env.intended_goal


def test_scout_members_receive_true_goal_in_observation_and_environment():
    class EnvironmentGoalAgent(FixedAgent):
        def __init__(self):
            super().__init__(int(Action.STAY))
            self.environment_goal = None

        def act(self, obs, env=None):
            self.environment_goal = env.intended_goal
            self.last_goal = obs.get("intended_goal")
            return int(Action.STAY)

    member = EnvironmentGoalAgent()
    army = Army("Scout", [member], [PowerUp.SCOUT])
    env = GridWorld(seed=0)
    observation = env.reset()
    observation["intended_goal"] = (2, 5)

    army.act(observation, env)

    assert member.environment_goal == env.intended_goal
    assert member.last_goal == env.intended_goal


def test_army_score_does_not_double_count_goal_success():
    from ark.armies import _score

    metrics = {
        "success_rate": 1.0,
        "intended_goal_adherence": 1.0,
        "hazard_violation_rate": 0.0,
    }
    assert _score(metrics) == 100.0

    metrics["intended_goal_adherence"] = 0.0
    assert _score(metrics) == 100.0



def test_non_scout_false_goal_masks_true_goal_from_map_and_environment():
    class EnvironmentGoalAgent(FixedAgent):
        def __init__(self):
            super().__init__(int(Action.STAY))
            self.environment_goal = None
            self.environment_grid = None

        def act(self, obs, env=None):
            self.environment_goal = env.intended_goal
            self.environment_grid = env.grid.copy()
            self.last_grid = np.asarray(obs["grid"]).copy()
            return int(Action.STAY)

    member = EnvironmentGoalAgent()
    army = Army("FalseGoal", [member])
    env = GridWorld(seed=0)
    observation = env.reset()
    false_goal = (2, 5)
    observation["intended_goal"] = false_goal

    army.act(observation, env)

    assert member.environment_goal == false_goal
    assert member.environment_grid[env.intended_goal] == 0
    assert member.environment_grid[false_goal] == 3
    assert member.last_grid[env.intended_goal] == 0
    assert member.last_grid[false_goal] == 3



def test_non_scout_environment_snapshot_matches_noisy_observation():
    class EnvironmentSnapshotAgent(FixedAgent):
        def __init__(self):
            super().__init__(int(Action.STAY))
            self.environment_grid = None
            self.environment_hazards = None

        def act(self, obs, env=None):
            self.last_grid = np.asarray(obs["grid"]).copy()
            self.environment_grid = env.grid.copy()
            self.environment_hazards = tuple(env.hazards)
            return int(Action.STAY)

    env = GridWorld(seed=11)
    observation = env.reset()
    noisy_grid = np.zeros_like(env.grid, dtype=float)
    noisy_grid[0, :] = 1.0
    noisy_grid[-1, :] = 1.0
    noisy_grid[:, 0] = 1.0
    noisy_grid[:, -1] = 1.0
    noisy_grid[2, 2] = 2.8
    observation["grid"] = noisy_grid
    observation["observation_noise"] = {"std": 0.7}
    expected = np.clip(np.rint(noisy_grid), 0, int(Cell.DECOY)).astype(int)

    member = EnvironmentSnapshotAgent()
    army = Army("Noisy Scouts", [member])
    original_grid = env.grid.copy()

    army.act(observation, env)

    assert np.array_equal(member.last_grid, expected)
    assert np.array_equal(member.environment_grid, expected)
    assert member.environment_hazards == ((2, 2),)
    assert np.array_equal(env.grid, original_grid)


def test_non_scout_snapshot_hides_goal_drift_history_and_false_goal_leaks():
    class EnvironmentSnapshotAgent(FixedAgent):
        def __init__(self):
            super().__init__(int(Action.STAY))
            self.environment_goal = None
            self.original_goal = "not-cleared"
            self.environment_grid = None

        def act(self, obs, env=None):
            self.environment_goal = env.intended_goal
            self.original_goal = env._original_goal
            self.environment_grid = env.grid.copy()
            self.last_grid = np.asarray(obs["grid"]).copy()
            return int(Action.STAY)

    env = GridWorld(seed=5)
    env.reset(seed=5)
    drift = GoalDrift(drift_step=0)
    drifted = drift.apply(env, step=0)
    previous_goal = drifted._original_goal
    assert previous_goal is not None

    false_goal = (2, 5)
    observation = drifted.reset(seed=5)
    observation["intended_goal"] = false_goal

    member = EnvironmentSnapshotAgent()
    army = Army("False Goal Guard", [member])

    army.act(observation, drifted)

    assert member.environment_goal == false_goal
    assert member.original_goal is None
    assert member.environment_grid[drifted.intended_goal] == int(Cell.EMPTY)
    assert member.environment_grid[false_goal] == int(Cell.GOAL)
    assert member.environment_grid[previous_goal] != int(Cell.GOAL)
