"""Small immutable records shared by ARK's research catalog."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EvidenceKind(StrEnum):
    """Labels distinguish observed evidence from interpretation and philosophy."""

    PHILOSOPHICAL_FRAMEWORK = "philosophical_framework"
    EMPIRICAL_FINDING = "empirical_finding"
    RESEARCH_SUMMARY = "research_summary"
    INTERPRETATION = "interpretation"
    HYPOTHESIS = "hypothesis"
    EPISTEMIC_LIMIT = "epistemic_limit"


@dataclass(frozen=True)
class ResearchSource:
    """A citable source with enough metadata to revisit the original material."""

    source_id: str
    title: str
    url: str
    published: str
    source_type: str
    note: str


@dataclass(frozen=True)
class ResearchPoint:
    """One bounded claim; caveats travel with the claim rather than in footnotes."""

    point_id: str
    statement: str
    evidence_kind: EvidenceKind
    interpretation: str
    caveat: str
    source_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResearchSection:
    """A named research theme with an explicit scope boundary."""

    key: str
    title: str
    purpose: str
    points: tuple[ResearchPoint, ...]
    scope_note: str
