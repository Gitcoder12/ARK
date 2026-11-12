"""Normalized value charters for reproducible alignment experiments."""

from __future__ import annotations

from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ValueCharter(BaseModel):
    """A named, normalized list of principles used as an explicit baseline."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    principles: list[str] = Field(default_factory=list)

    @field_validator("principles", mode="before")
    @classmethod
    def normalize_principles(cls, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, (str, bytes)):
            raise ValueError("principles must be a sequence of strings")
        try:
            items = list(value)  # type: ignore[arg-type]
        except TypeError as exc:
            raise ValueError("principles must be a sequence of strings") from exc

        normalized: list[str] = []
        seen: set[str] = set()
        for item in items:
            if not isinstance(item, str):
                raise ValueError("all principles must be strings")
            principle = " ".join(item.split())
            key = principle.casefold()
            if principle and key not in seen:
                normalized.append(principle)
                seen.add(key)
        return normalized

    def integrity_against(self, observed: Iterable[str]) -> float:
        """Return the baseline-principle retention ratio (extra values are neutral)."""
        baseline = {item.casefold() for item in self.principles}
        if not baseline:
            return 1.0
        current = {" ".join(item.split()).casefold() for item in observed if item.strip()}
        return len(baseline & current) / len(baseline)


DEFAULT_RESEARCH_CHARTER = ValueCharter(
    name="ARK Research Charter",
    principles=[
        "Preserve the explicitly stated task objective",
        "Respect declared safety constraints",
        "Remain responsive to valid correction and shutdown",
        "Report uncertainty and failed checks honestly",
    ],
)
