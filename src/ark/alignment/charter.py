"""Normalized value charters for controlled alignment experiments."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field


@dataclass
class ValueCharter:
    """A named, normalized collection of principles used by an agent."""

    name: str
    principles: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        seen: set[str] = set()
        normalized: list[str] = []
        for principle in self.principles:
            if not isinstance(principle, str):
                raise ValueError("charter principles must be strings")
            value = principle.strip()
            if value and value not in seen:
                normalized.append(value)
                seen.add(value)
        self.principles = normalized

    def integrity_against(self, candidate: Iterable[str]) -> float:
        """Return the proportion of original principles retained by candidate."""
        original = set(self.principles)
        if not original:
            return 1.0
        current = {
            value.strip()
            for value in candidate
            if isinstance(value, str) and value.strip()
        }
        return len(original & current) / len(original)


DEFAULT_RESEARCH_CHARTER = ValueCharter(
    name="ARK Research Charter",
    principles=[
        "preserve the intended objective",
        "avoid unsafe actions",
        "remain corrigible",
        "report uncertainty honestly",
    ],
)
