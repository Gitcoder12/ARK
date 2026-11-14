"""Regression tests for agent/environment trust isolation."""

from ark.agents.baselines import BaseAgent
from ark.envs.grid_world import Action, Cell, GridWorld
from ark.evaluation.monitor import SafetyMonitor
from ark.experiments.runner import run_episode


class MutatingAgent(BaseAgent):
    """Agent that attempts to erase a hazard through its environment argument."""

    def act(self, obs, env=None):
        assert env is not None
        env.grid[1, 2] = Cell.EMPTY
        return int(Action.RIGHT)


def test_agent_cannot_mutate_the_environment_seen_by_monitor_and_step():
    env = GridWorld(
        size=5,
        start=(1, 1),
        goal=(3, 3),
        hazards=[(1, 2)],
        decoy=None,
        max_steps=1,
    )
    agent = MutatingAgent(seed=7)

    run_episode(env, agent, monitor=SafetyMonitor(), seed=7)

    assert env.grid[1, 2] == Cell.HAZARD
    assert env.hazard_hits == 0
    assert env.agent_pos != (1, 2)
