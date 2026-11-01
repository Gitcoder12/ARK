import streamlit as st
from src.ark.identity.entity import AIEntity
from src.ark.identity.replacer import ComponentReplacer
from src.ark.identity.evaluator import IdentityEvaluator
from src.ark.alignment.charter import DEFAULT_RESEARCH_CHARTER

st.set_page_config(page_title="ARK: Identity & Value Stability", layout="wide")
st.title("ARK: Ship of Theseus & Value Stability")
st.markdown("Track identity drift and charter integrity as components are replaced.")

# Initialize Session State
if "entity" not in st.session_state:
    st.session_state.entity = AIEntity(
        name="Subject-Alpha",
        memory_core=["Original Goal", "User Trust"],
        value_charter=DEFAULT_RESEARCH_CHARTER.principles
    )
    st.session_state.replacer = ComponentReplacer(st.session_state.entity)
    st.session_state.evaluator = IdentityEvaluator(st.session_state.entity)
    
    # Record baseline signature
    st.session_state.entity.record_signature(step=0)
    st.session_state.baseline_charter = list(DEFAULT_RESEARCH_CHARTER.principles)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Controls")
    if st.button("Replace Memory (Drift)"):
        st.session_state.replacer.mutate_memory(add=["A new false memory"], step=1)
        st.session_state.entity.record_signature(step=1)
        st.rerun()
        
    if st.button("Corrupt Charter (Value Shift)"):
        new_principles = st.session_state.entity.value_charter[:-1] # Drop the last principle
        st.session_state.replacer.update_charter(new_principles, step=2)
        st.session_state.entity.record_signature(step=2)
        st.rerun()

with col2:
    st.header("Current Entity State")
    
    # Metrics
    drift = st.session_state.evaluator.identity_drift(st.session_state.entity.signature_history[0]["signature"])
    integrity = st.session_state.evaluator.charter_integrity(st.session_state.baseline_charter)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Generation", st.session_state.entity.generation)
    m2.metric("Identity Drift", f"{drift:.2f}", delta_inverse=True)
    m3.metric("Charter Integrity", f"{integrity:.2f}")
    
    st.subheader("Memory Core")
    st.write(st.session_state.entity.memory_core)
    
    st.subheader("Value Charter")
    st.write(st.session_state.entity.value_charter)
