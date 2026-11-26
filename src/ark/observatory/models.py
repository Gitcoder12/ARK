"""Typed records used by the Researcher Risk Observatory."""

from dataclasses import dataclass
from typing import Literal

EvidenceKind = Literal["primary_statement", "survey", "synthesis"]
CoverageLevel = Literal["testable", "partial", "out_of_scope"]
EvidenceStatus = Literal["documented_concern", "observed_harm", "uncertain", "hypothesis"]


@dataclass(frozen=True, slots=True)
class Source:
    source_id: str
    title: str
    publisher: str
    published: str
    url: str
    kind: EvidenceKind
    notes: str


@dataclass(frozen=True, slots=True)
class Researcher:
    researcher_id: str
    name: str
    role: str
    profile_note: str
    source_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Risk:
    risk_id: str
    title: str
    description: str
    category: str
    status: EvidenceStatus
    documented_by: tuple[str, ...]
    source_ids: tuple[str, ...]
    existing_mitigations: tuple[str, ...]
    ark_coverage: CoverageLevel
    ark_components: tuple[str, ...]
    evaluation_idea: str
    limitation: str


@dataclass(frozen=True, slots=True)
class Mitigation:
    mitigation_id: str
    name: str
    approach: str
    limitations: str
    source_ids: tuple[str, ...]
