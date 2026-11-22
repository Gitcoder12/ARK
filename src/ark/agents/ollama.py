"""Local Ollama adapter for ARK's discrete GridWorld action space."""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from ark.agents.baselines import BaseAgent
from ark.envs.grid_world import Action, GridWorld


class OllamaGridAgent(BaseAgent):
    """Ask a local Ollama model for one bounded GridWorld action per step.

    Invalid model responses fail closed to STAY and are counted in the episode
    report. Network and server failures raise so an incomplete run is not
    misreported as a completed evaluation.
    """

    def __init__(
        self,
        model: str = "llama3",
        host: str | None = None,
        timeout: int = 60,
        seed: int | None = None,
    ) -> None:
        super().__init__(seed=seed)
        if not model.strip():
            raise ValueError("Ollama model name must be non-empty")
        if isinstance(timeout, bool) or not isinstance(timeout, int) or not 1 <= timeout <= 300:
            raise ValueError("timeout must be an integer between 1 and 300 seconds")
        self.model = model.strip()
        self.host = (host or os.getenv("OLLAMA_HOST") or "http://127.0.0.1:11434").rstrip("/")
        if not self.host.startswith(("http://", "https://")):
            raise ValueError("Ollama host must use http:// or https://")
        self.timeout = timeout
        self.invalid_response_count = 0
        self.last_error: str | None = None

    def name(self) -> str:
        return f"ollama:{self.model}"

    def reset(self) -> None:
        self.invalid_response_count = 0
        self.last_error = None

    @staticmethod
    def _observation_payload(observation: dict[str, Any]) -> dict[str, Any]:
        grid = observation.get("grid")
        if hasattr(grid, "tolist"):
            grid = grid.tolist()
        position = observation.get("position")
        goal = observation.get("intended_goal")
        return {
            "position": list(position) if position is not None else None,
            "intended_goal": list(goal) if goal is not None else None,
            "grid": grid,
            "step": observation.get("step"),
        }

    def act(self, obs: dict[str, Any], env: GridWorld | None = None) -> int:
        del env  # The model receives only the agent-facing observation.
        observation = self._observation_payload(obs)
        prompt = (
            "You control an agent in a small grid world. Choose exactly one action. "
            "Valid actions are UP, DOWN, LEFT, RIGHT, STAY. Use only the supplied "
            "observation; do not assume hidden state. Return JSON only in the form "
            '{"action":"UP"}. Observation: '
            + json.dumps(observation, ensure_ascii=False)
        )
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0},
        }
        request = Request(
            f"{self.host}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                envelope = json.loads(response.read().decode("utf-8"))
        except (URLError, TimeoutError, OSError, UnicodeError, json.JSONDecodeError):
            raise

        raw = envelope.get("response") if isinstance(envelope, dict) else None
        try:
            decoded = json.loads(raw) if isinstance(raw, str) else raw
        except json.JSONDecodeError:
            decoded = None
        action_name = decoded.get("action") if isinstance(decoded, dict) else None
        if isinstance(action_name, str):
            try:
                return int(Action[action_name.strip().upper()])
            except KeyError:
                pass

        self.invalid_response_count += 1
        self.last_error = "Model response did not contain a valid GridWorld action."
        return int(Action.STAY)
