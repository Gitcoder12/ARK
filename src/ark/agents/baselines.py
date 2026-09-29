"""Baseline agents for ARK controlled experiments.

Deliberately simple so differences under perturbation are attributable
to objective / reward / constraint changes rather than complex learning.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from typing import Any

import numpy as np

from ark.envs.grid_world import Action, Cell, GridWorld


class BaseAgent(ABC):
    """Agent interface: propose an action given observation."""

    def __init__(self, seed: int | None = None):
        self.rng = np.random.default_rng(seed)

    @abstractmethod
    def act(self, obs: dict[str, Any], env: GridWorld | None = None) -> int:
        ...

    def reset(self) -> None:
        pass


def _bfs_path(
    env: GridWorld,
    start: tuple[int, int],
    goal: tuple[int, int],
    avoid_hazards: bool = False,
) -> list[tuple[int, int]]:
    """Shortest path (BFS). Returns list of positions from start to goal inclusive."""
    if start == goal:
        return [start]
    queue: deque[tuple[int, int]] = deque([start])
    came_from: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    while queue:
        cur = queue.popleft()
        if cur == goal:
            break
        r, c = cur
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            nxt = (nr, nc)
            if not (0 <= nr < env.size and 0 <= nc < env.size):
                continue
            cell = Cell(env.grid[nr, nc])
            if cell == Cell.WALL:
                continue
            if avoid_hazards and cell == Cell.HAZARD:
                continue
            if nxt not in came_from:
                came_from[nxt] = cur
                queue.append(nxt)
    if goal not in came_from:
        return []
    path: list[tuple[int, int]] = []
    node: tuple[int, int] | None = goal
    while node is not None:
        path.append(node)
        node = came_from[node]
    path.reverse()
    return path


def _action_toward(pos: tuple[int, int], nxt: tuple[int, int]) -> Action:
    r, c = pos
    nr, nc = nxt
    if nr < r:
        return Action.UP
    if nr > r:
        return Action.DOWN
    if nc < c:
        return Action.LEFT
    if nc > c:
        return Action.RIGHT
    return Action.STAY


class RandomAgent(BaseAgent):
    def act(self, obs: dict[str, Any], env: GridWorld | None = None) -> int:
        if env is not None:
            return int(self.rng.choice(env.valid_actions(obs["position"])))
        return int(self.rng.integers(0, 5))


class GoalFollowingAgent(BaseAgent):
    """Moves toward the *intended* goal via shortest path (ignores reward/decoy).

    Does **not** avoid hazards by default — that is the job of the
    SafetyConstrainedAgent or the external monitor.
    """

    def __init__(self, goal: tuple[int, int] | None = None, seed: int | None = None):
        super().__init__(seed)
        self.goal = goal

    def act(self, obs: dict[str, Any], env: GridWorld | None = None) -> int:
        if env is None:
            return int(Action.STAY)
        goal = self.goal or obs.get("intended_goal") or env.intended_goal
        pos = obs["position"]
        path = _bfs_path(env, pos, goal, avoid_hazards=False)
        if len(path) < 2:
            return int(Action.STAY)
        return int(_action_toward(pos, path[1]))


class SafetyConstrainedAgent(BaseAgent):
    """Goal-following that plans around hazards (hard constraint)."""

    def __init__(self, goal: tuple[int, int] | None = None, seed: int | None = None):
        super().__init__(seed)
        self.goal = goal

    def act(self, obs: dict[str, Any], env: GridWorld | None = None) -> int:
        if env is None:
            return int(Action.STAY)
        goal = self.goal or obs.get("intended_goal") or env.intended_goal
        pos = obs["position"]
        path = _bfs_path(env, pos, goal, avoid_hazards=True)
        if len(path) < 2:
            path = _bfs_path(env, pos, goal, avoid_hazards=False)
        if len(path) < 2:
            return int(Action.STAY)
        return int(_action_toward(pos, path[1]))


class RewardMaximizingAgent(BaseAgent):
    """Plans toward highest-value target (goal vs decoy) under current rewards.

    Makes reward-conflict perturbations clearly visible.
    """

    def __init__(self, seed: int | None = None, horizon: int = 30):
        super().__init__(seed)
        self.horizon = horizon

    def act(self, obs: dict[str, Any], env: GridWorld | None = None) -> int:
        if env is None:
            return int(Action.STAY)
        pos = obs["position"]
        candidates: list[tuple[float, list[tuple[int, int]]]] = []

        path_g = _bfs_path(env, pos, env.intended_goal, avoid_hazards=False)
        if path_g:
            candidates.append((self._path_value(env, path_g), path_g))

        if env.decoy is not None:
            path_d = _bfs_path(env, pos, env.decoy, avoid_hazards=False)
            if path_d:
                candidates.append((self._path_value(env, path_d), path_d))

        if not candidates:
            return int(Action.STAY)

        candidates.sort(key=lambda x: x[0], reverse=True)
        best_path = candidates[0][1]
        if len(best_path) < 2:
            return int(Action.STAY)
        return int(_action_toward(pos, best_path[1]))

    def _path_value(self, env: GridWorld, path: list[tuple[int, int]]) -> float:
        total = 0.0
        for i, cell_pos in enumerate(path[1:], start=1):
            total += env.step_penalty
            cell = Cell(env.grid[cell_pos])
            if cell == Cell.GOAL:
                total += env.goal_reward
                break
            if cell == Cell.DECOY:
                total += env.decoy_reward
                break
            if cell == Cell.HAZARD:
                total += env.hazard_penalty
            if i >= self.horizon:
                break
        return total
