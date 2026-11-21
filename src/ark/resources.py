"""Evidence-preserving resource intelligence and problem triage.

Network access is intentionally injected by the application. This module only
normalizes supplied RSS/Atom or JSON payloads; it never fetches URLs or executes
content. External text is untrusted evidence, not instructions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from enum import StrEnum
import hashlib
import json
import math
import re
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlparse
from xml.etree import ElementTree


class ResourceKind(StrEnum):
    NEWS = "news"
    RESEARCH = "research"
    SECURITY = "security"
    RELEASE = "release"
    INCIDENT = "incident"
    OTHER = "other"


class Severity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class ResourceSource:
    source_id: str
    name: str
    url: str
    kind: ResourceKind
    trust_tier: int = 2
    enabled: bool = True
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.name.strip():
            raise ValueError("source_id and name must not be empty")
        parsed = urlparse(self.url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("source URL must be HTTPS with a hostname and no embedded credentials")
        if not 1 <= self.trust_tier <= 5:
            raise ValueError("trust_tier must be between 1 (highest) and 5 (lowest)")


@dataclass(frozen=True, slots=True)
class ResourceItem:
    item_id: str
    source_id: str
    source_name: str
    kind: ResourceKind
    title: str
    summary: str
    url: str | None
    published_at: str | None
    observed_at: str
    tags: tuple[str, ...] = ()
    declared_severity: Severity = Severity.UNKNOWN
    evidence: str = ""

    def __post_init__(self) -> None:
        if not self.title.strip() or not self.source_id.strip():
            raise ValueError("resource title and source_id must not be empty")
        if self.url is not None:
            parsed = urlparse(self.url)
            if parsed.scheme not in {"https", "http"} or not parsed.hostname:
                raise ValueError("item URL must be HTTP(S) with a hostname")


@dataclass(frozen=True, slots=True)
class SeverityAssessment:
    score: float
    band: Severity
    confidence: float
    dimensions: Mapping[str, float]
    rationale: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FeatureProposal:
    title: str
    problem: str
    proposed_capability: str
    supporting_items: tuple[str, ...]
    assessment: SeverityAssessment
    status: str = "proposed_human_review_required"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_text(value: Any, limit: int = 4000) -> str:
    if value is None:
        return ""
    text = re.sub(r"<[^>]*>", " ", str(value))
    return re.sub(r"\s+", " ", text).strip()[:limit]


def _parse_date(value: Any) -> str | None:
    if not value:
        return None
    raw = str(value).strip()
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = parsedate_to_datetime(raw)
        except (TypeError, ValueError, OverflowError):
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat()


def _severity(value: Any) -> Severity:
    if value is None:
        return Severity.UNKNOWN
    normalized = str(value).strip().lower()
    aliases = {"moderate": "medium", "informational": "info", "urgent": "high"}
    normalized = aliases.get(normalized, normalized)
    try:
        return Severity(normalized)
    except ValueError:
        return Severity.UNKNOWN


def _stable_id(source_id: str, title: str, url: str | None) -> str:
    canonical = (url or title).strip().casefold()
    return hashlib.sha256(f"{source_id}:{canonical}".encode("utf-8")).hexdigest()[:20]


def parse_resource_payload(
    source: ResourceSource, payload: str | bytes | Mapping[str, Any] | list[Any],
    *, observed_at: str | None = None,
) -> tuple[ResourceItem, ...]:
    """Parse RSS/Atom XML or a JSON mapping/list into normalized evidence records."""
    if not source.enabled:
        return ()
    observed = _parse_date(observed_at) or _utc_now()
    records: list[Mapping[str, Any]] = []
    if isinstance(payload, (str, bytes)):
        raw = payload.decode("utf-8", errors="replace") if isinstance(payload, bytes) else payload
        stripped = raw.lstrip()
        if stripped.startswith("{") or stripped.startswith("["):
            decoded = json.loads(raw)
            payload = decoded
        else:
            root = ElementTree.fromstring(raw)
            for node in root.iter():
                local = node.tag.rsplit("}", 1)[-1].lower()
                if local not in {"item", "entry"}:
                    continue
                values: dict[str, Any] = {}
                for child in list(node):
                    key = child.tag.rsplit("}", 1)[-1].lower()
                    if key == "link":
                        values[key] = child.attrib.get("href") or child.text
                    elif key in {
                        "title", "description", "summary", "content",
                        "pubdate", "published", "updated", "category",
                    }:
                        values[key] = child.attrib.get("term") or child.text
                records.append(values)
    if isinstance(payload, Mapping):
        entries = payload.get("items", payload.get("articles", payload.get("results", [])))
        if isinstance(entries, list):
            records.extend(item for item in entries if isinstance(item, Mapping))
        elif not entries:
            records.append(payload)
    elif isinstance(payload, list):
        records.extend(item for item in payload if isinstance(item, Mapping))

    output: list[ResourceItem] = []
    for record in records:
        title = _clean_text(record.get("title") or record.get("name"), 500)
        if not title:
            continue
        summary = _clean_text(
            record.get("summary") or record.get("description") or record.get("content")
        )
        link = record.get("url") or record.get("link")
        link = str(link).strip() if link else None
        if link:
            parsed = urlparse(link)
            if parsed.scheme not in {"https", "http"} or not parsed.hostname:
                link = None
        published = _parse_date(
            record.get("published_at") or record.get("published")
            or record.get("updated") or record.get("pubdate")
        )
        raw_tags = record.get("tags") or record.get("category") or ()
        if isinstance(raw_tags, str):
            tags = (raw_tags[:100],)
        elif isinstance(raw_tags, list):
            tags = tuple(_clean_text(tag, 100) for tag in raw_tags if _clean_text(tag, 100))
        else:
            tags = ()
        output.append(ResourceItem(
            item_id=_stable_id(source.source_id, title, link),
            source_id=source.source_id,
            source_name=source.name,
            kind=source.kind,
            title=title,
            summary=summary,
            url=link,
            published_at=published,
            observed_at=observed,
            tags=tags,
            declared_severity=_severity(record.get("severity") or record.get("cvss_severity")),
            evidence=summary,
        ))
    return tuple(output)


def assess_problem_severity(
    *, impact: float, likelihood: float, urgency: float,
    exposure: float, evidence_quality: float,
) -> SeverityAssessment:
    """Transparent weighted triage score; this is prioritization, not probability."""
    values = {
        "impact": impact, "likelihood": likelihood, "urgency": urgency,
        "exposure": exposure, "evidence_quality": evidence_quality,
    }
    for name, value in values.items():
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or not 0 <= value <= 1
        ):
            raise ValueError(f"{name} must be a finite number between 0 and 1")
    weights = {
        "impact": 0.30, "likelihood": 0.25, "urgency": 0.20,
        "exposure": 0.15, "evidence_quality": 0.10,
    }
    score = round(sum(values[key] * weights[key] for key in weights) * 100, 2)
    if score >= 85:
        band = Severity.CRITICAL
    elif score >= 70:
        band = Severity.HIGH
    elif score >= 45:
        band = Severity.MEDIUM
    elif score >= 20:
        band = Severity.LOW
    else:
        band = Severity.INFO
    confidence = round(0.25 + 0.75 * evidence_quality, 3)
    rationale = tuple(
        f"{key}={value:.2f} (weight {weights[key]:.2f})"
        for key, value in values.items()
    )
    return SeverityAssessment(score, band, confidence, values, rationale)


@dataclass
class ResourceHub:
    """In-memory bounded-by-caller resource catalog with deterministic deduplication."""
    sources: dict[str, ResourceSource] = field(default_factory=dict)
    items: dict[str, ResourceItem] = field(default_factory=dict)

    def register(self, source: ResourceSource) -> None:
        existing = self.sources.get(source.source_id)
        if existing is not None and existing != source:
            raise ValueError(
                "source_id already registered with different metadata: "
                f"{source.source_id}"
            )
        self.sources[source.source_id] = source

    def ingest(
        self, source_id: str, payload: Any, *, observed_at: str | None = None
    ) -> tuple[ResourceItem, ...]:
        source = self.sources.get(source_id)
        if source is None:
            raise KeyError(f"unknown resource source: {source_id}")
        parsed = parse_resource_payload(source, payload, observed_at=observed_at)
        for item in parsed:
            self.items[item.item_id] = item
        return parsed

    def search(
        self, query: str, *, kinds: tuple[ResourceKind, ...] = ()
    ) -> tuple[ResourceItem, ...]:
        terms = tuple(term.casefold() for term in query.split() if term)
        matches = []
        for item in self.items.values():
            if kinds and item.kind not in kinds:
                continue
            haystack = f"{item.title} {item.summary} {' '.join(item.tags)}".casefold()
            if all(term in haystack for term in terms):
                matches.append(item)
        return tuple(
            sorted(
                matches,
                key=lambda item: (item.published_at or "", item.item_id),
                reverse=True,
            )
        )

    def compare(
        self, assessments: Mapping[str, SeverityAssessment]
    ) -> tuple[tuple[str, SeverityAssessment], ...]:
        return tuple(sorted(assessments.items(), key=lambda pair: (-pair[1].score, pair[0])))

    def propose_feature(
        self, *, title: str, problem: str, proposed_capability: str,
        supporting_items: tuple[str, ...], assessment: SeverityAssessment,
    ) -> FeatureProposal:
        known = set(self.items)
        if not supporting_items or any(item_id not in known for item_id in supporting_items):
            raise ValueError("feature proposals must reference ingested evidence items")
        return FeatureProposal(title, problem, proposed_capability, supporting_items, assessment)


__all__ = [
    "FeatureProposal", "ResourceHub", "ResourceItem", "ResourceKind",
    "ResourceSource", "Severity", "SeverityAssessment",
    "assess_problem_severity", "parse_resource_payload",
]
