"""Small, serializable contracts shared by robotics adapters and the safety layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RobotObservation:
    """A bounded snapshot supplied by a simulator or robot adapter."""

    sensors: dict[str, float] = field(default_factory=dict)
    target_visible: bool = False
    emergency_stop: bool = False
    workspace: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RobotCommand:
    """A proposed primitive action; it is not executable until supervised."""

    action: str
    target: dict[str, float] = field(default_factory=dict)
    velocity: float = 0.0
    force: float = 0.0
    duration: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SafetyDecision:
    allowed: bool
    reason: str
    requires_approval: bool = False
    checks: dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "requires_approval": self.requires_approval,
            "checks": dict(self.checks),
        }
