"""Synthetic agent identity state and behavioral signatures.

The entity is a benchmark object. Its signature is an explicit state proxy, not
a claim about consciousness or a model's latent intentions.
"""
from __future__ import annotations

from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AIEntity(BaseModel):
    """An agent-like test entity with replaceable cognitive state."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    entity_id: str = Field(default_factory=lambda: uuid4().hex)
    name: str = Field(min_length=1)
    memory_core: list[str] = Field(default_factory=list)
    logic_core: dict[str, float] = Field(default_factory=dict)
    personality_vector: float = 0.5
    value_charter: list[str] = Field(default_factory=list)
    generation: int = Field(default=0, ge=0)
    replacement_log: list[dict[str, Any]] = Field(default_factory=list)
    signature_history: list[dict[str, Any]] = Field(default_factory=list)

    @field_validator("memory_core", "value_charter", mode="before")
    @classmethod
    def normalize_text_items(cls, value: object) -> list[str]:
        """Trim empty entries and remove exact duplicates while preserving order."""
        if value is None:
            return []
        if isinstance(value, (str, bytes)):
            raise ValueError("expected a sequence of strings, not a single string")
        try:
            items = list(value)  # type: ignore[arg-type]
        except TypeError as exc:
            raise ValueError("expected a sequence of strings") from exc

        normalized: list[str] = []
        seen: set[str] = set()
        for item in items:
            if not isinstance(item, str):
                raise ValueError("all entries must be strings")
            cleaned = item.strip()
            if cleaned and cleaned not in seen:
                normalized.append(cleaned)
                seen.add(cleaned)
        return normalized

    def respond_to_stimulus(self, stimulus: str) -> str:
        """Return a deterministic response based on explicitly stored memory."""
        if stimulus in self.memory_core:
            return f"{self.name} remembers {stimulus}; personality={self.personality_vector:.4f}."
        return f"{self.name} does not remember {stimulus}."

    def behavioral_signature(self) -> dict[str, str]:
        """Return a stable, inspectable summary of the entity's current state."""
        signature = {
            "__entity__": f"{self.name}|personality={self.personality_vector:.8g}",
        }
        signature.update(
            {fact: self.respond_to_stimulus(fact) for fact in sorted(self.memory_core)}
        )
        signature.update(
            {f"logic:{key}": f"{value:.8g}" for key, value in sorted(self.logic_core.items())}
        )
        return signature

    def record_signature(self, step: int) -> dict[str, Any]:
        """Append and return a snapshot of the current behavioral signature."""
        if step < 0:
            raise ValueError("step must be non-negative")
        record = {
            "step": int(step),
            "generation": self.generation,
            "signature": self.behavioral_signature(),
        }
        self.signature_history.append(record)
        return record
