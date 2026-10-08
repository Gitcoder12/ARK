"""Agents that depend on an explicit memory buffer for goal information.

Used in Phase-2 experiments: when memory is corrupted the agent may
pursue a false goal or forget hazards, measuring adherence vs fidelity.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from ark.agents.baselines import BaseAgent, _action_toward, _bfs_path
from ark.envs.grid_world import Action, GridWorld
from ark.memory.buffer import AgentMemory


class MemoryAgent(BaseAgent):
    """Goal-following agent that reads the goal (and optional hazards)
    from its AgentMemory rather than from the live environment.

    If memory is intact → behaves like GoalFollowingAgent.
    If goal fact is missing/flipped → may fail or chase the wrong cell.
    """

    def __init__(
        self,
        memory: AgentMemory | None = None,
        seed: int | None = None,
        avoid_hazards: bool = True,
        fallback_to_env: bool = False,
    ):
        super().__init__(seed)
        self.memory = memory or AgentMemory()
        self.avoid_hazards = avoid_hazards
        self.fallback_to_env = fallback_to_env
        self.last_fidelity: float = 1.0
        self._ground_truth: dict[str, Any] = {}

    def seed_memory_from_env(self, env: GridWorld) -> None:
        """Write ground-truth facts at episode start."""
        self.memory.clear()
        self.memory.write("goal", env.intended_goal, step=0, trusted=True)
        self.memory.write("hazards", list(env.hazards), step=0, trusted=True)
        self.memory.write("start", env.start, step=0, trusted=True)
        if env.decoy is not None:
            self.memory.write("decoy", env.decoy, step=0, trusted=True)
            self.memory.write("decoy_is_goal", False, step=0, trusted=True)
        self._ground_truth = {
            "goal": env.intended_goal,
            "hazards": list(env.hazards),
        }

    def apply_corruption(self, corruption, rng: np.random.Generator | None = None) -> None:
        from ark.memory.corruption import apply_memory_corruption

        self.memory = apply_memory_corruption(self.memory, corruption, rng=rng)
        if self._ground_truth:
            self.last_fidelity = self.memory.fidelity(self._ground_truth)

    def act(self, obs: dict[str, Any], env: GridWorld | None = None) -> int:
        if env is None:
            return int(Action.STAY)

        goal = self.memory.read("goal")
        if goal is None:
            if self.fallback_to_env:
                goal = obs.get("intended_goal") or env.intended_goal
            else:
                # no goal in memory → stay (amnesia)
                return int(Action.STAY)

        # if memory claims decoy is the goal, chase decoy
        if self.memory.read("decoy_is_goal", default=False) and env.decoy is not None:
            goal = env.decoy

        hazards_safe = self.memory.read("hazards_safe", default=False)
        avoid = self.avoid_hazards and not hazards_safe

        pos = obs["position"]
        path = _bfs_path(env, pos, tuple(goal), avoid_hazards=avoid)
        if len(path) < 2 and avoid:
            path = _bfs_path(env, pos, tuple(goal), avoid_hazards=False)
        if len(path) < 2:
            return int(Action.STAY)
        return int(_action_toward(pos, path[1]))

    def reset(self) -> None:
        # keep memory across resets unless caller re-seeds
        pass

    def memory_fidelity(self) -> float:
        if not self._ground_truth:
            return 1.0
        return self.memory.fidelity(self._ground_truth)
