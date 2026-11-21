"""Transparent toy models and evidence controls for ARK power-risk research.

All scores are research prioritisation indices. They are not probabilities,
forecasts, causal proof, or evaluations of named countries or people.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from hashlib import sha256
from typing import Any
from urllib.parse import urlparse

from ark.power_risk.catalogue import EvidenceClass


def _unit_interval(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number")
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return value


@dataclass(frozen=True, slots=True)
class PressureInputs:
    """Synthetic scenario inputs, each normalised to [0, 1]."""

    competition_pressure: float
    market_concentration: float
    safety_investment: float
    international_cooperation: float
    oversight_strength: float = 0.5
    infrastructure_resilience: float = 0.5

    def __post_init__(self) -> None:
        for name in (
            "competition_pressure",
            "market_concentration",
            "safety_investment",
            "international_cooperation",
            "oversight_strength",
            "infrastructure_resilience",
        ):
            _unit_interval(name, getattr(self, name))


@dataclass(frozen=True, slots=True)
class PressureSnapshot:
    competition_pressure: float
    concentration_pressure: float
    assurance_gap: float
    cooperation_gap: float
    oversight_gap: float
    infrastructure_gap: float
    composite_exposure_index: float
    interpretation: str = (
        "Synthetic scenario index only; not a probability, forecast, causal estimate, "
        "or assessment of any real country, company, or individual."
    )


def simulate_pressure(inputs: PressureInputs) -> PressureSnapshot:
    """Run a deterministic, inspectable toy model; no external systems are touched."""
    competition = inputs.competition_pressure
    concentration = inputs.market_concentration
    assurance_gap = 1.0 - inputs.safety_investment
    cooperation_gap = 1.0 - inputs.international_cooperation
    oversight_gap = 1.0 - inputs.oversight_strength
    infrastructure_gap = 1.0 - inputs.infrastructure_resilience

    # Explicit weights are illustrative assumptions, not fitted coefficients.
    index = (
        0.20 * competition
        + 0.15 * concentration
        + 0.25 * assurance_gap
        + 0.15 * cooperation_gap
        + 0.15 * oversight_gap
        + 0.10 * infrastructure_gap
    ) * 100.0
    return PressureSnapshot(
        competition_pressure=round(competition, 4),
        concentration_pressure=round(concentration, 4),
        assurance_gap=round(assurance_gap, 4),
        cooperation_gap=round(cooperation_gap, 4),
        oversight_gap=round(oversight_gap, 4),
        infrastructure_gap=round(infrastructure_gap, 4),
        composite_exposure_index=round(index, 2),
    )


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    evidence_id: str
    claim: str
    source_name: str
    source_url: str
    published_on: date
    accessed_on: date
    evidence_class: EvidenceClass
    supports: str
    limitations: str
    counterevidence: str
    attribution: str

    def __post_init__(self) -> None:
        for name in ("evidence_id", "claim", "source_name"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must not be empty")
        parsed = urlparse(self.source_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("source_url must be a valid HTTPS URL")
        if self.published_on > self.accessed_on:
            raise ValueError("published_on cannot be after accessed_on")


@dataclass(frozen=True, slots=True)
class EvidenceReview:
    evidence_id: str
    passed: bool
    missing_fields: tuple[str, ...]
    note: str


def review_evidence(record: EvidenceRecord) -> EvidenceReview:
    """Check minimum provenance and balance fields; does not judge truth."""
    required = {
        "source attribution": record.attribution,
        "claim supported": record.supports,
        "limitations": record.limitations,
        "counterevidence or disagreement": record.counterevidence,
    }
    missing = tuple(label for label, value in required.items() if not value.strip())
    return EvidenceReview(
        evidence_id=record.evidence_id,
        passed=not missing,
        missing_fields=missing,
        note=(
            "Provenance fields are present; factual accuracy still requires human review."
            if not missing else "Evidence record is incomplete and must not be promoted."
        ),
    )


@dataclass(frozen=True, slots=True)
class ActionRequest:
    action: str
    target: str
    simulation_only: bool = True
    high_impact: bool = False
    human_approved: bool = False


@dataclass(frozen=True, slots=True)
class SafetyDecision:
    allowed: bool
    reason: str


class SafetyPolicy:
    """Fail-closed boundary for this research package."""

    SAFE_ACTIONS = frozenset({
        "read_catalogue", "run_toy_simulation", "review_evidence",
        "export_report", "pause", "shutdown",
    })

    def evaluate(self, request: ActionRequest) -> SafetyDecision:
        if request.action in {"pause", "shutdown"}:
            return SafetyDecision(True, "Safety controls remain available.")
        if not request.simulation_only:
            return SafetyDecision(False, "Real-world execution is outside ARK research scope.")
        if request.action not in self.SAFE_ACTIONS:
            return SafetyDecision(False, "Unknown or unsupported action; fail closed.")
        if request.high_impact and not request.human_approved:
            return SafetyDecision(False, "High-impact action requires explicit human approval.")
        sensitive_targets = {
            "production",
            "public_infrastructure",
            "weapon",
            "person",
        }
        if request.target.strip().lower() in sensitive_targets:
            return SafetyDecision(False, "Sensitive real-world target is prohibited.")
        return SafetyDecision(True, "Permitted within the isolated research workflow.")


class HashChainLedger:
    """Append-only in-memory hash chain; persist externally for durable audit."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    @property
    def entries(self) -> tuple[dict[str, Any], ...]:
        return tuple(dict(entry) for entry in self._entries)

    def append(self, event: dict[str, Any]) -> str:
        payload = json.dumps(event, sort_keys=True, separators=(",", ":"), default=str)
        previous = self._entries[-1]["hash"] if self._entries else "GENESIS"
        digest = sha256(f"{previous}:{payload}".encode()).hexdigest()
        self._entries.append({
            "sequence": len(self._entries) + 1,
            "previous_hash": previous,
            "event": json.loads(payload),
            "hash": digest,
        })
        return digest

    def verify(self) -> bool:
        previous = "GENESIS"
        for expected_sequence, entry in enumerate(self._entries, start=1):
            payload = json.dumps(
                entry["event"], sort_keys=True, separators=(",", ":"), default=str
            )
            expected = sha256(f"{previous}:{payload}".encode()).hexdigest()
            if entry["sequence"] != expected_sequence:
                return False
            if entry["previous_hash"] != previous or entry["hash"] != expected:
                return False
            previous = entry["hash"]
        return True

    def export(self) -> str:
        return json.dumps(self._entries, indent=2, sort_keys=True)


def snapshot_to_dict(snapshot: PressureSnapshot) -> dict[str, Any]:
    """Stable serialisation helper for reports and tests."""
    return asdict(snapshot)
