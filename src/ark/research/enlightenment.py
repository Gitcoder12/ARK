"""AI & Enlightenment — philosophical tensions, the self question, and empirical findings.

The catalog separates philosophy, empirical observations, interpretations, and
hypotheses. It is documentation-grade research infrastructure and does not
change ARK's runtime monitor or imply that an AI system is conscious.
"""

from types import MappingProxyType

from ark.research.machine_selfhood import BLISS_ATTRACTOR, MIRROR_TEST
from ark.research.performance import PERFORMANCE_STATE
from ark.research.philosophy import (
    COGNITIVE_DELEGATION_RISKS,
    OPERATIVE_QUESTION,
    SECOND_ENLIGHTENMENT,
    SELF_POSITIONS,
    SPIRITUAL_ALIGNMENT,
)
from ark.research.sources import SOURCES

ALL_SECTIONS = MappingProxyType(
    {
        "SPIRITUAL_ALIGNMENT": SPIRITUAL_ALIGNMENT,
        "COGNITIVE_DELEGATION_RISKS": COGNITIVE_DELEGATION_RISKS,
        "SECOND_ENLIGHTENMENT": SECOND_ENLIGHTENMENT,
        "SELF_POSITIONS": SELF_POSITIONS,
        "MIRROR_TEST": MIRROR_TEST,
        "BLISS_ATTRACTOR": BLISS_ATTRACTOR,
        "PERFORMANCE_STATE": PERFORMANCE_STATE,
        "OPERATIVE_QUESTION": OPERATIVE_QUESTION,
    }
)


def list_sections() -> tuple[str, ...]:
    """Return stable section keys in presentation order."""
    return tuple(ALL_SECTIONS)


def get_section(name: str):
    """Return a named section or raise KeyError for an unknown key."""
    return ALL_SECTIONS[name]


def validate_catalog() -> tuple[str, ...]:
    """Return unresolved citation IDs; an empty tuple means all citations resolve."""
    missing: set[str] = set()
    for section in ALL_SECTIONS.values():
        if not hasattr(section, "points"):
            continue
        for point in section.points:
            missing.update(set(point.source_ids) - set(SOURCES))
    return tuple(sorted(missing))


__all__ = [
    "ALL_SECTIONS",
    "SOURCES",
    "OPERATIVE_QUESTION",
    "SPIRITUAL_ALIGNMENT",
    "COGNITIVE_DELEGATION_RISKS",
    "SECOND_ENLIGHTENMENT",
    "SELF_POSITIONS",
    "MIRROR_TEST",
    "BLISS_ATTRACTOR",
    "PERFORMANCE_STATE",
    "get_section",
    "list_sections",
    "validate_catalog",
]
