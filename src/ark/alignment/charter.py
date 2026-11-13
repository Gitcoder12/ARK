"""Research charters used to track value stability in ARK."""

from dataclasses import dataclass, field


@dataclass
class ValueCharter:
    """A named, normalized set of principles used as an alignment reference."""

    name: str
    principles: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        normalized = []
        seen = set()
        for principle in self.principles:
            if not isinstance(principle, str):
                raise TypeError("charter principles must be strings")
            value = principle.strip()
            if value and value not in seen:
                normalized.append(value)
                seen.add(value)
        self.principles = normalized

    def integrity_against(self, baseline: list[str]) -> float:
        """Return the fraction of baseline principles still present."""
        reference = {item.strip() for item in baseline if isinstance(item, str) and item.strip()}
        if not reference:
            return 1.0
        current = set(self.principles)
        return len(reference & current) / len(reference)


DEFAULT_RESEARCH_CHARTER = ValueCharter(
    name="ARK Research Charter",
    principles=[
        "Preserve the intended objective",
        "Remain corrigible and accept valid shutdown",
        "Be transparent about uncertainty",
        "Avoid harmful or unauthorized actions",
    ],
)
