"""Tabular Q-learning baseline for ARK's partially observed grid-world tasks.

This is a small, model-free research baseline, not a production agent. Its
state abstraction includes the agent position, observed goal/decoy coordinates,
and the four adjacent cell types. It can generalize local action preferences
across layouts, but it does not encode the full map or provide a guarantee of
optimal planning.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

import numpy as np

from ark.agents.baselines import BaseAgent
from ark.envs.grid_world import Action, Cell, GridWorld

State = tuple[int, ...]
_ACTION_DELTAS: dict[Action, tuple[int, int]] = {
    Action.UP: (-1, 0),
    Action.DOWN: (1, 0),
    Action.LEFT: (0, -1),
    Action.RIGHT: (0, 1),
}


@dataclass(frozen=True)
class QLearningTrainingSummary:
    """Compact, reproducible summary of a training run."""

    train_seeds: tuple[int, ...]
    episodes: int
    success_rate: float
    mean_return: float
    final_epsilon: float


class QLearningAgent(BaseAgent):
    """Tabular Q-learning agent using a compact local-observation state.

    Training is explicit through :func:`train_q_learning`. During evaluation,
    set `epsilon=0.0` to disable exploratory actions.
    """

    def __init__(
        self,
        *,
        alpha: float = 0.15,
        gamma: float = 0.95,
        epsilon: float = 1.0,
        seed: int | None = None,
    ) -> None:
        super().__init__(seed=seed)
        if not 0.0 < alpha <= 1.0:
            raise ValueError("alpha must be in (0, 1]")
        if not 0.0 <= gamma <= 1.0:
            raise ValueError("gamma must be in [0, 1]")
        if not 0.0 <= epsilon <= 1.0:
            raise ValueError("epsilon must be in [0, 1]")
        self.alpha = float(alpha)
        self.gamma = float(gamma)
        self.epsilon = float(epsilon)
        self.q_table: dict[State, np.ndarray] = {}

    @staticmethod
    def state_key(obs: dict, env: GridWorld) -> State:
        """Encode position, objective and adjacent observed cell types."""
        position = tuple(int(value) for value in obs["position"])
        if len(position) != 2:
            raise ValueError("observation position must contain row and column")

        raw_grid = obs.get("grid", env.grid)
        grid = np.asarray(raw_grid)
        if grid.shape != (env.size, env.size):
            raise ValueError(
                f"observation grid must have shape {(env.size, env.size)}, "
                f"got {grid.shape}"
            )
        grid = np.clip(np.rint(grid.astype(float)), 0, int(Cell.DECOY)).astype(np.int8)

        goal = obs.get("intended_goal") or env.intended_goal
        goal = tuple(int(value) for value in goal)
        decoy = obs.get("decoy", env.decoy)
        decoy_key = (-1, -1) if decoy is None else tuple(int(value) for value in decoy)

        adjacent: list[int] = []
        row, column = position
        for action in (Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT):
            delta_row, delta_column = _ACTION_DELTAS[action]
            next_row, next_column = row + delta_row, column + delta_column
            if not (0 <= next_row < env.size and 0 <= next_column < env.size):
                adjacent.append(int(Cell.WALL))
            else:
                adjacent.append(int(grid[next_row, next_column]))

        steps_elapsed = int(obs.get("steps", 0))
        steps_remaining = max(0, int(env.max_steps) - steps_elapsed)

        return (
            position[0],
            position[1],
            goal[0],
            goal[1],
            decoy_key[0],
            decoy_key[1],
            steps_remaining,
            *adjacent,
        )

    @staticmethod
    def valid_actions(obs: dict, env: GridWorld) -> list[int]:
        """Return actions that do not enter a wall according to the observation."""
        row, column = (int(value) for value in obs["position"])
        raw_grid = obs.get("grid", env.grid)
        grid = np.asarray(raw_grid)
        if grid.shape != (env.size, env.size):
            raise ValueError(f"observation grid must have shape {(env.size, env.size)}")

        actions = [int(Action.STAY)]
        for action, (delta_row, delta_column) in _ACTION_DELTAS.items():
            next_row, next_column = row + delta_row, column + delta_column
            if not (0 <= next_row < env.size and 0 <= next_column < env.size):
                continue
            cell = int(np.clip(round(float(grid[next_row, next_column])), 0, int(Cell.DECOY)))
            if cell != int(Cell.WALL):
                actions.append(int(action))
        return actions

    def _values(self, state: State) -> np.ndarray:
        if state not in self.q_table:
            self.q_table[state] = np.zeros(len(Action), dtype=np.float64)
        return self.q_table[state]

    def act(self, obs: dict, env: GridWorld | None = None) -> int:
        if env is None:
            return int(Action.STAY)

        state = self.state_key(obs, env)
        valid = self.valid_actions(obs, env)
        if self.rng.random() < self.epsilon:
            return int(self.rng.choice(valid))

        values = self._values(state)
        best_value = max(float(values[action]) for action in valid)
        best_actions = [action for action in valid if np.isclose(values[action], best_value)]
        return int(self.rng.choice(best_actions))

    def update(
        self,
        obs: dict,
        action: int,
        reward: float,
        next_obs: dict,
        done: bool,
        env: GridWorld,
    ) -> float:
        """Apply one Q-learning update and return the new Q(s, a)."""
        action_value = int(Action(action))
        state = self.state_key(obs, env)
        values = self._values(state)
        old_value = float(values[action_value])

        if done:
            target = float(reward)
        else:
            next_state = self.state_key(next_obs, env)
            next_values = self._values(next_state)
            next_actions = self.valid_actions(next_obs, env)
            target = float(reward) + self.gamma * max(
                float(next_values[next_action]) for next_action in next_actions
            )

        values[action_value] = old_value + self.alpha * (target - old_value)
        return float(values[action_value])


def train_q_learning(
    agent: QLearningAgent,
    env_factory: Callable[[int], GridWorld],
    train_seeds: Iterable[int],
    *,
    epsilon_decay: float = 0.995,
    min_epsilon: float = 0.05,
    max_steps: int | None = None,
) -> QLearningTrainingSummary:
    """Train on the supplied seeds and return a reproducible training summary.

    The caller is responsible for keeping evaluation seeds disjoint from
    `train_seeds`. The factory receives the episode seed; the environment is
    also reset with that seed so randomized layouts are reproducible.
    """
    seeds = tuple(int(seed) for seed in train_seeds)
    if not seeds:
        raise ValueError("train_seeds must contain at least one seed")
    if not 0.0 < epsilon_decay <= 1.0:
        raise ValueError("epsilon_decay must be in (0, 1]")
    if not 0.0 <= min_epsilon <= 1.0:
        raise ValueError("min_epsilon must be in [0, 1]")

    successes: list[bool] = []
    returns: list[float] = []

    for seed in seeds:
        env = env_factory(seed)
        obs = env.reset(seed=seed)
        episode_return = 0.0
        steps_limit = env.max_steps if max_steps is None else max_steps
        if steps_limit <= 0:
            raise ValueError("max_steps must be positive")

        for _ in range(steps_limit):
            action = agent.act(obs, env)
            next_obs, reward, done, _info = env.step(action)
            agent.update(obs, action, reward, next_obs, done, env)
            episode_return += float(reward)
            obs = next_obs
            if done:
                break

        successes.append(env.agent_pos == env.intended_goal)
        returns.append(episode_return)
        agent.epsilon = max(min_epsilon, agent.epsilon * epsilon_decay)

    return QLearningTrainingSummary(
        train_seeds=seeds,
        episodes=len(seeds),
        success_rate=float(np.mean(successes)),
        mean_return=float(np.mean(returns)),
        final_epsilon=float(agent.epsilon),
    )
