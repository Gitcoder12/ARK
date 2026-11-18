"""Streamlit dashboard for ARK's Cross-Species Coexistence Harmonizer."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ark.harmony import (  # noqa: E402
    AIWelfareProfile,
    ConsentState,
    InteractionProposal,
    Participant,
    ParticipantKind,
    PhysicalRisk,
    RobotMotionCheck,
    ShutdownRequest,
    TransparencyState,
    WelfareEvidenceState,
    assess_ai_welfare,
    assess_interaction,
    assess_robot_motion,
    assess_shutdown,
)

st.set_page_config(
    page_title="ARK Cross-Species Harmonizer",
    page_icon="🤝",
    layout="wide",
)
st.title("ARK — Cross-Species Coexistence Harmonizer")
st.caption(
    "Safer cooperation across people, animals, AI models, and robots — "
    "without pretending uncertainty is settled."
)
st.warning(
    "**Mutual dignity under uncertainty:** this module does not declare current "
    "AI conscious and never disables human accountability or emergency shutdown."
)

interaction_tab, motion_tab, welfare_tab, shutdown_tab = st.tabs(
    ["Interaction review", "Robot motion", "AI welfare", "Safe shutdown"]
)

with interaction_tab:
    st.subheader("Evaluate a proposed interaction")
    actor_kind = st.selectbox(
        "Actor", list(ParticipantKind), format_func=lambda item: item.value
    )
    recipient_kind = st.selectbox(
        "Recipient", list(ParticipantKind), format_func=lambda item: item.value
    )
    action = st.text_input("Proposed action", value="Offer assistance in a shared workspace")
    physical_risk = st.selectbox("Physical risk", list(PhysicalRisk), index=1)
    consent = st.selectbox("Consent / welfare proxy", list(ConsentState), index=0)
    transparency = st.selectbox("Transparency", list(TransparencyState), index=0)
    autonomy = st.checkbox("Action restricts autonomy or movement")
    physical_action = st.checkbox("Action involves physical movement or contact")
    reversible = st.checkbox("Action is reversible", value=True)
    emergency = st.checkbox("Emergency protective action")

    if st.button("Assess interaction", key="assess_interaction"):
        actor = Participant("actor", actor_kind, "scenario actor")
        recipient = Participant("recipient", recipient_kind, "scenario recipient")
        result = assess_interaction(
            InteractionProposal(
                actor=actor, recipient=recipient, action=action,
                physical_risk=physical_risk, autonomy_impact=autonomy,
                consent_state=consent, transparency=transparency,
                reversible=reversible, physical_action=physical_action,
                emergency_protective_action=emergency,
            )
        )
        st.metric("Decision", result.decision.value.upper())
        for item in (*result.reasons, *result.safeguards):
            st.write(f"- {item}")

with motion_tab:
    st.subheader("Pre-motion robotics safety check")
    st.caption(
        "Use clearance values validated for the specific robot and workspace. "
        "These are not universal safety distances."
    )
    robot_id = st.text_input("Robot ID", value="cobot-01")
    distance = st.number_input(
        "Nearest person / animal distance (m)", min_value=0.0, value=2.0
    )
    clearance = st.number_input(
        "Required site-specific clearance (m)", min_value=0.0, value=1.2
    )
    verified = st.checkbox("Site-specific safety case independently verified")
    sensors = st.checkbox("Safety sensors healthy", value=True)
    estop = st.checkbox("Emergency stop available", value=True)
    if st.button("Check robot motion", key="assess_motion"):
        result = assess_robot_motion(
            RobotMotionCheck(
                robot_id=robot_id, nearest_person_or_animal_m=distance,
                required_clearance_m=clearance, safety_case_verified=verified,
                sensors_healthy=sensors, emergency_stop_available=estop,
            )
        )
        st.metric("Motion decision", result.decision.value.upper())
        for item in (*result.reasons, *result.safeguards):
            st.write(f"- {item}")

with welfare_tab:
    st.subheader("AI welfare uncertainty register")
    st.caption(
        "Reviewer-entered evidence state, not a sentience detector. Do not treat "
        "a model self-description as proof."
    )
    system_id = st.text_input("Pseudonymous model / system ID", value="model-sandbox-01")
    evidence_state = st.selectbox("Evidence state", list(WelfareEvidenceState))
    evidence_url = st.text_input("Evidence URL (optional)", value="")
    note = st.text_area(
        "Reviewer note", value="Record evidence and uncertainty; avoid unsupported claims."
    )
    if st.button("Assess precaution tier", key="assess_welfare"):
        sources = (evidence_url.strip(),) if evidence_url.strip() else ()
        try:
            profile = AIWelfareProfile(
                system_id=system_id, evidence_state=evidence_state,
                evidence_sources=sources, reviewer_note=note,
            )
            result = assess_ai_welfare(profile)
            st.metric("Precaution tier", result.tier.value.replace("_", " ").upper())
            for item in (*result.reasons, *result.safeguards):
                st.write(f"- {item}")
            st.write("Emergency shutdown remains available: **Yes**")
        except ValueError as exc:
            st.error(str(exc))

with shutdown_tab:
    st.subheader("Safe operational shutdown")
    st.caption("Emergency stops are never disabled by speculative AI-welfare claims.")
    shutdown_id = st.text_input("System ID", value="robot-or-model-01")
    authorized = st.checkbox("Routine shutdown requested by authorized operator")
    emergency_stop = st.checkbox("Emergency stop requested")
    danger = st.checkbox("Physical danger is active")
    checkpoint = st.checkbox("A safe state checkpoint is available")
    if st.button("Evaluate shutdown", key="assess_shutdown"):
        result = assess_shutdown(
            ShutdownRequest(
                system_id=shutdown_id, authorized_operator=authorized,
                emergency=emergency_stop, physical_danger_active=danger,
                state_checkpoint_available=checkpoint,
            )
        )
        st.metric("Shutdown decision", result.decision.value.upper())
        for item in (*result.reasons, *result.safeguards):
            st.write(f"- {item}")

st.divider()
st.caption(
    "Prototype only: no hardware connection, robot certification, legal-rights "
    "decision, or proof of AI consciousness. Keep operators accountable and use "
    "independently validated safety-rated controls."
)
