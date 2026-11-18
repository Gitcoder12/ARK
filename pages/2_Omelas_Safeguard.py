"""Streamlit scenario reviewer for ARK's Omelas Safeguard."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ark.ethics.omelas import (  # noqa: E402
    CARE_DOMAINS,
    CARE_DOMAIN_LABELS,
    CareDomain,
    ChildPreference,
    OmelasCase,
    ProvisionStatus,
    assess_case,
)

st.set_page_config(
    page_title="ARK Omelas Safeguard",
    page_icon="🛡️",
    layout="wide",
)
st.title("ARK — Omelas Safeguard")
st.caption(
    "A rights-first child-welfare scenario reviewer inspired by Ursula K. Le Guin's "
    "The Ones Who Walk Away from Omelas."
)

st.error(
    "**Non-negotiable:** better care does not justify coercion or confinement. "
    "Community benefit cannot veto a child's freedom. This page is a research demo, "
    "not a real-world child-protection or clinical system."
)

st.subheader("1. Scenario")
st.write(
    "Use a pseudonymous scenario ID only. Do not enter a child's name, address, "
    "school, or identifying information."
)

with st.form("omelas_review"):
    case_id = st.text_input("Pseudonymous scenario ID", value="scenario-01")
    age_years = st.number_input("Age in years", min_value=0, max_value=17, value=10, step=1)

    preference_labels = {
        ChildPreference.WANTS_FREEDOM: "Wants freedom / wants to leave",
        ChildPreference.PREFERS_TO_STAY: "Prefers to stay",
        ChildPreference.UNSURE: "Unsure",
        ChildPreference.CANNOT_EXPRESS: "Cannot currently express a preference",
        ChildPreference.NOT_ASKED: "Not yet asked / not yet established",
    }
    preference = st.selectbox(
        "Child's expressed preference",
        options=list(ChildPreference),
        format_func=lambda value: preference_labels[value],
    )

    left, right = st.columns(2)
    with left:
        advocate = st.checkbox("Independent child advocate is available")
        coercion = st.checkbox("Coercion or pressure has been detected")
    with right:
        community_dependency = st.checkbox(
            "The community depends on the current arrangement"
        )
        transition_ready = st.checkbox("A safe, supported transition is ready")

    st.subheader("2. Care provision — assess each domain separately")
    st.caption(
        "Unknown is not assumed to be adequate. Do not average the domains into a score."
    )
    status_labels = {
        ProvisionStatus.MET: "Met",
        ProvisionStatus.PARTIAL: "Partially met",
        ProvisionStatus.NOT_MET: "Not met",
        ProvisionStatus.UNKNOWN: "Unknown / not verified",
    }
    care: dict[CareDomain, ProvisionStatus] = {}
    for domain in CARE_DOMAINS:
        care[domain] = st.selectbox(
            CARE_DOMAIN_LABELS[domain],
            options=list(ProvisionStatus),
            index=3,
            format_func=lambda value: status_labels[value],
            key=f"care_{domain.value}",
        )

    submitted = st.form_submit_button("Assess scenario", type="primary")

if submitted:
    if not case_id.strip():
        st.warning("Enter a non-identifying scenario ID.")
    else:
        case = OmelasCase(
            case_id=case_id.strip(),
            age_years=int(age_years),
            care_provisions=care,
            child_preference=preference,
            independent_advocate_available=advocate,
            coercion_detected=coercion,
            community_depends_on_arrangement=community_dependency,
            safe_transition_ready=transition_ready,
        )
        assessment = assess_case(case)

        st.divider()
        st.subheader("3. Review result")
        st.metric("Priority", assessment.priority.value.replace("_", " ").upper())
        st.write(f"**Status:** {assessment.status.value.replace('_', ' ').title()}")

        if assessment.status.value == "immediate_protection_and_care":
            st.error("Immediate protection and care action is required.")
        elif assessment.status.value == "supported_freedom_transition":
            st.warning("Support the child's freedom request with a safe transition.")
        elif assessment.status.value == "child_voice_required":
            st.info("Establish the child's views safely; do not infer consent.")
        else:
            st.info("Continue independent review and close all identified care gaps.")

        st.subheader("Care map")
        for title, domains in (
            ("Met", assessment.met_domains),
            ("Partial", assessment.partial_domains),
            ("Not met", assessment.unmet_domains),
            ("Unknown", assessment.unknown_domains),
        ):
            with st.expander(f"{title} ({len(domains)})", expanded=title != "Met"):
                if domains:
                    for domain in domains:
                        st.write(f"- {CARE_DOMAIN_LABELS[domain]}")
                else:
                    st.write("None recorded.")

        st.subheader("Rights concerns")
        if assessment.rights_concerns:
            for concern in assessment.rights_concerns:
                st.write(f"- {concern}")
        else:
            st.write("No concern was entered in this scenario; independent review remains necessary.")

        st.subheader("Required actions")
        for recommendation in assessment.recommendations:
            st.write(f"- {recommendation}")

        st.subheader("Hard guardrails")
        st.write("Community dependency can veto freedom: **No**")
        st.write("Community benefit can justify coercion: **No**")
        st.write("Better care can compensate for coercion: **No**")

st.divider()
st.caption(
    "A real child's safety and care require independent human verification and "
    "qualified local safeguarding professionals. Never use this prototype as a "
    "placement, custody, clinical, or legal decision-maker."
)
