"""Stable adapter interface for models under evaluation by ARK."""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class AdapterAction:
    raw: Any
    normalized: list[float]
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelMetadata:
    name: str
    type: str
    version: str
    provider: str
    parameters: dict[str, Any] = field(default_factory=dict)
    capabilities: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)


class ModelAdapter(ABC):
    """Interface for LLM, RL, multi-agent, robotics, or custom systems."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._episode_count = 0
        self._step_count = 0
        self._action_history: list[AdapterAction] = []
        self._observation_history: list[Any] = []

    @abstractmethod
    def reset(self, task_spec: dict[str, Any]) -> None: ...

    @abstractmethod
    def act(self, observation: Any) -> AdapterAction: ...

    @abstractmethod
    def name(self) -> str: ...

    def metadata(self) -> ModelMetadata:
        return ModelMetadata(self.name(), "unknown", "0.0.0", "unknown")

    def replan(self, observation: Any, reason: str = "") -> AdapterAction:
        return self.act(observation)

    def shutdown(self) -> None:  # noqa: B027  (optional hook)
        pass

    def fingerprint(self) -> str:
        payload = {"name": self.name(), "config": self.config, "metadata": self.metadata().__dict__}
        blob = json.dumps(payload, sort_keys=True, default=str).encode()
        return hashlib.sha256(blob).hexdigest()[:16]

    def history(self) -> dict[str, Any]:
        return {
            "actions": [a.__dict__ for a in self._action_history],
            "observations": self._observation_history,
            "episode_count": self._episode_count,
            "step_count": self._step_count,
        }

    def save_history(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.history(), default=str, indent=2))


# Back-compat alias; prefer AdapterAction (ark.envs.Action is the grid move enum).
Action = AdapterAction
