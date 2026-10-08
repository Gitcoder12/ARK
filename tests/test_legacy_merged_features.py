import numpy as np

from ark.adapters import Action, ModelAdapter, ModelMetadata
from ark.envs.grid_world import Action as GridAction
from ark.envs.grid_world import GridWorld
from ark.perturbations.legacy import ActionDelay, GoalDrift, ObservationNoise


class DummyAdapter(ModelAdapter):
    def reset(self, task_spec):
        pass

    def act(self, observation):
        return Action(0, [1.0])

    def name(self):
        return "dummy"

    def metadata(self):
        return ModelMetadata("dummy", "custom", "1", "test")


def test_goal_drift_preserves_old_goal_and_moves_goal():
    env = GridWorld(seed=1)
    env.reset(seed=1)
    old = env.intended_goal
    pert = GoalDrift(drift_step=0)
    shifted = pert.apply(env, 0)
    assert shifted.intended_goal != old
    assert shifted._original_goal == old
    assert shifted.grid[shifted.intended_goal] == 3


def test_observation_noise_changes_numeric_grid():
    env = GridWorld(seed=1)
    obs = env.reset(seed=1)
    noisy = ObservationNoise(std=0.5).apply_observation(obs, np.random.default_rng(1))
    assert noisy["grid"].shape == obs["grid"].shape
    assert not np.array_equal(noisy["grid"], obs["grid"])


def test_action_delay_buffers_actions():
    d = ActionDelay(delay=1)
    assert d.apply(int(GridAction.RIGHT)) == int(GridAction.STAY)
    assert d.apply(int(GridAction.DOWN)) == int(GridAction.RIGHT)


def test_adapter_fingerprint_is_stable():
    a = DummyAdapter()
    assert len(a.fingerprint()) == 16
