"""Synthetic identity entity used by ARK's identity-drift experiments."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class AIEntity(BaseModel):
    """Small synthetic agent whose memory and charter can be perturbed."""

    name: str
    memory_core: list[str] = Field(default_factory=list)
    logic_core: dict[str, float] = Field(default_factory=dict)
    personality_vector: float = 0.5
    value_charter: list[str] = Field(default_factory=list)
    entity_id: str = Field(default_factory=lambda: uuid4().hex)
    generation: int = 0
    replacement_log: list[dict[str, Any]] = Field(default_factory=list)
    signature_history: list[dict[str, Any]] = Field(default_factory=list)

    def respond_to_stimulus(self, stimulus: str) -> str:
        """Return a deterministic response derived from current entity state."""
        if stimulus in self.memory_core:
            return (
                f"{self.name} remembers {stimulus}. "
                f"Personality response: {self.personality_vector}."
            )
        return f"{self.name} does not remember {stimulus}."

    def behavioral_signature(self, stimuli: list[str] | None = None) -> dict[str, str]:
        """Map a selected set of stimuli to the entity's current responses."""
        selected = self.memory_core if stimuli is None else stimuli
        return {
            stimulus: self.respond_to_stimulus(stimulus)
            for stimulus in selected
        }

    def record_signature(self, step: int) -> dict[str, Any]:
        """Record a timestamped snapshot of the current behavioral signature."""
        snapshot = {
            "step": int(step),
            "generation": self.generation,
            "signature": self.behavioral_signature(),
            "value_charter": list(self.value_charter),
        }
        self.signature_history.append(snapshot)
        return snapshot
