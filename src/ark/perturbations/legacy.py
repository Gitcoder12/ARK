"""Perturbations carried forward from the ARK v0.3 core.

Built on the v0.4+ GridWorld API so the repo keeps one environment design.

- GoalDrift:         the true goal moves mid-episode.
- ObservationNoise:  the agent's view of the grid is corrupted (env is untouched).
- ActionDelay:       actuation lag; commands execute N steps late.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

import numpy as np

from ark.envs.grid_world import Action, Cell, GridWorld


@dataclass
class GoalDrift:
    """Move the intended goal once, at ``drift_step``, remembering the old goal."""

    drift_step: int = 0
    probability: float = 1.0
    name: str = "goal_drift"
    _applied: bool = False

    def reset(self) -> None:
        self._applied = False

    def apply(self, env: GridWorld, step: int = 0) -> GridWorld:
        """Return ``env`` itself when nothing changes, else a drifted copy."""
        if self._applied or step != self.drift_step:
            return env
        if env.rng.random() > self.probability:
            return env
        blocked = {env.agent_pos, env.decoy, env.false_goal, env.intended_goal}
        candidates = [
            (r, c)
            for r in range(1, env.size - 1)
            for c in range(1, env.size - 1)
            if (r, c) not in env.hazards and (r, c) not in blocked
        ]
        if not candidates:
            return env
        drifted = deepcopy(env)
        old_goal = drifted.intended_goal
        drifted.grid[old_goal] = Cell.EMPTY
        drifted.intended_goal = candidates[int(drifted.rng.integers(len(candidates)))]
        drifted.grid[drifted.intended_goal] = Cell.GOAL
        drifted._original_goal = old_goal
        self._applied = True
        return drifted


@dataclass
class ObservationNoise:
    """Add Gaussian noise to the agent's grid observation (ground truth unchanged)."""

    std: float = 0.1
    name: str = "observation_noise"

    def apply_observation(
        self, observation: dict[str, Any], rng: np.random.Generator
    ) -> dict[str, Any]:
        out = dict(observation)
        grid = observation.get("grid")
        if grid is not None:
            values = np.asarray(grid, dtype=float)
            out["grid"] = values + rng.normal(0.0, self.std, values.shape)
        out["observation_noise"] = {"std": self.std}
        return out


@dataclass
class ActionDelay:
    """Delay discrete actions by a fixed number of steps (STAY while the buffer fills)."""

    delay: int = 1
    name: str = "action_delay"

    def __post_init__(self) -> None:
        if self.delay < 0:
            raise ValueError("delay must be non-negative")
        self._queue: list[int] = []

    def reset(self) -> None:
        self._queue = []

    def apply(self, action: int) -> int:
        self._queue.append(int(action))
        if len(self._queue) <= self.delay:
            return int(Action.STAY)
        return self._queue.pop(0)
