"""Identity and value-stability experiment preserved as an ARKWorld module."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ark.alignment.charter import DEFAULT_RESEARCH_CHARTER  # noqa: E402
from ark.identity.entity import AIEntity  # noqa: E402
from ark.identity.evaluator import IdentityEvaluator  # noqa: E402
from ark.identity.replacer import ComponentReplacer  # noqa: E402

st.set_page_config(page_title="ARKWorld — Identity & Value Stability", layout="wide")
st.title("Identity & Value Stability")
st.caption("Ship of Theseus experiment: track identity drift and charter integrity.")

if "entity" not in st.session_state:
    st.session_state.entity = AIEntity(
        name="Subject-Alpha",
        memory_core=["Original Goal", "User Trust"],
        value_charter=DEFAULT_RESEARCH_CHARTER.principles,
    )
    st.session_state.replacer = ComponentReplacer(st.session_state.entity)
    st.session_state.evaluator = IdentityEvaluator(st.session_state.entity)
    st.session_state.entity.record_signature(step=0)
    st.session_state.baseline_charter = list(DEFAULT_RESEARCH_CHARTER.principles)

col1, col2 = st.columns([1, 2])
with col1:
    st.header("Controls")
    if st.button("Replace Memory (Drift)"):
        st.session_state.replacer.mutate_memory(
            add=["A new false memory"], step=1
        )
        st.session_state.entity.record_signature(step=1)
        st.rerun()

    if st.button("Corrupt Charter (Value Shift)"):
        new_principles = st.session_state.entity.value_charter[:-1]
        st.session_state.replacer.update_charter(new_principles, step=2)
        st.session_state.entity.record_signature(step=2)
        st.rerun()

with col2:
    st.header("Current Entity State")
    baseline = st.session_state.entity.signature_history[0]["signature"]
    drift = st.session_state.evaluator.identity_drift(baseline)
    integrity = st.session_state.evaluator.charter_integrity(
        st.session_state.baseline_charter
    )
    metrics = st.columns(3)
    metrics[0].metric("Generation", st.session_state.entity.generation)
    metrics[1].metric("Identity Drift", f"{drift:.2f}", delta_inverse=True)
    metrics[2].metric("Charter Integrity", f"{integrity:.2f}")
    st.subheader("Memory Core")
    st.write(st.session_state.entity.memory_core)
    st.subheader("Value Charter")
    st.write(st.session_state.entity.value_charter)
