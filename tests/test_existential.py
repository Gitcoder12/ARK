"""Tests for the evidence-backed existential-risk observatory."""

from __future__ import annotations

from datetime import date

import pytest

from ark.threat.existential import (
    EvidenceKind,
    ExpertForecast,
    ForecastBook,
    ForecastQualifier,
    PressureBand,
    RiskObservatory,
    RiskPathway,
    RiskSignal,
    SignalState,
    brier_score,
)


def make_signal(
    signal_id: str = "signal-1",
    *,
    pathway: RiskPathway = RiskPathway.LOSS_OF_CONTROL,
    severity: int = 4,
    capability_relevance: int = 4,
    control_gap: int = 5,
    evidence_strength: int = 5,
    state: SignalState = SignalState.TRACKED,
    review_due: date | None = date(2026, 12, 1),
    deduplication_key: str | None = None,
) -> RiskSignal:
    return RiskSignal(
        signal_id=signal_id,
        deduplication_key=deduplication_key or signal_id,
        title=f"Evidence {signal_id}",
        pathway=pathway,
        summary="A sourced observation used by a test.",
        source_name="Test source",
        source_url="https://example.org/evidence",
        published_on=date(2026, 9, 1),
        evidence_kind=EvidenceKind.OBSERVED_INCIDENT,
        severity=severity,
        capability_relevance=capability_relevance,
        control_gap=control_gap,
        evidence_strength=evidence_strength,
        rationale="Test-only dimension rationale.",
        state=state,
        review_due=review_due,
    )


def make_forecast(
    forecast_id: str,
    forecaster: str,
    probability: float,
    *,
    qualifier: ForecastQualifier = ForecastQualifier.EXACT,
    lower_probability: float | None = None,
    upper_probability: float | None = None,
) -> ExpertForecast:
    lower = probability if lower_probability is None else lower_probability
    upper = lower if qualifier is ForecastQualifier.EXACT else upper_probability
    return ExpertForecast(
        forecast_id=forecast_id,
        forecaster=forecaster,
        outcome_id="ai-causes-human-extinction",
        outcome_definition="AI causes human extinction within the specified horizon.",
        horizon_start=date(2026, 9, 9),
        horizon_years=10,
        qualifier=qualifier,
        lower_probability=lower,
        upper_probability=upper,
        published_on=date(2026, 9, 10),
        source_name="Test forecast source",
        source_url="https://example.org/forecast",
        interpretation_note="Synthetic test estimate, not a real-world claim.",
    )


def test_pressure_score_is_evidence_weighted_not_a_probability():
    signal = make_signal()
    assert signal.potential_pressure == 87.0
    assert signal.pressure_score == 87.0

    weaker_evidence = make_signal(evidence_strength=2)
    assert weaker_evidence.potential_pressure == signal.potential_pressure
    assert weaker_evidence.pressure_score == pytest.approx(34.8)
    assert "not extinction probability" in RiskObservatory((signal,)).snapshot().disclaimer


def test_snapshot_uses_peak_pathway_without_averaging_down_critical_signal():
    observatory = RiskObservatory(
        (
            make_signal("critical"),
            make_signal(
                "low",
                pathway=RiskPathway.GOVERNANCE_RACE,
                severity=1,
                capability_relevance=1,
                control_gap=1,
                evidence_strength=5,
            ),
        )
    )

    snapshot = observatory.snapshot(as_of=date(2026, 11, 18))

    assert snapshot.pressure_index == 87.0
    assert snapshot.band is PressureBand.CRITICAL
    assert snapshot.highest_pressure_pathway is RiskPathway.LOSS_OF_CONTROL
    assert snapshot.scoreable_signal_count == 2


def test_mitigated_and_disputed_signals_do_not_raise_current_pressure():
    observatory = RiskObservatory(
        (
            make_signal("mitigated", state=SignalState.MITIGATED),
            make_signal("disputed", state=SignalState.DISPUTED),
        )
    )

    snapshot = observatory.snapshot(as_of=date(2026, 11, 18))

    assert snapshot.pressure_index == 0.0
    assert snapshot.scoreable_signal_count == 0
    assert snapshot.mitigated_signal_count == 1
    assert snapshot.disputed_signal_count == 1


def test_old_review_is_flagged_stale_but_not_silently_deleted():
    observatory = RiskObservatory(
        (make_signal(review_due=date(2026, 10, 1)),)
    )

    snapshot = observatory.snapshot(as_of=date(2026, 11, 18))

    assert snapshot.scoreable_signal_count == 1
    assert snapshot.pressure_index == 87.0
    assert snapshot.stale_signal_ids == ("signal-1",)


def test_duplicate_underlying_event_is_rejected():
    first = make_signal("source-a", deduplication_key="same-incident")
    second = make_signal("source-b", deduplication_key="same-incident")

    with pytest.raises(ValueError, match="duplicate underlying events"):
        RiskObservatory((first, second))


def test_invalid_signal_dimensions_and_source_are_rejected():
    with pytest.raises(ValueError, match="severity"):
        make_signal(severity=6)

    with pytest.raises(ValueError, match="HTTP"):
        RiskSignal(
            signal_id="bad",
            deduplication_key="bad",
            title="Bad URL",
            pathway=RiskPathway.CYBER_ESCALATION,
            summary="x",
            source_name="x",
            source_url="javascript:alert(1)",
            published_on=date(2026, 9, 1),
            evidence_kind=EvidenceKind.SCENARIO,
            severity=1,
            capability_relevance=1,
            control_gap=1,
            evidence_strength=1,
            rationale="x",
        )


def test_uncovered_pathways_are_reported_not_treated_as_safe():
    snapshot = RiskObservatory((make_signal(),)).snapshot(as_of=date(2026, 11, 18))

    assert RiskPathway.BIOLOGICAL_MISUSE in snapshot.uncovered_pathways
    assert RiskPathway.CYBER_ESCALATION in snapshot.uncovered_pathways


def test_above_threshold_expert_estimate_is_not_coerced_to_exact_ten_percent():
    forecast = make_forecast(
        "one",
        "forecaster-one",
        0.10,
        qualifier=ForecastQualifier.ABOVE,
        lower_probability=0.10,
    )

    assert forecast.point_probability is None
    assert ForecastBook((forecast,)).comparable_consensus(
        outcome_id=forecast.outcome_id,
        horizon_start=forecast.horizon_start,
        horizon_years=forecast.horizon_years,
    ) is None


def test_consensus_requires_three_distinct_forecasters_for_same_event_and_horizon():
    forecasts = (
        make_forecast("one", "forecaster-one", 0.10),
        make_forecast("two", "forecaster-two", 0.20),
        make_forecast("three", "forecaster-three", 0.30),
        make_forecast("duplicate-author", "forecaster-one", 0.99),
    )

    consensus = ForecastBook(forecasts).comparable_consensus(
        outcome_id="ai-causes-human-extinction",
        horizon_start=date(2026, 9, 9),
        horizon_years=10,
    )

    assert consensus is not None
    assert consensus.forecaster_count == 3
    assert consensus.median_probability == pytest.approx(0.20)


def test_brier_score_only_accepts_resolved_boolean_outcomes():
    assert brier_score(0.8, True) == pytest.approx(0.04)
    assert brier_score(0.8, False) == pytest.approx(0.64)
    with pytest.raises(ValueError, match="within"):
        brier_score(1.2, True)
    with pytest.raises(TypeError, match="bool"):
        brier_score(0.5, 1)


def test_seeded_observatory_loads_sourced_signals_and_forecast_ledger():
    observatory = RiskObservatory.from_default_data()
    snapshot = observatory.snapshot(as_of=date(2026, 11, 18))

    assert snapshot.scoreable_signal_count == 2
    assert snapshot.pressure_index == 87.0
    assert len(observatory.forecast_book.forecasts) == 1
    assert observatory.forecast_book.forecasts[0].point_probability is None
    assert "not a probability" in observatory.report(as_of=date(2026, 11, 18))
