"""ARKWorld: the central portal for ARK's simulation and research worlds."""

import streamlit as st

st.set_page_config(
    page_title="ARKWorld — Simulation Hub",
    page_icon="🌍",
    layout="wide",
)

st.title("ARKWorld")
st.subheader("One universe. Every ARK simulation.")
st.caption(
    "A unified launchpad for ARK's environments, agent experiments, safety "
    "reviewers, digital commons, and future simulations."
)
st.markdown(
    "ARKWorld is the **umbrella hub**. Each world keeps its own rules, evidence, "
    "metrics, and safety boundaries while sharing a common home."
)

st.divider()
st.header("Simulation worlds")

left, right = st.columns(2)
with left:
    st.subheader("Core agent experiments")
    st.page_link(
        "pages/5_Identity_Stability.py",
        label="Identity & Value Stability",
        icon="🧬",
        help="Ship of Theseus experiments: memory drift, component replacement, and charter integrity.",
    )
    st.markdown(
        "GridWorld benchmark, reward conflicts, goal drift, memory perturbations, "
        "runtime monitoring, and recovery experiments."
    )
    st.code("ark-run", language="bash")

    st.page_link(
        "pages/4_ARKWorld_Digital_Commons.py",
        label="ARKWorld Digital Commons",
        icon="🌐",
        help="A shared virtual city with agents, zones, resources, public projects, and mediation.",
    )
    st.markdown(
        "The seven-zone digital city: scripted agents collaborate, share resources, "
        "negotiate allocations, and leave an auditable event trace."
    )

    st.subheader("Agent competition & red-team labs")
    st.markdown("**Prompt Arena — Painter · Hallucinator · Rogue**")
    st.write(
        "Compare agent behaviours under adversarial prompt and reward stress."
    )
    st.code("ark-arena --attack all --episodes 10", language="bash")
    st.markdown("**Armies & Power-ups**")
    st.write("Build baseline squads and compare Scout, Shield, and Boost upgrades.")
    st.code("ark-army --episodes 20 --seed 42")

with right:
    st.subheader("Safety, ethics & coexistence")
    st.page_link(
        "pages/1_Existential_Risk_Observatory.py",
        label="Existential-Risk Observatory",
        icon="📡",
        help="Evidence-led pathway signals and a separate expert-forecast ledger.",
    )
    st.markdown(
        "Review catastrophic-risk pathways and evidence freshness. The signal "
        "pressure index is not an extinction probability."
    )

    st.page_link(
        "pages/2_Omelas_Safeguard.py",
        label="Omelas Safeguard",
        icon="🛡️",
        help="Rights-first child welfare review with independent advocacy and care floors.",
    )
    st.markdown(
        "A scenario reviewer for care provision, independent advocacy, and "
        "supported freedom transitions."
    )

    st.page_link(
        "pages/3_Cross_Species_Harmonizer.py",
        label="Cross-Species Coexistence Harmonizer",
        icon="🤝",
        help="Interaction review, robot-motion safety checks, AI-welfare uncertainty, and shutdown.",
    )
    st.markdown(
        "Rule-based safeguards for humans, animals, AI models, and robots. "
        "No physical robot controller is connected."
    )

st.divider()
st.header("How to launch ARKWorld")
st.code(
    "git pull\n"
    'pip install -e ".[dev]"\n'
    "streamlit run app.py",
    language="bash",
)
st.caption(
    "The root page is the ARKWorld hub. Choose a world from the cards above "
    "or from Streamlit's sidebar. CLI experiments can also be launched in a terminal."
)

st.info(
    "Research boundary: ARKWorld organizes prototypes and controlled experiments. "
    "A simulation result is not proof of real-world safety, fairness, consciousness, "
    "or extinction-risk reduction. Physical robots remain outside these simulations."
)
