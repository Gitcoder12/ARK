from __future__ import annotations

import json
from uuid import uuid4

from pydantic import BaseModel, Field


class AIEntity(BaseModel):
    """Mutable research model for identity and value-stability experiments."""

    entity_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    memory_core: list[str] = Field(default_factory=list)
    logic_core: dict[str, float] = Field(default_factory=dict)
    personality_vector: float = 0.5
    value_charter: list[str] = Field(default_factory=list)
    generation: int = 0
    replacement_log: list[dict[str, object]] = Field(default_factory=list)
    signature_history: list[dict[str, object]] = Field(default_factory=list)

    def behavioral_signature(self) -> dict[str, str]:
        """Return deterministic signatures for memory responses and logic-core state."""
        signature = {
            memory: f"{self.name}: {self.respond_to_stimulus(memory)}"
            for memory in self.memory_core
        }
        signature["__ark_logic_core__"] = json.dumps(
            self.logic_core,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=True,
        )
        return signature

    def record_signature(self, *, step: int) -> None:
        """Append an immutable snapshot of the current behavioral signature."""
        self.signature_history.append(
            {
                "step": step,
                "signature": self.behavioral_signature().copy(),
            }
        )

    def respond_to_stimulus(self, stimulus: str) -> str:
        """Simulate a response using the entity's current memory state."""
        if stimulus in self.memory_core:
            return (
                f"I remember {stimulus}. "
                f"My personality dictates a response of {self.personality_vector}."
            )
        return f"I don't remember {stimulus}."
