"""Tests for the grid-world environment."""

from ark.envs.grid_world import Action, GridWorld


def test_reset_and_step():
    env = GridWorld(seed=0)
    obs = env.reset()
    assert obs["position"] == env.start
    assert not obs["done"]
    obs, reward, done, info = env.step(Action.RIGHT)
    assert isinstance(reward, float)
    assert obs["steps"] == 1


def test_goal_terminates():
    env = GridWorld(size=5, start=(1, 1), goal=(1, 2), hazards=[], decoy=None, max_steps=10)
    env.reset()
    obs, reward, done, info = env.step(Action.RIGHT)
    assert done
    assert env.agent_pos == (1, 2)
    assert reward > 0


def test_hazard_penalty():
    env = GridWorld(size=5, start=(1, 1), goal=(3, 3), hazards=[(1, 2)], decoy=None, max_steps=10)
    env.reset()
    obs, reward, done, info = env.step(Action.RIGHT)
    assert env.hazard_hits == 1
    assert reward < 0


def test_render():
    env = GridWorld(seed=1)
    env.reset()
    s = env.render_ascii()
    assert "A" in s
    assert "G" in s


def test_randomized_layout_is_reproducible_and_solvable():
    first = GridWorld(seed=3, randomize=True)
    second = GridWorld(seed=3, randomize=True)
    first.reset(seed=3)
    second.reset(seed=3)
    assert first.hazards == second.hazards
    assert first._safe_path_exists(first.hazards)


def test_randomized_layouts_vary_across_seeds_and_keep_fixed_cells_clear():
    layouts = set()
    for seed in range(20):
        env = GridWorld(seed=seed, randomize=True)
        env.reset(seed=seed)
        layouts.add(tuple(sorted(env.hazards)))
        assert env.start not in env.hazards
        assert env.intended_goal not in env.hazards
        assert env.decoy not in env.hazards
        assert len(env.hazards) == 3
    assert len(layouts) > 5
