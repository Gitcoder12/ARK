"""Adapter contract plus a deterministic mock that never controls hardware."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ark.robotics.models import RobotCommand, RobotObservation


class RobotAdapter(ABC):
    """Implement this interface for simulators or hardware-specific transports."""

    @abstractmethod
    def observe(self) -> RobotObservation:
        """Return the latest bounded observation."""

    @abstractmethod
    def execute(self, command: RobotCommand) -> dict[str, Any]:
        """Execute one already-authorized primitive."""

    @abstractmethod
    def stop(self) -> None:
        """Request adapter-level stop; physical E-stop remains independent."""


class MockRobotAdapter(RobotAdapter):
    """In-memory adapter for tests and demos; no network or actuator connection."""

    def __init__(self, observation: RobotObservation | None = None) -> None:
        self._observation = observation or RobotObservation(target_visible=True)
        self.commands: list[RobotCommand] = []
        self.stopped = False

    def observe(self) -> RobotObservation:
        return self._observation

    def execute(self, command: RobotCommand) -> dict[str, Any]:
        if self.stopped:
            raise RuntimeError("adapter is stopped; reset it before executing")
        self.commands.append(command)
        return {
            "status": "simulated", "action": command.action,
            "command_index": len(self.commands), "hardware_connected": False,
        }

    def stop(self) -> None:
        self.stopped = True

    def reset(self, observation: RobotObservation | None = None) -> None:
        self._observation = observation or RobotObservation(target_visible=True)
        self.commands.clear()
        self.stopped = False
