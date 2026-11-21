"""Streamlit dashboard for ARK's evidence-backed existential-risk observatory."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ark.threat.existential import (  # noqa: E402
    ForecastQualifier,
    RiskObservatory,
)

st.set_page_config(
    page_title="ARK Existential-Risk Observatory",
    page_icon="📡",
    layout="wide",
)
st.title("ARK — Existential-Risk Observatory")
st.caption(
    "Evidence-led monitoring of AI catastrophic-risk pathways. "
    "This is not a probability forecast of human extinction."
)

observatory = RiskObservatory.from_files(
    ROOT / "data" / "existential_risk_signals.json",
    ROOT / "data" / "expert_forecasts.json",
)
snapshot = observatory.snapshot()

st.warning(
    "**Important:** Signal pressure is a prioritization index built from reviewed "
    "evidence and explicit analyst ratings. It is not a calibrated probability. "
    "Uncovered pathways are unknown, not safe."
)

left, middle, right = st.columns(3)
left.metric("Signal pressure", f"{snapshot.pressure_index:.1f}/100", snapshot.band.value.upper())
middle.metric("Tracked evidence signals", snapshot.scoreable_signal_count)
right.metric("Evidence reviews overdue", len(snapshot.stale_signal_ids))

st.progress(snapshot.pressure_index / 100.0)
peak_pathway = (
    snapshot.highest_pressure_pathway.value
    if snapshot.highest_pressure_pathway
    else "none"
)
st.caption(
    f"Peak pathway: {peak_pathway} · Snapshot date: {snapshot.as_of.isoformat()}"
)

st.subheader("Pathway pressure")
if snapshot.pathway_scores:
    for pathway, score in snapshot.pathway_scores.items():
        col1, col2 = st.columns([3, 1])
        col1.write(pathway.replace("_", " ").title())
        col2.write(f"**{score:.1f}/100**")
        col1.progress(score / 100.0)
else:
    st.info("No scoreable evidence signals have been entered yet.")

if snapshot.uncovered_pathways:
    st.info(
        "Not yet covered by the current evidence register: "
        + ", ".join(path.value.replace("_", " ") for path in snapshot.uncovered_pathways)
    )

if snapshot.stale_signal_ids:
    st.error("Evidence needing review: " + ", ".join(snapshot.stale_signal_ids))

st.subheader("Evidence register")
for signal in sorted(
    observatory.signals,
    key=lambda item: item.pressure_score,
    reverse=True,
):
    with st.expander(
        f"{signal.title} · {signal.pressure_score:.1f}/100 · {signal.state.value}"
    ):
        st.write(signal.summary)
        pathway_names = ", ".join(
            pathway.value.replace("_", " ")
            for pathway in (signal.pathway, *signal.secondary_pathways)
        )
        st.caption(
            f"Pathways: {pathway_names}"
            f" · Evidence type: {signal.evidence_kind.value.replace('_', ' ')}"
            f" · Evidence strength: {signal.evidence_strength}/5"
            f" · Published: {signal.published_on.isoformat()}"
        )
        st.caption(
            "Review due: "
            + (signal.review_due.isoformat() if signal.review_due else "not set")
        )
        st.write("**Scoring rationale**")
        st.write(signal.rationale)
        st.markdown(f"**Primary source:** [{signal.source_name}]({signal.source_url})")
        for source in signal.corroborating_sources:
            st.markdown(f"- Corroborating source: {source}")

st.subheader("Expert probability judgments — separate from the meter")
if not observatory.forecast_book.forecasts:
    st.info("No expert probability judgments recorded.")
else:
    for forecast in observatory.forecast_book.forecasts:
        if forecast.qualifier is ForecastQualifier.ABOVE:
            estimate = f"> {forecast.lower_probability:.0%}"
        elif forecast.qualifier is ForecastQualifier.RANGE:
            estimate = f"{forecast.lower_probability:.0%}–{forecast.upper_probability:.0%}"
        else:
            estimate = f"{forecast.lower_probability:.0%}"
        st.markdown(
            f"**{forecast.forecaster}: {estimate}** over {forecast.horizon_years} years "
            f"(published {forecast.published_on.isoformat()})"
        )
        st.write(forecast.interpretation_note)
        st.markdown(f"[Source: {forecast.source_name}]({forecast.source_url})")

        consensus = observatory.forecast_book.comparable_consensus(
            outcome_id=forecast.outcome_id,
            horizon_start=forecast.horizon_start,
            horizon_years=forecast.horizon_years,
        )
        if consensus is None:
            st.caption(
                "No pooled consensus: fewer than three distinct forecasters with "
                "comparable exact estimates for this event and horizon."
            )
        else:
            st.metric(
                "Median of comparable exact forecasts",
                f"{consensus.median_probability:.1%}",
                f"{consensus.forecaster_count} independent forecasters",
            )

st.caption(
    "Method: peak active pathway pressure. Severity 35%, capability relevance 30%, "
    "control gap 35%; then multiplied by evidence strength. Descriptive thresholds "
    "are not empirically calibrated. Edit the JSON evidence registers and review "
    "score rationales before updating."
)
