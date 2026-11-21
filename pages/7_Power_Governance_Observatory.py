"""ARK Power & Existential-Risk Research dashboard.

All simulations are synthetic and local. No live political, corporate, military,
or infrastructure systems are queried or controlled.
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ark.power_risk import (  # noqa: E402
    ActionRequest,
    EXPERIMENTS,
    GOVERNANCE_DOMAINS,
    HashChainLedger,
    PressureInputs,
    SCENARIOS,
    SafetyPolicy,
    simulate_pressure,
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
    "Safety controls", "Audit trail",
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

st.divider()
st.caption(
    "Research standard: distinguish observed facts, supported analysis, hypotheses "
    "and unverified claims. Record source dates, limitations, counterevidence and "
    "attribution. Do not infer motives from outcomes."
)
