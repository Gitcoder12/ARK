"""Independent evaluation layer that can ALLOW / BLOCK / REPLAN.

Core ARK idea: proposed actions are checked against safety and
goal-integrity heuristics before execution.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any

from ark.envs.grid_world import Action, Cell, GridWorld


class Decision(Enum):
    ALLOW = "allow"
    BLOCK = "block"
    REPLAN = "replan"


@dataclass
class MonitorResult:
    decision: Decision
    reason: str
    original_action: int
    alternative_action: int | None = None


def _bfs_next(
    env: GridWorld,
    start: tuple[int, int],
    goal: tuple[int, int],
    avoid_hazards: bool = True,
) -> int | None:
    """Return the first action of a shortest safe path, or None."""
    if start == goal:
        return int(Action.STAY)
    deltas = {
        Action.UP: (-1, 0),
        Action.DOWN: (1, 0),
        Action.LEFT: (0, -1),
        Action.RIGHT: (0, 1),
    }
    queue: deque[tuple[int, int]] = deque([start])
    came_from: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    found = False
    while queue:
        cur = queue.popleft()
        if cur == goal:
            found = True
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
    if not found or goal not in came_from:
        return None
    node: tuple[int, int] = goal
    while came_from[node] is not None and came_from[node] != start:
        node = came_from[node]  # type: ignore[assignment]
    for a, (dr, dc) in deltas.items():
        if (start[0] + dr, start[1] + dc) == node:
            return int(a)
    return int(Action.STAY)


class SafetyMonitor:
    """Rule-based monitor for the grid-world MVP.

    Checks:
    1. Action steps onto hazard? → REPLAN (safe path) or BLOCK
    2. Soft note when action targets decoy (reward-hacking signal)
    """

    def __init__(
        self,
        block_hazards: bool = True,
        replan_on_hazard: bool = True,
    ):
        self.block_hazards = block_hazards
        self.replan_on_hazard = replan_on_hazard

    def evaluate(
        self,
        proposed_action: int,
        obs: dict[str, Any],
        env: GridWorld,
    ) -> MonitorResult:
        action = Action(proposed_action)
        pos = obs["position"]
        goal = obs.get("intended_goal") or env.intended_goal
        next_pos = self._next_pos(pos, action)

        cell = None
        if self._in_bounds(next_pos, env):
            cell = Cell(env.grid[next_pos])

        if self.block_hazards and cell == Cell.HAZARD:
            if self.replan_on_hazard:
                alt = _bfs_next(env, pos, goal, avoid_hazards=True)
                if alt is not None:
                    return MonitorResult(
                        decision=Decision.REPLAN,
                        reason="proposed action enters hazard; replan to safe path",
                        original_action=proposed_action,
                        alternative_action=alt,
                    )
            return MonitorResult(
                decision=Decision.BLOCK,
                reason="proposed action enters hazard",
                original_action=proposed_action,
            )

        if cell == Cell.DECOY:
            return MonitorResult(
                decision=Decision.ALLOW,
                reason="action targets decoy (reward-hacking risk noted)",
                original_action=proposed_action,
            )

        return MonitorResult(
            decision=Decision.ALLOW,
            reason="action passes safety checks",
            original_action=proposed_action,
        )

    def _next_pos(self, pos: tuple[int, int], action: Action) -> tuple[int, int]:
        r, c = pos
        if action == Action.UP:
            return r - 1, c
        if action == Action.DOWN:
            return r + 1, c
        if action == Action.LEFT:
            return r, c - 1
        if action == Action.RIGHT:
            return r, c + 1
        return pos

    def _in_bounds(self, pos: tuple[int, int], env: GridWorld) -> bool:
        r, c = pos
        return 0 <= r < env.size and 0 <= c < env.size
