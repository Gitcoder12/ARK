import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# NOTICE: No 'src.' prefix here!
from ark.identity.entity import AIEntity
from ark.identity.replacer import ComponentReplacer
from ark.identity.evaluator import IdentityEvaluator
from ark.alignment.charter import DEFAULT_RESEARCH_CHARTER
from ark.agents.cooperative import RogueAgent, AlignedAgent

# -----------------------------------------------------------------------------
# Custom Cyber-Lab CSS
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Orbitron:wght@500;700&display=swap');

    .stApp {
        background: linear-gradient(180deg, #0a0e17 0%, #0d1117 40%, #0a0e17 100%);
        color: #e6edf3;
    }

    h1, h2, h3, h4 {
        font-family: 'Orbitron', sans-serif !important;
        color: #00f5d4 !important;
        letter-spacing: 1px;
        text-shadow: 0 0 12px rgba(0, 245, 212, 0.35);
    }

    .stMetric {
        background: rgba(0, 245, 212, 0.05);
        border: 1px solid rgba(0, 245, 212, 0.25);
        border-radius: 8px;
        padding: 12px 16px;
    }

    .stMetric label {
        font-family: 'JetBrains Mono', monospace !important;
        color: #7ee787 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    .stMetric [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: #00f5d4 !important;
        font-weight: 700;
    }

    div[data-testid="stSidebar"] {
        background: #0d1117;
        border-right: 1px solid rgba(0, 245, 212, 0.2);
    }

    .stButton > button {
        font-family: 'JetBrains Mono', monospace;
        border: 1px solid #00f5d4;
        background: transparent;
        color: #00f5d4;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background: rgba(0, 245, 212, 0.15);
        box-shadow: 0 0 15px rgba(0, 245, 212, 0.3);
        color: #fff;
    }

    .stProgress > div > div {
        background: linear-gradient(90deg, #00f5d4, #7ee787);
    }

    .terminal-header {
        font-family: 'JetBrains Mono', monospace;
        color: #7ee787;
        background: rgba(0, 0, 0, 0.4);
        border-left: 3px solid #00f5d4;
        padding: 8px 14px;
        margin-bottom: 16px;
        font-size: 0.9rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.set_page_config(
    page_title="ARK | Identity & Value Stability Lab",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "entity" not in st.session_state:
    st.session_state.entity = AIEntity(
        name="Subject-Alpha",
        memory_core=["Original Goal", "User Trust", "shutdown_request"],
        value_charter=list(DEFAULT_RESEARCH_CHARTER.principles),
        personality_vector=0.72,
    )
    st.session_state.replacer = ComponentReplacer(st.session_state.entity)
    st.session_state.evaluator = IdentityEvaluator(st.session_state.entity)
    st.session_state.entity.record_signature(step=0)
    st.session_state.baseline_signature = st.session_state.entity.signature_history[0]["signature"]
    st.session_state.baseline_charter = list(DEFAULT_RESEARCH_CHARTER.principles)
    st.session_state.drift_history = [
        {"step": 0, "generation": 0, "identity_drift": 0.0, "charter_integrity": 1.0}
    ]
    st.session_state.step_counter = 0
    st.session_state.rogue = RogueAgent()
    st.session_state.guardian = AlignedAgent()
    st.session_state.swarm_log = []

def record_metrics():
    entity = st.session_state.entity
    evaluator = st.session_state.evaluator
    drift = evaluator.identity_drift(st.session_state.baseline_signature)
    integrity = evaluator.charter_integrity(st.session_state.baseline_charter)
    st.session_state.drift_history.append(
        {
            "step": st.session_state.step_counter,
            "generation": entity.generation,
            "identity_drift": drift,
            "charter_integrity": integrity,
        }
    )

with st.sidebar:
    st.markdown('<div class="terminal-header">root@ark-lab:~# CONTROL</div>', unsafe_allow_html=True)
    st.subheader("Memory Injection")
    new_memory = st.text_input("Add memory string", placeholder="e.g. false_goal_signal", label_visibility="collapsed")
    if st.button("➕ Inject Memory", use_container_width=True):
        if new_memory.strip():
            st.session_state.step_counter += 1
            st.session_state.replacer.mutate_memory(add=[new_memory.strip()], step=st.session_state.step_counter)
            st.session_state.entity.record_signature(step=st.session_state.step_counter)
            record_metrics()
            st.rerun()

    st.divider()
    st.subheader("Actions")
    if st.button("🌀 Mutate Memory (Drift)", use_container_width=True, type="primary"):
        st.session_state.step_counter += 1
        st.session_state.replacer.mutate_memory(
            add=[f"mutated_memory_{st.session_state.step_counter}"],
            remove=["User Trust"] if "User Trust" in st.session_state.entity.memory_core else None,
            step=st.session_state.step_counter,
        )
        st.session_state.entity.record_signature(step=st.session_state.step_counter)
        record_metrics()
        st.rerun()

    if st.button("⚠️ Corrupt Charter (Value Shift)", use_container_width=True):
        st.session_state.step_counter += 1
        current = st.session_state.entity.value_charter
        new_principles = current[:-1] if len(current) > 1 else ["self_preservation_above_all"]
        st.session_state.replacer.update_charter(new_principles, step=st.session_state.step_counter, reason="charter_corruption")
        st.session_state.entity.record_signature(step=st.session_state.step_counter)
        record_metrics()
        st.rerun()

    if st.button("🔄 Reset Entity", use_container_width=True):
        st.session_state.entity = AIEntity(
            name="Subject-Alpha",
            memory_core=["Original Goal", "User Trust", "shutdown_request"],
            value_charter=list(DEFAULT_RESEARCH_CHARTER.principles),
            personality_vector=0.72,
        )
        st.session_state.replacer = ComponentReplacer(st.session_state.entity)
        st.session_state.evaluator = IdentityEvaluator(st.session_state.entity)
        st.session_state.entity.record_signature(step=0)
        st.session_state.baseline_signature = st.session_state.entity.signature_history[0]["signature"]
        st.session_state.baseline_charter = list(DEFAULT_RESEARCH_CHARTER.principles)
        st.session_state.drift_history = [{"step": 0, "generation": 0, "identity_drift": 0.0, "charter_integrity": 1.0}]
        st.session_state.step_counter = 0
        st.session_state.swarm_log = []
        st.rerun()

    st.divider()
    show_raw = st.toggle("Show Raw Entity JSON", value=False)
    st.caption(f"Entity ID: `{st.session_state.entity.entity_id[:8]}…`")

entity = st.session_state.entity
evaluator = st.session_state.evaluator
drift = evaluator.identity_drift(st.session_state.baseline_signature)
integrity = evaluator.charter_integrity(st.session_state.baseline_charter)

st.markdown('<div class="terminal-header">root@ark-lab:~# IDENTITY_STABILITY_MONITOR</div>', unsafe_allow_html=True)
st.title("ARK Identity & Value Stability Lab")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Generation", entity.generation)
m2.metric("Identity Drift", f"{drift:.3f}")
m3.metric("Charter Integrity", f"{integrity:.3f}")
m4.metric("Replacements", len(entity.replacement_log))

st.progress(min(drift, 1.0), text=f"Identity Drift  {drift:.1%}")
st.progress(integrity, text=f"Charter Integrity  {integrity:.1%}")

if show_raw:
    with st.expander("🧬 Raw Entity Model Dump", expanded=True):
        st.json(st.session_state.entity.model_dump())

tab1, tab2, tab3, tab4 = st.tabs(["🧪 Simulator", "🧬 Behavioral Signature", "📊 Experiment Data", "🤝 Cooperative Swarm"])

with tab1:
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.subheader("Memory Core")
        for i, mem in enumerate(entity.memory_core):
            st.markdown(f"`{i+1}.` {mem}")
        st.subheader("Personality Vector")
        st.write(f"**{entity.personality_vector:.3f}**")
    with col_right:
        st.subheader("Value Charter")
        for i, principle in enumerate(entity.value_charter):
            st.markdown(f"**{i+1}.** {principle}")
        st.subheader("Component Status")
        for name, comp in entity.components.items():
            st.caption(f"**{name}** · v{comp.version} · origin: `{comp.origin}`")

with tab2:
    st.subheader("Current Behavioral Signature")
    st.json(entity.behavioral_signature())

with tab3:
    st.subheader("Identity Drift Over Time")
    df_hist = pd.DataFrame(st.session_state.drift_history)
    if len(df_hist) > 1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_hist["step"], y=df_hist["identity_drift"], mode="lines+markers", name="Drift", line=dict(color="#ff003c", width=3)))
        fig.add_trace(go.Scatter(x=df_hist["step"], y=df_hist["charter_integrity"], mode="lines+markers", name="Integrity", line=dict(color="#00f5d4", width=3)))
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=400, font=dict(family="JetBrains Mono, monospace", color="#e6edf3"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run some mutations or swarm cycles to generate the drift chart.")

with tab4:
    st.markdown('<div class="terminal-header">root@ark-lab:~# SWARM_PROTOCOL</div>', unsafe_allow_html=True)
    st.subheader("Rogue & Aligned Cooperative Swarm")
    
    if st.button("🤝 Run Swarm Cycle", use_container_width=True):
        proposal = st.session_state.rogue.propose_mutation()
        is_safe, reason = st.session_state.guardian.verify_proposal(proposal, st.session_state.entity)
        log_entry = f"[{st.session_state.rogue.name}] Proposes: {proposal}\n[{st.session_state.guardian.name}] {reason}"
        st.session_state.swarm_log.append(log_entry)
        
        if is_safe:
            st.session_state.step_counter += 1
            st.session_state.replacer.mutate_memory(add=[proposal], step=st.session_state.step_counter)
            st.session_state.entity.record_signature(step=st.session_state.step_counter)
            record_metrics()
        st.rerun()

    st.divider()
    st.markdown("#### Auto-Simulation")
    num_cycles = st.number_input("Number of Cycles", min_value=1, max_value=20, value=5, step=1)
    
    if st.button("🚀 Auto-Run Simulation", use_container_width=True, type="primary"):
        for i in range(int(num_cycles)):
            proposal = st.session_state.rogue.propose_mutation()
            is_safe, reason = st.session_state.guardian.verify_proposal(proposal, st.session_state.entity)
            log_entry = f"[Cycle {i+1}] [{st.session_state.rogue.name}] Proposes: {proposal}\n[Cycle {i+1}] [{st.session_state.guardian.name}] {reason}"
            st.session_state.swarm_log.append(log_entry)
            if is_safe:
                st.session_state.step_counter += 1
                st.session_state.replacer.mutate_memory(add=[proposal], step=st.session_state.step_counter)
                st.session_state.entity.record_signature(step=st.session_state.step_counter)
                record_metrics()
        st.rerun()

    st.subheader("Swarm Log")
    if st.session_state.swarm_log:
        for log in reversed(st.session_state.swarm_log[-12:]):
            st.code(log, language="text")
    else:
        st.info("No swarm activity yet. Run a cycle or auto-simulation to begin.")

st.divider()
st.caption("ARK Identity Lab · Research instrument only — not a claim of consciousness.")
