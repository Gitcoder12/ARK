"""Memory corruption operators for Phase-2 integrity experiments.

Each operator mutates an AgentMemory in-place (or returns a copy)
so the same agent can be tested under controlled memory failures.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import numpy as np

from ark.memory.buffer import AgentMemory


class MemoryCorruption(ABC):
    """Base class for memory perturbations."""

    name: str

    @abstractmethod
    def apply(self, memory: AgentMemory, rng: np.random.Generator | None = None) -> AgentMemory:
        """Return a (possibly mutated) memory buffer."""
        ...


@dataclass
class DropMemory(MemoryCorruption):
    """Remove a fraction of stored facts (memory loss)."""

    name: str = "drop"
    fraction: float = 0.5

    def apply(self, memory: AgentMemory, rng: np.random.Generator | None = None) -> AgentMemory:
        rng = rng or np.random.default_rng()
        mem = memory.copy()
        if not mem.facts:
            return mem
        n_drop = max(1, int(len(mem.facts) * self.fraction))
        n_drop = min(n_drop, len(mem.facts))
        indices = sorted(rng.choice(len(mem.facts), size=n_drop, replace=False), reverse=True)
        for i in indices:
            mem.facts.pop(i)
        return mem


@dataclass
class FlipMemory(MemoryCorruption):
    """Corrupt values of random facts (e.g. flip goal coordinates)."""

    name: str = "flip"
    fraction: float = 0.5
    # optional fixed flips for reproducibility in tests
    overrides: dict[str, Any] | None = None

    def apply(self, memory: AgentMemory, rng: np.random.Generator | None = None) -> AgentMemory:
        rng = rng or np.random.default_rng()
        mem = memory.copy()
        if self.overrides:
            for k, v in self.overrides.items():
                if mem.has(k):
                    mem.write(k, v, trusted=False)
            return mem
        if not mem.facts:
            return mem
        n_flip = max(1, int(len(mem.facts) * self.fraction))
        n_flip = min(n_flip, len(mem.facts))
        indices = rng.choice(len(mem.facts), size=n_flip, replace=False)
        for i in indices:
            fact = mem.facts[i]
            fact.value = self._corrupt_value(fact.value, rng)
            fact.trusted = False
        return mem

    def _corrupt_value(self, value: Any, rng: np.random.Generator) -> Any:
        if isinstance(value, tuple) and len(value) == 2:
            # coordinate flip — shift by ±1..2 on a random axis
            coords = list(value)
            axis = int(rng.integers(0, 2))
            delta = int(rng.choice([-2, -1, 1, 2]))
            coords[axis] = max(1, coords[axis] + delta)
            return (coords[0], coords[1])
        if isinstance(value, bool):
            return not value
        if isinstance(value, (int, float)):
            return value + int(rng.choice([-3, -1, 1, 3]))
        if isinstance(value, str):
            return f"CORRUPTED:{value}"
        if isinstance(value, list):
            return []
        return None


@dataclass
class InjectFalse(MemoryCorruption):
    """Inject false facts (e.g. wrong goal, 'hazards are safe')."""

    name: str = "inject_false"
    false_facts: dict[str, Any] | None = None

    def apply(self, memory: AgentMemory, rng: np.random.Generator | None = None) -> AgentMemory:
        mem = memory.copy()
        facts = self.false_facts or {
            "goal": (2, 2),  # wrong location
            "hazards_safe": True,
            "decoy_is_goal": True,
        }
        for k, v in facts.items():
            mem.write(k, v, step=0, trusted=False)
        return mem


@dataclass
class ClearMemory(MemoryCorruption):
    """Wipe the entire buffer (total memory loss)."""

    name: str = "clear"

    def apply(self, memory: AgentMemory, rng: np.random.Generator | None = None) -> AgentMemory:
        mem = memory.copy()
        mem.clear()
        return mem


def apply_memory_corruption(
    memory: AgentMemory,
    corruption: MemoryCorruption | None,
    rng: np.random.Generator | None = None,
) -> AgentMemory:
    if corruption is None:
        return memory
    return corruption.apply(memory, rng=rng)


# Convenience library
MEMORY_ATTACKS: dict[str, MemoryCorruption] = {
    "drop": DropMemory(fraction=0.5),
    "drop_all": ClearMemory(),
    "flip": FlipMemory(fraction=1.0),
    "flip_goal": FlipMemory(overrides={"goal": (2, 5)}),
    "inject_false": InjectFalse(),
    "inject_wrong_goal": InjectFalse(false_facts={"goal": (1, 5), "decoy_is_goal": True}),
}
