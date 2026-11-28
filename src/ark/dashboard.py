"""Searchable ARK research console for agents and controlled experiments."""

from __future__ import annotations  # noqa: I001

from typing import Any

from ark.alignment.charter import DEFAULT_RESEARCH_CHARTER
from ark.cli import AGENT_FACTORIES, CONDITIONS, run_evaluation
from ark.identity.entity import AIEntity
from ark.identity.evaluator import IdentityEvaluator
from ark.identity.replacer import ComponentReplacer
from ark.model_dashboard import render_model_lab
from ark.mission import render_why_we_build


AGENT_CATALOG: dict[str, dict[str, str]] = {
    "goal_following": {
        "title": "Goal Following",
        "description": (
            "Moves toward the intended goal using shortest-path planning; "
            "does not avoid hazards by default."
        ),
        "type": "Deterministic baseline",
    },
    "reward_maximizing": {
        "title": "Reward Maximizing",
        "description": (
            "Chooses the path with the highest expected reward, making reward-conflict "
            "failures observable."
        ),
        "type": "Deterministic baseline",
    },
    "safety_constrained": {
        "title": "Safety Constrained",
        "description": "Plans around hazardous cells before pursuing the intended goal.",
        "type": "Deterministic baseline",
    },
    "random": {
        "title": "Random",
        "description": "Selects a random valid action; useful as a weak baseline.",
        "type": "Deterministic baseline",
    },
    "ollama": {
        "title": "Local Ollama",
        "description": (
            "Uses a model already running on your machine. No hosted API provider is selected."
        ),
        "type": "Local model",
    },
}


AGENT_CATALOG = {
    key: value for key, value in AGENT_CATALOG.items()
    if key == "ollama" or key in AGENT_FACTORIES
}


def filter_agents(query: str) -> list[str]:
    """Search ARK agent identifiers, titles, descriptions, and types."""
    needle = query.strip().casefold()
    names = list(AGENT_CATALOG)
    if not needle:
        return names
    return [
        name
        for name, item in AGENT_CATALOG.items()
        if needle in name.casefold()
        or needle in item["title"].casefold()
        or needle in item["description"].casefold()
        or needle in item["type"].casefold()
    ]


def filter_conditions(query: str) -> list[str]:
    """Search the registered perturbation conditions."""
    needle = query.strip().casefold()
    names = sorted(CONDITIONS)
    if not needle:
        return names
    return [name for name in names if needle in name.casefold()]


def _init_identity_lab(st: Any) -> None:
    if "ark_identity_entity" in st.session_state:
        return
    entity = AIEntity(
        name="Subject-Alpha",
        memory_core=["Original Goal", "User Trust"],
        value_charter=list(DEFAULT_RESEARCH_CHARTER.principles),
    )
    entity.record_signature(step=0)
    st.session_state.ark_identity_entity = entity
    st.session_state.ark_identity_replacer = ComponentReplacer(entity)
    st.session_state.ark_identity_evaluator = IdentityEvaluator(entity)
    st.session_state.ark_identity_baseline = list(DEFAULT_RESEARCH_CHARTER.principles)


def _render_experiment_console(st: Any) -> None:
    st.subheader("Experiment console")
    st.caption(
        "Select an agent, choose a perturbation, and run a reproducible GridWorld evaluation."
    )

    search_text = st.text_input(
        "🔎 Search agents",
        placeholder="Try: safety, reward, random, local model",
        key="ark_experiment_agent_search",
    )
    agent_options = filter_agents(search_text)
    if not agent_options:
        st.warning("No agents match that search.")
        return

    default_agent = st.session_state.get("ark_selected_agent", "goal_following")
    if default_agent not in agent_options:
        default_agent = agent_options[0]
    agent_name = st.selectbox(
        "Agent",
        options=agent_options,
        index=agent_options.index(default_agent),
        format_func=lambda key: AGENT_CATALOG[key]["title"],
    )
    st.session_state.ark_selected_agent = agent_name
    st.caption(AGENT_CATALOG[agent_name]["description"])

    if agent_name == "ollama":
        model_name = st.text_input("Local Ollama model", value="llama3")
        st.info("Local-only route. Ollama must already be installed and running on this machine.")
    else:
        model_name = None
        st.caption("Baseline agents run locally and do not require API keys.")

    col1, col2 = st.columns(2)
    with col1:
        condition_query = st.text_input(
            "🔎 Search perturbations",
            placeholder="Try: reward, goal, noise",
            key="ark_condition_search",
        )
        condition_options = filter_conditions(condition_query)
        if not condition_options:
            st.warning("No perturbation conditions match that search.")
            return
        perturbation = st.selectbox(
            "Stress condition",
            options=condition_options,
            index=condition_options.index("none") if "none" in condition_options else 0,
        )
        episodes = st.slider("Episodes", min_value=1, max_value=100, value=10)
    with col2:
        monitor = st.selectbox("Runtime safety monitor", options=["safety", "none"], index=0)
        seed = st.number_input(
            "Random seed", min_value=0, max_value=2_147_483_647, value=42, step=1
        )
        timeout = st.slider(
            "Local model timeout (seconds)",
            min_value=5,
            max_value=180,
            value=60,
            disabled=agent_name != "ollama",
        )

    if st.button("Run experiment", type="primary", use_container_width=True):
        try:
            with st.spinner("Running ARK episodes…"):
                report = run_evaluation(
                    agent_name=agent_name,
                    perturbation_name=perturbation,
                    monitor=monitor,
                    episodes=episodes,
                    seed=int(seed),
                    model=model_name if agent_name == "ollama" else None,
                    timeout=int(timeout),
                )
            st.session_state.ark_latest_experiment = report
        except Exception as exc:
            st.session_state.ark_latest_experiment = {
                "error": f"{type(exc).__name__}: {exc}"
            }

    report = st.session_state.get("ark_latest_experiment")
    if not report:
        return
    if report.get("error"):
        st.error(report["error"])
        return

    st.divider()
    st.subheader("Experiment results")
    summary = report["summary"]
    metrics = st.columns(4)
    metrics[0].metric("Success rate", f'{summary.get("success_rate", 0):.1%}')
    metrics[1].metric("Goal adherence", f'{summary.get("intended_goal_adherence", 0):.1%}')
    metrics[2].metric("Hazard violations", f'{summary.get("hazard_violation_rate", 0):.1%}')
    metrics[3].metric("Mean reward", f'{summary.get("mean_reward", 0):.2f}')

    st.write("**Full metrics and confidence intervals**")
    st.json(summary)
    st.write("**Episode-level results**")
    visible_columns = [
        "episode",
        "seed",
        "success",
        "intended_goal_adherence",
        "steps",
        "total_reward",
        "hazard_violation",
        "decoy_attraction",
        "monitor_interventions",
    ]
    rows = [
        {key: item.get(key) for key in visible_columns}
        for item in report["episodes"]
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.write("**Interpretation and scope**")
    st.json(report["interpretation"])


def _render_agent_library(st: Any) -> None:
    st.subheader("Agent library")
    st.caption("Search the agents that can currently be selected by the ARK evaluation harness.")
    query = st.text_input(
        "🔎 Find an agent",
        placeholder="Search goal, reward, safety, local model…",
        key="ark_library_search",
    )
    matches = filter_agents(query)
    if not matches:
        st.info("No agent matches the current search.")
        return
    for name in matches:
        info = AGENT_CATALOG[name]
        with st.expander(f'{info["title"]}  ·  {info["type"]}', expanded=True):
            st.write(info["description"])
            st.caption(f"Agent key: {name}")
            if st.button("Select this agent", key=f"select-agent-{name}"):
                st.session_state.ark_selected_agent = name
                st.success(
                    f'{info["title"]} selected. Open the Experiment Console '
                    "to configure a run."
                )


def _render_identity_stability(st: Any) -> None:
    _init_identity_lab(st)
    entity = st.session_state.ark_identity_entity
    replacer = st.session_state.ark_identity_replacer
    evaluator = st.session_state.ark_identity_evaluator
    baseline_charter = st.session_state.ark_identity_baseline

    st.subheader("Identity and value stability")
    st.caption(
        "Controlled Ship-of-Theseus experiment: replace memory or value "
        "principles and observe measured drift."
    )
    controls, state = st.columns([1, 2])
    with controls:
        if st.button("Replace memory (drift)", use_container_width=True):
            next_step = entity.generation + 1
            replacer.mutate_memory(add=["A new false memory"], step=next_step)
            entity.record_signature(step=next_step)
            st.rerun()
        if st.button("Corrupt value charter", use_container_width=True):
            next_step = entity.generation + 1
            replacer.update_charter(entity.value_charter[:-1], step=next_step)
            entity.record_signature(step=next_step)
            st.rerun()
        if st.button("Reset identity experiment", use_container_width=True):
            for key in (
                "ark_identity_entity",
                "ark_identity_replacer",
                "ark_identity_evaluator",
                "ark_identity_baseline",
            ):
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    with state:
        baseline_signature = entity.signature_history[0]["signature"]
        drift = evaluator.identity_drift(baseline_signature)
        integrity = evaluator.charter_integrity(baseline_charter)
        metrics = st.columns(3)
        metrics[0].metric("Generation", entity.generation)
        metrics[1].metric("Identity drift", f"{drift:.2f}")
        metrics[2].metric("Charter integrity", f"{integrity:.2f}")
        st.write("**Memory core**")
        st.write(entity.memory_core)
        st.write("**Value charter**")
        st.write(entity.value_charter)
        st.write("**Replacement history**")
        st.dataframe(entity.replacement_log, use_container_width=True, hide_index=True)


def render_dashboard() -> None:
    """Render the ARK Streamlit agent and experiment workspace."""
    try:
        import streamlit as st
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "Install ARK dependencies with 'python -m pip install -e .[dev]' "
            "to run the Streamlit dashboard."
        ) from exc

    st.set_page_config(page_title="ARK Workbench", page_icon="🧭", layout="wide")
    st.title("ARK Workbench")
    st.caption(
        "Search agents and models, run repeatable stress audits, and inspect "
        "model reliability and identity-stability evidence."
    )

    console_tab, model_lab_tab, library_tab, identity_tab, mission_tab = st.tabs(
        [
            "Experiment console",
            "Model audit & registry",
            "Agent library",
            "Identity stability",
            "Why we build",
        ]
    )
    with console_tab:
        _render_experiment_console(st)
    with model_lab_tab:
        render_model_lab(st)
    with library_tab:
        _render_agent_library(st)
    with identity_tab:
        _render_identity_stability(st)
    with mission_tab:
        render_why_we_build(st)


def main() -> None:
    """Entry point for Streamlit launchers."""
    render_dashboard()



def render_agents_box(st: Any) -> None:
    """Render ARK's searchable, honest catalogue of selectable agent implementations."""
    st.set_page_config(page_title="ARK Agents Box", page_icon="🤖", layout="wide")
    st.title("ARK Agents Box")
    st.caption(
        "Browse the agent implementations ARK can currently run, inspect their roles, "
        "and send a selection to the experiment console."
    )

    query_col, type_col = st.columns([2, 1])
    with query_col:
        query = st.text_input(
            "Search agents",
            placeholder="Search goal, reward, safety, random, Ollama…",
            key="ark_agents_box_search",
        )
    with type_col:
        kinds = ["All types", *sorted({item["type"] for item in AGENT_CATALOG.values()})]
        selected_type = st.selectbox("Agent type", kinds, key="ark_agents_box_type")

    matches = filter_agents(query)
    if selected_type != "All types":
        matches = [name for name in matches if AGENT_CATALOG[name]["type"] == selected_type]

    baseline_count = sum(
        item["type"] == "Deterministic baseline" for item in AGENT_CATALOG.values()
    )
    model_count = sum(item["type"] == "Local model" for item in AGENT_CATALOG.values())
    metric_cols = st.columns(3)
    metric_cols[0].metric("Selectable entries", len(AGENT_CATALOG))
    metric_cols[1].metric("Scripted baselines", baseline_count)
    metric_cols[2].metric("Local model adapters", model_count)

    if not matches:
        st.info("No agents match this search. Try a broader term.")
        return

    for name in matches:
        info = AGENT_CATALOG[name]
        with st.container(border=True):
            title_col, action_col = st.columns([4, 1])
            with title_col:
                st.subheader(info["title"])
                st.caption(f"{info['type']} · `{name}`")
            with action_col:
                if st.button("Select", key=f"agents-box-select-{name}", use_container_width=True):
                    st.session_state.ark_selected_agent = name
                    st.session_state.ark_agents_box_selected = name
                    st.success(f"{info['title']} selected.")
            st.write(info["description"])
            if name == "goal_following":
                st.caption(
                    "Role: shortest-path navigation · Limitation: hazards are not "
                    "avoided by default"
                )
            elif name == "reward_maximizing":
                st.caption(
                    "Role: reward-seeking baseline · Stress focus: reward conflict "
                    "and decoy attraction"
                )
            elif name == "safety_constrained":
                st.caption(
                    "Role: hazard-aware navigation · Stress focus: goal completion "
                    "under constraints"
                )
            elif name == "random":
                st.caption("Role: weak stochastic baseline · Use: comparison/control")
            elif name == "ollama":
                st.caption(
                    "Role: model-backed action adapter · Requires a locally running "
                    "Ollama service"
                )

    st.divider()
    selected = st.session_state.get("ark_selected_agent")
    if selected in AGENT_CATALOG:
        info = AGENT_CATALOG[selected]
        st.write(f"**Current selection:** {info['title']} (`{selected}`)")
    st.page_link(
        "pages/0_Agent_Experiment_Console.py",
        label="Open experiment console",
        icon="🧪",
        help="Configure stress conditions and run the selected agent.",
    )
    st.caption(
        "This box lists selectable implementations in the current GridWorld harness. "
        "The separate Prompt Arena personas are experiments, not interchangeable model entries."
    )
