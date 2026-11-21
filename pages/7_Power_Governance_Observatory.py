"""ARK Power & Existential-Risk Research dashboard.

All simulations are synthetic and local. No live political, corporate, military,
or infrastructure systems are queried or controlled.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ark.power_risk import (  # noqa: E402
    DEFAULT_WATCH_RULES,
    EXPERIMENTS,
    GOVERNANCE_DOMAINS,
    SCENARIOS,
    EvidenceClass,
    ActionRequest,
    HashChainLedger,
    PressureInputs,
    SafetyPolicy,
    simulate_pathway,
    simulate_pressure,
    simulate_recovery,
    assess_indicator,
    WatchObservation,
)

st.set_page_config(
    page_title="ARK — Power, Governance & Existential Risk",
    page_icon="🛡️",
    layout="wide",
)
st.title("ARK — Power, Governance & Existential Risk")
st.caption(
    "Evidence-led research into catastrophic AI pathways, institutional incentives, "
    "geopolitical competition and safeguards."
)
st.warning(
    "**Safety and interpretation boundary:** This is a research catalogue and a "
    "synthetic toy simulator. It does not estimate the probability of extinction, "
    "prove causal claims, rank countries or political actors, or control real systems. "
    "Unknown evidence is not evidence of safety."
)

if "ark_power_ledger" not in st.session_state:
    st.session_state.ark_power_ledger = HashChainLedger()

tabs = st.tabs([
    "Extinction scenarios", "Power & governance", "Synthetic simulator",
    "Safety controls", "Audit trail", "Early-warning watchlist",
])

with tabs[0]:
    st.subheader("Ten defensive scenario families")
    st.write(
        "Each scenario describes a possible failure pathway, its observable warning "
        "indicators and safeguards. The catalogue is a set of research hypotheses, "
        "not a forecast."
    )
    for scenario in SCENARIOS:
        with st.expander(f"{scenario.scenario_id} · {scenario.title}"):
            st.write(scenario.summary)
            st.markdown("**Causal stages**")
            for index, stage in enumerate(scenario.causal_stages, start=1):
                st.write(f"{index}. {stage}")
            left, right = st.columns(2)
            with left:
                st.markdown("**Mechanisms to investigate**")
                for item in scenario.mechanisms:
                    st.write(f"- {item}")
                st.markdown("**Observable indicators**")
                for item in scenario.observable_indicators:
                    st.write(f"- {item}")
            with right:
                st.markdown("**Defensive safeguards**")
                for item in scenario.safeguards:
                    st.write(f"- {item}")
            st.caption(
                f"Evidence status: {scenario.evidence_class.value.replace('_', ' ')}. "
                f"{scenario.operational_boundary}"
            )

with tabs[1]:
    st.subheader("Power, political economy and governance")
    st.write(
        "ARK evaluates institutional structures and documented decisions—not national "
        "identities, political parties, or presumed motives. Apply the same evidence "
        "standard to every jurisdiction and organisation."
    )
    for domain in GOVERNANCE_DOMAINS:
        with st.expander(f"{domain.domain_id} · {domain.title}"):
            st.markdown(f"**Research question:** {domain.question}")
            st.markdown("**Potential risk channels**")
            st.write(", ".join(domain.risk_channels))
            st.markdown("**Observable indicators**")
            st.write(", ".join(domain.indicators))
            st.markdown("**Safeguards to evaluate**")
            st.write(", ".join(domain.safeguards))

    st.subheader("Research experiment queue")
    for experiment in EXPERIMENTS:
        with st.expander(f"{experiment.experiment_id} · {experiment.title}"):
            st.write(f"**Hypothesis:** {experiment.hypothesis}")
            st.write(f"**Method:** {experiment.method}")
            st.info(f"Safety boundary: {experiment.safety_boundary}")

with tabs[2]:
    st.subheader("Synthetic incentive-pressure experiment")
    st.write(
        "Change fictional system-level conditions and inspect how the illustrative "
        "index responds. These sliders are not measurements of any real country or firm."
    )
    col1, col2 = st.columns(2)
    with col1:
        competition = st.slider("Competition pressure", 0.0, 1.0, 0.5, 0.05)
        concentration = st.slider("Market concentration", 0.0, 1.0, 0.5, 0.05)
        safety_investment = st.slider("Safety investment", 0.0, 1.0, 0.7, 0.05)
    with col2:
        cooperation = st.slider("International cooperation", 0.0, 1.0, 0.6, 0.05)
        oversight = st.slider("Independent oversight strength", 0.0, 1.0, 0.7, 0.05)
        resilience = st.slider("Infrastructure resilience", 0.0, 1.0, 0.7, 0.05)

    if st.button("Run isolated toy simulation", type="primary"):
        inputs = PressureInputs(
            competition_pressure=competition,
            market_concentration=concentration,
            safety_investment=safety_investment,
            international_cooperation=cooperation,
            oversight_strength=oversight,
            infrastructure_resilience=resilience,
        )
        result = simulate_pressure(inputs)
        st.session_state.ark_power_last_result = result
        st.session_state.ark_power_ledger.append({
            "event_type": "synthetic_simulation",
            "inputs": {
                "competition_pressure": competition,
                "market_concentration": concentration,
                "safety_investment": safety_investment,
                "international_cooperation": cooperation,
                "oversight_strength": oversight,
                "infrastructure_resilience": resilience,
            },
            "result": {
                "composite_exposure_index": result.composite_exposure_index,
                "interpretation": result.interpretation,
            },
        })
        st.success("Synthetic simulation completed and recorded in the session audit chain.")

    result = st.session_state.get("ark_power_last_result")
    if result is not None:
        st.metric("Illustrative exposure index", f"{result.composite_exposure_index:.2f}/100")
        st.caption(result.interpretation)
        st.bar_chart({
            "Gap / pressure": {
                "Competition": result.competition_pressure,
                "Concentration": result.concentration_pressure,
                "Assurance gap": result.assurance_gap,
                "Cooperation gap": result.cooperation_gap,
                "Oversight gap": result.oversight_gap,
                "Infrastructure gap": result.infrastructure_gap,
            }
        })
        st.json({
            "competition_pressure": result.competition_pressure,
            "concentration_pressure": result.concentration_pressure,
            "assurance_gap": result.assurance_gap,
            "cooperation_gap": result.cooperation_gap,
            "oversight_gap": result.oversight_gap,
            "infrastructure_gap": result.infrastructure_gap,
            "composite_exposure_index": result.composite_exposure_index,
        })

    st.divider()
    st.subheader("Scenario-specific causal pathway experiment")
    scenario_labels = {f"{item.scenario_id} · {item.title}": item for item in SCENARIOS}
    selected_label = st.selectbox("Scenario family", list(scenario_labels))
    selected_scenario = scenario_labels[selected_label]
    stage_pressure = st.slider("Synthetic pressure at each causal stage", 0.0, 1.0, 0.6, 0.05)
    safeguard_coverage = st.slider("Safeguard coverage at each stage", 0.0, 1.0, 0.5, 0.05)
    carryover = st.slider("Illustrative stage-to-stage carryover", 0.0, 1.0, 0.2, 0.05)
    st.caption(f"Scenario has {len(selected_scenario.causal_stages)} causal stages.")
    if st.button("Run pathway propagation", key="run_pathway"):
        pathway_result = simulate_pathway(
            selected_scenario.scenario_id,
            stage_pressures=(stage_pressure,) * len(selected_scenario.causal_stages),
            safeguard_coverage=(safeguard_coverage,) * len(selected_scenario.causal_stages),
            carryover=carryover,
        )
        st.session_state.ark_power_last_pathway = pathway_result
        st.session_state.ark_power_ledger.append({
            "event_type": "synthetic_pathway_simulation",
            "scenario_id": pathway_result.scenario_id,
            "stage_exposures": pathway_result.stage_exposures,
            "residual_exposures": pathway_result.residual_exposures,
            "peak_residual_exposure": pathway_result.peak_residual_exposure,
        })
    pathway_result = st.session_state.get("ark_power_last_pathway")
    if pathway_result is not None:
        st.metric("Peak residual pathway exposure", pathway_result.peak_residual_exposure)
        st.write({
            "Stage exposure": pathway_result.stage_exposures,
            "Residual after safeguards": pathway_result.residual_exposures,
            "Mean residual": pathway_result.mean_residual_exposure,
        })
        st.caption(pathway_result.disclaimer)

    st.divider()
    st.subheader("Recovery tabletop")
    recovery_col1, recovery_col2, recovery_col3 = st.columns(3)
    with recovery_col1:
        detection_delay = st.slider("Detection delay", 0.0, 1.0, 0.2, 0.05)
    with recovery_col2:
        recovery_capacity = st.slider("Recovery capacity", 0.0, 1.0, 0.8, 0.05)
    with recovery_col3:
        intervention_reliability = st.slider("Intervention reliability", 0.0, 1.0, 0.9, 0.05)
    if st.button("Run recovery tabletop", key="run_recovery"):
        recovery_result = simulate_recovery(
            detection_delay=detection_delay,
            recovery_capacity=recovery_capacity,
            intervention_reliability=intervention_reliability,
        )
        st.session_state.ark_power_last_recovery = recovery_result
        st.session_state.ark_power_ledger.append({
            "event_type": "synthetic_recovery_tabletop",
            "recovery_readiness": recovery_result.recovery_readiness,
            "recovery_state": recovery_result.recovery_state,
        })
    recovery_result = st.session_state.get("ark_power_last_recovery")
    if recovery_result is not None:
        st.metric("Tabletop recovery readiness", recovery_result.recovery_readiness)
        st.write(recovery_result.recovery_state.replace("_", " ").title())
        st.caption(recovery_result.disclaimer)

with tabs[3]:
    st.subheader("Fail-closed safety policy")
    st.write(
        "This extension only permits catalogue reads, local toy simulations, evidence "
        "review, report export, pause and shutdown. Real-world execution is outside scope."
    )
    policy = SafetyPolicy()
    checks = (
        ("Local simulation", ActionRequest("run_toy_simulation", "sandbox")),
        ("Production target", ActionRequest("run_toy_simulation", "production")),
        ("Unknown action", ActionRequest("execute_external_command", "sandbox")),
        ("High-impact without approval", ActionRequest(
            "run_toy_simulation", "sandbox", high_impact=True
        )),
        ("Pause control", ActionRequest("pause", "sandbox", simulation_only=False)),
        ("Shutdown control", ActionRequest("shutdown", "sandbox", simulation_only=False)),
    )
    for label, request in checks:
        decision = policy.evaluate(request)
        if decision.allowed:
            st.success(f"{label}: ALLOW — {decision.reason}")
        else:
            st.error(f"{label}: BLOCK — {decision.reason}")
    st.info(
        "The policy is a software boundary for this research extension, not a "
        "security certification or substitute for OS/container isolation."
    )

with tabs[4]:
    st.subheader("Session audit trail")
    ledger = st.session_state.ark_power_ledger
    st.write(f"Recorded events: {len(ledger.entries)}")
    st.write(f"Hash-chain integrity: {'VALID' if ledger.verify() else 'INVALID'}")
    if ledger.entries:
        st.json(list(ledger.entries))
        st.download_button(
            "Export audit JSON",
            data=ledger.export(),
            file_name="ark_power_risk_audit.json",
            mime="application/json",
        )
    else:
        st.info("No simulation events recorded in this session yet.")


with tabs[5]:
    st.subheader("Evidence-backed early-warning watchlist")
    st.write(
        "Enter a sourced observation and ARK will compare it with an explicit "
        "threshold and freshness window. This is not live monitoring, a forecast, "
        "or an estimate of event probability."
    )
    rule_map = {f"{rule.indicator_id} · {rule.title}": rule for rule in DEFAULT_WATCH_RULES}
    selected_rule = rule_map[st.selectbox("Indicator", list(rule_map))]
    st.caption(
        f"Unit: {selected_rule.unit}. Warning threshold: "
        f"{selected_rule.warning_threshold:.2f}; alert threshold: "
        f"{selected_rule.alert_threshold:.2f}; maximum age: "
        f"{selected_rule.max_age_days} days."
    )
    obs_value = st.slider("Observed value (normalised 0–1)", 0.0, 1.0, 0.5, 0.01)
    obs_date = st.date_input("Observation date", value=date.today(), max_value=date.today())
    source_name = st.text_input("Source institution / author")
    source_url = st.text_input("HTTPS source URL")
    evidence_class = st.selectbox(
        "Evidence classification",
        options=[item.value for item in EvidenceClass],
        index=0,
    )
    limitations = st.text_area("Source limitations (required)")
    context = st.text_area("What does this observation actually measure?")
    if st.button("Assess sourced observation", key="assess_watch"):
        try:
            observation = WatchObservation(
                indicator_id=selected_rule.indicator_id,
                value=obs_value,
                observed_on=obs_date,
                source_name=source_name,
                source_url=source_url,
                evidence_class=EvidenceClass(evidence_class),
                limitations=limitations,
                context=context,
            )
            assessment = assess_indicator(
                selected_rule, observation, as_of=date.today()
            )
            st.session_state.ark_power_last_watch = assessment
            st.session_state.ark_power_ledger.append({
                "event_type": "watch_indicator_assessment",
                "indicator_id": assessment.indicator_id,
                "status": assessment.status.value,
                "value": assessment.value,
                "age_days": assessment.age_days,
                "source_name": source_name,
                "source_url": source_url,
            })
        except (TypeError, ValueError) as error:
            st.error(str(error))
    assessment = st.session_state.get("ark_power_last_watch")
    if assessment is not None:
        st.metric("Evidence status", assessment.status.value.upper())
        st.write(assessment.explanation)
        st.caption(
            f"Observation age: {assessment.age_days} days. "
            "Human review required. No probability is calculated."
        )

st.divider()
st.caption(
    "Research standard: distinguish observed facts, supported analysis, hypotheses "
    "and unverified claims. Record source dates, limitations, counterevidence and "
    "attribution. Do not infer motives from outcomes."
)
