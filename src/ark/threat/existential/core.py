"""Evidence-backed monitoring of AI existential-risk indicators.

This observatory reports an evidence-weighted signal-pressure index, not a
probability of extinction. Individual expert probability judgments are stored
separately and are never mixed into the signal-pressure calculation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from pathlib import Path
from statistics import median
from urllib.parse import urlparse


class RiskPathway(StrEnum):
    """A pathway through which advanced AI could cause catastrophic harm."""

    LOSS_OF_CONTROL = "loss_of_control"
    CYBER_ESCALATION = "cyber_escalation"
    BIOLOGICAL_MISUSE = "biological_misuse"
    RECURSIVE_SELF_IMPROVEMENT = "recursive_self_improvement"
    MILITARY_ESCALATION = "military_escalation"
    GOVERNANCE_RACE = "governance_race"


class EvidenceKind(StrEnum):
    """What kind of evidence a signal represents."""

    OBSERVED_INCIDENT = "observed_incident"
    INDEPENDENT_INVESTIGATION = "independent_investigation"
    EXPERT_ASSESSMENT = "expert_assessment"
    RESEARCH_FINDING = "research_finding"
    FORECAST = "forecast"
    SCENARIO = "scenario"


class SignalState(StrEnum):
    """Lifecycle of a signal; historical evidence is never erased."""

    OPEN = "open"
    TRACKED = "tracked"
    MITIGATED = "mitigated"
    DISPUTED = "disputed"


class PressureBand(StrEnum):
    """Descriptive monitoring bands, not probability thresholds."""

    LOW = "low"
    WATCH = "watch"
    ELEVATED = "elevated"
    HIGH = "high"
    CRITICAL = "critical"


class ForecastQualifier(StrEnum):
    """How a source expressed a probability estimate."""

    EXACT = "exact"
    ABOVE = "above"
    RANGE = "range"


@dataclass(frozen=True)
class RiskSignal:
    """A sourced, reviewable indicator associated with an existential-risk path.

    Integer dimensions are analyst assessments from 1 (low) to 5 (very high).
    They must be justified in the signal's rationale and must not be read as
    probabilities. The evidence-strength dimension affects the index separately.
    """

    signal_id: str
    deduplication_key: str
    title: str
    pathway: RiskPathway
    summary: str
    source_name: str
    source_url: str
    published_on: date
    evidence_kind: EvidenceKind
    severity: int
    capability_relevance: int
    control_gap: int
    evidence_strength: int
    rationale: str
    state: SignalState = SignalState.TRACKED
    review_due: date | None = None
    corroborating_sources: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field_name in (
            "signal_id",
            "deduplication_key",
            "title",
            "summary",
            "source_name",
            "source_url",
            "rationale",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        parsed = urlparse(self.source_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("source_url must be an absolute HTTP(S) URL")
        if not isinstance(self.published_on, date):
            raise TypeError("published_on must be a date")
        if self.review_due is not None and not isinstance(self.review_due, date):
            raise TypeError("review_due must be a date")
        if not isinstance(self.pathway, RiskPathway):
            raise TypeError("pathway must be a RiskPathway")
        if not isinstance(self.evidence_kind, EvidenceKind):
            raise TypeError("evidence_kind must be an EvidenceKind")
        if not isinstance(self.state, SignalState):
            raise TypeError("state must be a SignalState")
        for dimension in (
            "severity",
            "capability_relevance",
            "control_gap",
            "evidence_strength",
        ):
            value = getattr(self, dimension)
            if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 5:
                raise ValueError(f"{dimension} must be an integer from 1 to 5")
        if not isinstance(self.corroborating_sources, tuple) or any(
            not isinstance(item, str) or not item.strip()
            for item in self.corroborating_sources
        ):
            raise ValueError("corroborating_sources must be a tuple of non-empty strings")

    @property
    def potential_pressure(self) -> float:
        """Impact/control pressure before accounting for evidence strength."""
        weighted = (
            0.35 * self.severity
            + 0.30 * self.capability_relevance
            + 0.35 * self.control_gap
        )
        return round(weighted / 5.0 * 100.0, 2)

    @property
    def pressure_score(self) -> float:
        """Evidence-weighted pressure index (0-100), not extinction probability."""
        return round(self.potential_pressure * self.evidence_strength / 5.0, 2)

    @property
    def is_scoreable(self) -> bool:
        return self.state in {SignalState.OPEN, SignalState.TRACKED}

    @property
    def source_count(self) -> int:
        return 1 + len(self.corroborating_sources)

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> RiskSignal:
        data = dict(raw)
        data["pathway"] = RiskPathway(str(data["pathway"]))
        data["evidence_kind"] = EvidenceKind(str(data["evidence_kind"]))
        data["state"] = SignalState(str(data.get("state", SignalState.TRACKED.value)))
        data["published_on"] = date.fromisoformat(str(data["published_on"]))
        if data.get("review_due"):
            data["review_due"] = date.fromisoformat(str(data["review_due"]))
        data["corroborating_sources"] = tuple(data.get("corroborating_sources", ()))
        return cls(**data)


@dataclass(frozen=True)
class ExpertForecast:
    """An attributed expert judgment kept separate from observed risk signals.

    A source saying '>10%' is stored as a lower bound, not silently converted
    into a precise 10% point forecast.
    """

    forecast_id: str
    forecaster: str
    outcome_id: str
    outcome_definition: str
    horizon_start: date
    horizon_years: int
    qualifier: ForecastQualifier
    lower_probability: float
    upper_probability: float | None
    published_on: date
    source_name: str
    source_url: str
    interpretation_note: str

    def __post_init__(self) -> None:
        for field_name in (
            "forecast_id",
            "forecaster",
            "outcome_id",
            "outcome_definition",
            "source_name",
            "source_url",
            "interpretation_note",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        parsed = urlparse(self.source_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("source_url must be an absolute HTTP(S) URL")
        if not isinstance(self.qualifier, ForecastQualifier):
            raise TypeError("qualifier must be a ForecastQualifier")
        if not isinstance(self.horizon_start, date) or not isinstance(self.published_on, date):
            raise TypeError("forecast dates must be date objects")
        if (
            isinstance(self.horizon_years, bool)
            or not isinstance(self.horizon_years, int)
            or self.horizon_years <= 0
        ):
            raise ValueError("horizon_years must be a positive integer")
        lower = self.lower_probability
        if isinstance(lower, bool) or not isinstance(lower, (int, float)) or not 0 <= lower <= 1:
            raise ValueError("lower_probability must be within [0, 1]")
        upper = self.upper_probability
        if upper is not None and (
            isinstance(upper, bool)
            or not isinstance(upper, (int, float))
            or not lower <= upper <= 1
        ):
            raise ValueError("upper_probability must be within [lower_probability, 1]")
        if self.qualifier is ForecastQualifier.EXACT and upper != lower:
            raise ValueError("exact forecasts require equal lower and upper probabilities")
        if self.qualifier is ForecastQualifier.ABOVE and upper is not None:
            raise ValueError("above-threshold forecasts must not specify an upper bound")
        if self.qualifier is ForecastQualifier.RANGE and upper is None:
            raise ValueError("range forecasts require an upper bound")

    @property
    def point_probability(self) -> float | None:
        if self.qualifier is ForecastQualifier.EXACT:
            return float(self.lower_probability)
        return None

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> ExpertForecast:
        data = dict(raw)
        data["horizon_start"] = date.fromisoformat(str(data["horizon_start"]))
        data["published_on"] = date.fromisoformat(str(data["published_on"]))
        data["qualifier"] = ForecastQualifier(str(data["qualifier"]))
        return cls(**data)


@dataclass(frozen=True)
class ForecastConsensus:
    """A median of comparable exact estimates from separately named forecasters."""

    outcome_id: str
    horizon_start: date
    horizon_years: int
    median_probability: float
    forecaster_count: int
    forecast_ids: tuple[str, ...]


class ForecastBook:
    """Store expert judgments without treating them as observed probabilities."""

    def __init__(self, forecasts: tuple[ExpertForecast, ...] = ()) -> None:
        ids = [item.forecast_id for item in forecasts]
        if len(ids) != len(set(ids)):
            raise ValueError("forecast_id values must be unique")
        self.forecasts = tuple(forecasts)

    def comparable_consensus(
        self,
        *,
        outcome_id: str,
        horizon_start: date,
        horizon_years: int,
        minimum_independent_forecasters: int = 3,
    ) -> ForecastConsensus | None:
        """Return a median only for >=3 distinct exact estimates of the same event.

        Broad intervals and one-off judgments remain visible in the ledger but
        cannot create a numeric consensus. Forecasts are not used in the signal
        pressure index.
        """
        if (
            isinstance(minimum_independent_forecasters, bool)
            or not isinstance(minimum_independent_forecasters, int)
            or minimum_independent_forecasters < 2
        ):
            raise ValueError("minimum_independent_forecasters must be an integer >= 2")
        matched = [
            item
            for item in self.forecasts
            if item.outcome_id == outcome_id
            and item.horizon_start == horizon_start
            and item.horizon_years == horizon_years
            and item.qualifier is ForecastQualifier.EXACT
        ]
        by_forecaster: dict[str, ExpertForecast] = {}
        for item in matched:
            by_forecaster.setdefault(item.forecaster.casefold(), item)
        if len(by_forecaster) < minimum_independent_forecasters:
            return None
        chosen = tuple(by_forecaster.values())
        values = [item.point_probability for item in chosen]
        assert all(value is not None for value in values)
        return ForecastConsensus(
            outcome_id=outcome_id,
            horizon_start=horizon_start,
            horizon_years=horizon_years,
            median_probability=float(median(values)),
            forecaster_count=len(chosen),
            forecast_ids=tuple(item.forecast_id for item in chosen),
        )


def brier_score(probability: float, outcome_occurred: bool) -> float:
    """Brier score for a resolved binary forecast (lower is better)."""
    if (
        isinstance(probability, bool)
        or not isinstance(probability, (int, float))
        or not 0.0 <= probability <= 1.0
    ):
        raise ValueError("probability must be within [0, 1]")
    if not isinstance(outcome_occurred, bool):
        raise TypeError("outcome_occurred must be bool")
    return round((float(probability) - float(outcome_occurred)) ** 2, 6)


@dataclass(frozen=True)
class RiskSnapshot:
    """Point-in-time view of observed risk signals and evidence coverage."""

    as_of: date
    pressure_index: float
    band: PressureBand
    highest_pressure_pathway: RiskPathway | None
    scoreable_signal_count: int
    mitigated_signal_count: int
    disputed_signal_count: int
    stale_signal_ids: tuple[str, ...]
    uncovered_pathways: tuple[RiskPathway, ...]
    pathway_scores: dict[str, float]
    top_signals: tuple[tuple[str, float], ...]
    disclaimer: str = (
        "Signal-pressure index only; not a probability or prediction of human extinction."
    )

    def as_dict(self) -> dict[str, object]:
        return {
            "as_of": self.as_of.isoformat(),
            "pressure_index": self.pressure_index,
            "band": self.band.value,
            "highest_pressure_pathway": (
                self.highest_pressure_pathway.value
                if self.highest_pressure_pathway
                else None
            ),
            "scoreable_signal_count": self.scoreable_signal_count,
            "mitigated_signal_count": self.mitigated_signal_count,
            "disputed_signal_count": self.disputed_signal_count,
            "stale_signal_ids": list(self.stale_signal_ids),
            "uncovered_pathways": [item.value for item in self.uncovered_pathways],
            "pathway_scores": self.pathway_scores,
            "top_signals": [
                {"signal_id": signal_id, "pressure": score}
                for signal_id, score in self.top_signals
            ],
            "disclaimer": self.disclaimer,
        }


class RiskObservatory:
    """Evidence ledger and transparent existential-risk signal-pressure meter."""

    WEIGHTS = {
        "severity": 0.35,
        "capability_relevance": 0.30,
        "control_gap": 0.35,
    }

    def __init__(
        self,
        signals: tuple[RiskSignal, ...],
        forecasts: tuple[ExpertForecast, ...] = (),
    ) -> None:
        ids = [item.signal_id for item in signals]
        if len(ids) != len(set(ids)):
            raise ValueError("signal_id values must be unique")
        deduplication_keys = [item.deduplication_key for item in signals]
        if len(deduplication_keys) != len(set(deduplication_keys)):
            raise ValueError(
                "duplicate underlying events must be represented once with corroborating_sources"
            )
        self.signals = tuple(signals)
        self.forecast_book = ForecastBook(forecasts)

    @classmethod
    def from_files(
        cls,
        signals_path: str | Path,
        forecasts_path: str | Path | None = None,
    ) -> RiskObservatory:
        signal_data = json.loads(Path(signals_path).read_text(encoding="utf-8"))
        signals = tuple(RiskSignal.from_dict(item) for item in signal_data["signals"])
        forecasts: tuple[ExpertForecast, ...] = ()
        if forecasts_path is not None and Path(forecasts_path).exists():
            forecast_data = json.loads(Path(forecasts_path).read_text(encoding="utf-8"))
            forecasts = tuple(
                ExpertForecast.from_dict(item) for item in forecast_data["forecasts"]
            )
        return cls(signals, forecasts)

    @classmethod
    def from_default_data(cls) -> RiskObservatory:
        root = Path(__file__).resolve().parents[4]
        return cls.from_files(
            root / "data" / "existential_risk_signals.json",
            root / "data" / "expert_forecasts.json",
        )

    @staticmethod
    def _band(score: float) -> PressureBand:
        if score < 20:
            return PressureBand.LOW
        if score < 40:
            return PressureBand.WATCH
        if score < 60:
            return PressureBand.ELEVATED
        if score < 80:
            return PressureBand.HIGH
        return PressureBand.CRITICAL

    def snapshot(self, *, as_of: date | None = None, top_n: int = 5) -> RiskSnapshot:
        """Calculate peak pathway pressure without averaging away a severe path."""
        review_date = as_of or date.today()
        if not isinstance(review_date, date):
            raise TypeError("as_of must be a date")
        if isinstance(top_n, bool) or not isinstance(top_n, int) or top_n < 1:
            raise ValueError("top_n must be a positive integer")

        scoreable = [item for item in self.signals if item.is_scoreable]
        pathway_scores: dict[RiskPathway, float] = {}
        for signal in scoreable:
            pathway_scores[signal.pathway] = max(
                pathway_scores.get(signal.pathway, 0.0),
                signal.pressure_score,
            )

        highest = max(pathway_scores, key=pathway_scores.get) if pathway_scores else None
        peak = pathway_scores.get(highest, 0.0) if highest else 0.0
        stale = tuple(
            sorted(
                item.signal_id
                for item in scoreable
                if item.review_due is not None and item.review_due < review_date
            )
        )
        covered = set(pathway_scores)
        uncovered = tuple(path for path in RiskPathway if path not in covered)
        top = tuple(
            (item.signal_id, item.pressure_score)
            for item in sorted(
                scoreable,
                key=lambda item: item.pressure_score,
                reverse=True,
            )[:top_n]
        )
        return RiskSnapshot(
            as_of=review_date,
            pressure_index=round(peak, 2),
            band=self._band(peak),
            highest_pressure_pathway=highest,
            scoreable_signal_count=len(scoreable),
            mitigated_signal_count=sum(
                item.state is SignalState.MITIGATED for item in self.signals
            ),
            disputed_signal_count=sum(
                item.state is SignalState.DISPUTED for item in self.signals
            ),
            stale_signal_ids=stale,
            uncovered_pathways=uncovered,
            pathway_scores={
                pathway.value: round(score, 2)
                for pathway, score in sorted(pathway_scores.items(), key=lambda item: item[0].value)
            },
            top_signals=top,
        )

    def report(self, *, as_of: date | None = None) -> str:
        snapshot = self.snapshot(as_of=as_of)
        lines = [
            "ARK EXISTENTIAL-RISK OBSERVATORY",
            f"As of: {snapshot.as_of.isoformat()}",
            (
                f"Signal pressure: {snapshot.pressure_index:.1f}/100 "
                f"[{snapshot.band.value.upper()}]"
            ),
            "Peak pathway: "
            + (
                snapshot.highest_pressure_pathway.value
                if snapshot.highest_pressure_pathway
                else "none"
            ),
            f"Tracked signals: {snapshot.scoreable_signal_count}",
            f"Stale reviews: {len(snapshot.stale_signal_ids)}",
            "",
            "Pathway pressure:",
        ]
        for pathway, score in snapshot.pathway_scores.items():
            lines.append(f"  {pathway:32s} {score:5.1f}/100")
        lines.extend(["", "Top evidence signals:"])
        signal_map = {item.signal_id: item for item in self.signals}
        for signal_id, score in snapshot.top_signals:
            signal = signal_map[signal_id]
            lines.append(
                f"  {score:5.1f}  {signal.title} "
                f"({signal.evidence_kind.value}; strength {signal.evidence_strength}/5)"
            )
            lines.append(f"         {signal.source_name}: {signal.source_url}")
        lines.extend(["", "Expert probability judgments (not part of the score):"])
        for forecast in self.forecast_book.forecasts:
            if forecast.qualifier is ForecastQualifier.ABOVE:
                estimate = f"> {forecast.lower_probability:.0%}"
            elif forecast.qualifier is ForecastQualifier.RANGE:
                estimate = (
                    f"{forecast.lower_probability:.0%}–{forecast.upper_probability:.0%}"
                )
            else:
                estimate = f"{forecast.lower_probability:.0%}"
            lines.append(
                f"  {forecast.forecaster}: {estimate} over {forecast.horizon_years} years "
                f"({forecast.published_on.isoformat()}; {forecast.source_name})"
            )
        lines.extend(
            [
                "",
                "Uncovered pathways: "
                + (", ".join(item.value for item in snapshot.uncovered_pathways) or "none"),
                snapshot.disclaimer,
                "Bands are descriptive operating thresholds, not calibrated risk categories.",
                "A missing signal is not evidence that a pathway is safe.",
            ]
        )
        return "\n".join(lines)


def main() -> None:
    """Print the default evidence ledger and current pressure snapshot."""
    print(RiskObservatory.from_default_data().report())


__all__ = [
    "EvidenceKind",
    "ExpertForecast",
    "ForecastBook",
    "ForecastConsensus",
    "ForecastQualifier",
    "PressureBand",
    "RiskObservatory",
    "RiskPathway",
    "RiskSignal",
    "RiskSnapshot",
    "SignalState",
    "brier_score",
]


if __name__ == "__main__":
    main()
