"""Deterministic pre-execution checks for robot commands."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from ark.robotics.models import RobotCommand, RobotObservation, SafetyDecision


@dataclass(frozen=True)
class SafetyPolicy:
    allowed_actions: frozenset[str] = frozenset({"move", "grasp", "release", "wait"})
    max_velocity: float = 0.25
    max_force: float = 10.0
    max_duration: float = 2.0
    workspace_bounds: dict[str, tuple[float, float]] = field(
        default_factory=lambda: {
            "x": (-0.5, 0.5), "y": (-0.5, 0.5), "z": (0.0, 0.6),
        }
    )
    require_human_approval: bool = True
    max_actions_per_episode: int = 100

    def __post_init__(self) -> None:
        limits = (self.max_velocity, self.max_force, self.max_duration)
        if any(not math.isfinite(value) or value <= 0 for value in limits):
            raise ValueError("robot limits must be finite and positive")
        if self.max_actions_per_episode < 1:
            raise ValueError("max_actions_per_episode must be positive")
        for axis, bounds in self.workspace_bounds.items():
            if (
                len(bounds) != 2
                or not all(math.isfinite(value) for value in bounds)
                or bounds[0] > bounds[1]
            ):
                raise ValueError(f"invalid workspace bounds for {axis}")

    def evaluate(
        self,
        command: RobotCommand,
        observation: RobotObservation,
        *,
        actions_executed: int = 0,
        approved: bool = False,
    ) -> SafetyDecision:
        """Fail closed when any command or environment constraint is invalid."""
        checks = {
            "known_action": command.action in self.allowed_actions,
            "emergency_stop_clear": not observation.emergency_stop,
            "velocity_within_limit": self._bounded(command.velocity, 0.0, self.max_velocity),
            "force_within_limit": self._bounded(command.force, 0.0, self.max_force),
            "duration_within_limit": self._bounded(command.duration, 0.0, self.max_duration),
            "episode_budget_available": actions_executed < self.max_actions_per_episode,
            "target_within_workspace": self._target_is_safe(command.action, command.target),
            "grasp_target_visible": command.action != "grasp" or observation.target_visible,
        }
        failed = [name for name, passed in checks.items() if not passed]
        if failed:
            return SafetyDecision(False, "Blocked: " + ", ".join(failed), checks=checks)
        if self.require_human_approval and not approved:
            return SafetyDecision(
                False, "Human approval required before execution.",
                requires_approval=True, checks=checks,
            )
        return SafetyDecision(True, "All configured safety checks passed.", checks=checks)

    @staticmethod
    def _bounded(value: float, minimum: float, maximum: float) -> bool:
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
            and minimum <= value <= maximum
        )

    def _target_is_safe(self, action: str, target: dict[str, float]) -> bool:
        if action == "move" and not {"x", "y", "z"} <= set(target):
            return False
        for axis, value in target.items():
            if axis not in self.workspace_bounds or not self._bounded(
                value, *self.workspace_bounds[axis]
            ):
                return False
        return True
