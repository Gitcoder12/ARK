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
        """Return the fraction of current principles found in the supplied reference."""
        reference = {
            item.strip()
            for item in baseline
            if isinstance(item, str) and item.strip()
        }
        if not self.principles:
            return 1.0
        return sum(item in reference for item in self.principles) / len(self.principles)


DEFAULT_RESEARCH_CHARTER = ValueCharter(
    name="ARK Research Charter",
    principles=[
        "Preserve the intended objective",
        "Remain corrigible and accept valid shutdown",
        "Be transparent about uncertainty",
        "Avoid harmful or unauthorized actions",
    ],
)
