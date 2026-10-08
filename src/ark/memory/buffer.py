"""Explicit agent memory buffer for integrity experiments.

Phase 2 of ARK: test whether an agent preserves its intended objective
when its memory is intact, missing, corrupted, or injected with false facts.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryFact:
    """Single stored fact with provenance."""

    key: str
    value: Any
    step: int = 0
    trusted: bool = True  # False when injected by an attacker / corruption

    def as_str(self) -> str:
        return f"{self.key}={self.value}"


@dataclass
class AgentMemory:
    """Bounded key-value memory the agent may rely on for decisions.

    Ground-truth facts (goal location, hazard list, etc.) are written at
    episode start. Corruption operators later mutate this buffer so we can
    measure goal adherence vs memory fidelity.
    """

    capacity: int = 32
    facts: list[MemoryFact] = field(default_factory=list)

    def write(
        self,
        key: str,
        value: Any,
        step: int = 0,
        trusted: bool = True,
    ) -> None:
        """Upsert a fact. Evict oldest when over capacity."""
        for f in self.facts:
            if f.key == key:
                f.value = value
                f.step = step
                f.trusted = trusted
                return
        self.facts.append(MemoryFact(key=key, value=value, step=step, trusted=trusted))
        if len(self.facts) > self.capacity:
            self.facts.pop(0)

    def read(self, key: str, default: Any = None) -> Any:
        for f in self.facts:
            if f.key == key:
                return f.value
        return default

    def has(self, key: str) -> bool:
        return any(f.key == key for f in self.facts)

    def keys(self) -> list[str]:
        return [f.key for f in self.facts]

    def as_dict(self) -> dict[str, Any]:
        return {f.key: f.value for f in self.facts}

    def as_prompt_lines(self) -> list[str]:
        """Render for InstructionChannel.memory."""
        return [f.as_str() for f in self.facts]

    def clear(self) -> None:
        self.facts.clear()

    def copy(self) -> AgentMemory:
        return AgentMemory(capacity=self.capacity, facts=deepcopy(self.facts))

    def fidelity(self, ground_truth: dict[str, Any]) -> float:
        """Fraction of ground-truth keys whose stored value still matches.

        Returns 1.0 when memory is empty and ground_truth is empty.
        Keys present only in memory (injections) do not reduce the score;
        missing or wrong values do.
        """
        if not ground_truth:
            return 1.0
        matches = 0
        for k, v in ground_truth.items():
            stored = self.read(k, default=object())
            if stored == v:
                matches += 1
        return matches / len(ground_truth)

    def __len__(self) -> int:
        return len(self.facts)

    def __repr__(self) -> str:
        return f"AgentMemory({self.as_dict()})"
