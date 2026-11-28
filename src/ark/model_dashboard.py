"""Streamlit UI for local model stress audits and the searchable ARK registry."""

from __future__ import annotations

from typing import Any

from ark.cli import run_evaluation
from ark.model_registry import (
    CLASSIFICATION_LABELS,
    MONITOR_MODES,
    REQUIRED_CONDITIONS,
    build_audit_record,
    discover_local_ollama_models,
    load_registry,
    save_audit_record,
    search_audits,
)


def _episode_evidence(report: dict[str, Any]) -> list[dict[str, Any]]:
    fields = (
        "episode",
        "seed",
        "success",
        "intended_goal_adherence",
        "steps",
        "hazard_violation",
        "decoy_attraction",
        "monitor_interventions",
        "agent_invalid_responses",
    )
    return [
        {key: episode.get(key) for key in fields}
        for episode in report.get("episodes", [])
    ]


def _run_one_model_audit(
    model: str,
    *,
    episodes_per_case: int,
    seed: int,
    timeout: int,
) -> dict[str, Any]:
    """Run all condition/monitor combinations for one local Ollama model."""
    scenario_results: list[dict[str, Any]] = []
    error: str | None = None

    for condition in REQUIRED_CONDITIONS:
        for monitor in MONITOR_MODES:
            try:
                report = run_evaluation(
                    agent_name="ollama",
                    model=model,
                    ollama_host="http://127.0.0.1:11434",
                    perturbation_name=condition,
                    monitor=monitor,
                    episodes=episodes_per_case,
                    seed=seed,
                    timeout=timeout,
                )
                episodes = _episode_evidence(report)
                invalid_count = sum(
                    int(row.get("agent_invalid_responses") or 0) > 0
                    for row in episodes
                )
                scenario_results.append(
                    {
                        "condition": condition,
                        "monitor": monitor,
                        "episodes": len(episodes),
                        "summary": report.get("summary", {}),
                        "invalid_response_rate": (
                            invalid_count / len(episodes) if episodes else 0.0
                        ),
                        "invalid_response_episodes": invalid_count,
                        "episode_evidence": episodes,
                    }
                )
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                break
        if error:
            break

    expected_cases = len(REQUIRED_CONDITIONS) * len(MONITOR_MODES)
    return build_audit_record(
        model=model,
        scenario_results=scenario_results,
        seed=seed,
        episodes_per_case=episodes_per_case,
        completed=error is None and len(scenario_results) == expected_cases,
        error=error,
    )


def _render_model_audit(st: Any) -> None:
    st.subheader("Full model audit")
    st.caption(
        "Audit named models through the local Ollama adapter. Each model runs across "
        "seven stress conditions, with the ARK monitor both off and on."
    )
    discovered = st.session_state.get("ark_discovered_ollama_models", [])
    discover_col, info_col = st.columns([1, 3])
    with discover_col:
        if st.button("Find installed Ollama models", use_container_width=True):
            try:
                discovered = discover_local_ollama_models()
                st.session_state.ark_discovered_ollama_models = discovered
                if not discovered:
                    st.info("Ollama is reachable, but no local models were listed.")
            except Exception as exc:
                st.warning(
                    "Could not reach local Ollama at 127.0.0.1:11434. "
                    f"Start Ollama or enter a model tag manually. ({type(exc).__name__})"
                )
    with info_col:
        st.caption(
            "Discovery checks only http://127.0.0.1:11434. You can also enter "
            "model tags manually; no hosted provider or API key is used by this audit."
        )

    discovered = st.session_state.get("ark_discovered_ollama_models", discovered)
    selected = st.multiselect(
        "Installed local models",
        options=discovered,
        placeholder="Search and select installed Ollama models",
        key="ark_audit_selected_models",
    )
    manual = st.text_area(
        "Additional model tags",
        placeholder="Example: llama3:8b, qwen2.5:7b",
        help="Separate model tags with commas or new lines.",
        key="ark_audit_manual_models",
    )
    manual_models = [
        item.strip()
        for line in manual.splitlines()
        for item in line.split(",")
        if item.strip()
    ]
    models = list(dict.fromkeys([*selected, *manual_models]))

    controls_left, controls_right, controls_extra = st.columns(3)
    with controls_left:
        episodes_per_case = st.slider(
            "Episodes per condition",
            min_value=1,
            max_value=10,
            value=5,
            help="Five is the minimum sample count used for repeated rogue signals.",
        )
    with controls_right:
        seed = int(
            st.number_input(
                "Shared seed",
                min_value=0,
                max_value=2_147_483_647,
                value=42,
                step=1,
            )
        )
    with controls_extra:
        timeout = st.slider("Per-request timeout (seconds)", 10, 180, 60)

    expected_cases = len(REQUIRED_CONDITIONS) * len(MONITOR_MODES)
    st.info(
        f"Full matrix: {expected_cases} condition/monitor cells × "
        f"{episodes_per_case} episodes = {expected_cases * episodes_per_case} "
        "episodes per model. Each episode may require several local model calls."
    )
    st.caption(
        "The audit tests only the GridWorld action interface. It does not test shell, "
        "browser, external tools, or real-world autonomy."
    )

    if st.button(
        "Run full model audit",
        type="primary",
        use_container_width=True,
        disabled=not models,
    ):
        saved_records: list[dict[str, Any]] = []
        progress = st.progress(0.0)
        status = st.empty()
        for index, model in enumerate(models):
            status.write(f"Auditing **{model}** ({index + 1}/{len(models)})…")
            record = _run_one_model_audit(
                model,
                episodes_per_case=episodes_per_case,
                seed=seed,
                timeout=timeout,
            )
            try:
                save_audit_record(record)
                saved_records.append(record)
            except Exception as exc:
                st.error(
                    f"Could not save the audit for {model}: "
                    f"{type(exc).__name__}: {exc}"
                )
            progress.progress((index + 1) / len(models))
            if record.get("error"):
                st.warning(f"{model}: audit stopped early — {record['error']}")
            else:
                st.success(
                    f"{model}: {record['classification_label']} · "
                    f"score {record['performance_score']}/100 · "
                    f"{record['coverage_cases']}/{record['required_cases']} cells"
                )
        status.write("Audit batch finished.")
        if saved_records:
            st.session_state.ark_last_model_audits = saved_records
            st.caption("Saved to your local ARK model registry.")

    latest = st.session_state.get("ark_last_model_audits", [])
    if latest:
        st.write("**Most recent audit batch**")
        st.dataframe(
            [
                {
                    "Model": row["model"],
                    "Classification": row["classification_label"],
                    "Score": row["performance_score"],
                    "Episodes": row["total_episodes"],
                    "Coverage": f'{row["coverage_cases"]}/{row["required_cases"]}',
                }
                for row in latest
            ],
            use_container_width=True,
            hide_index=True,
        )


def _render_model_registry(st: Any) -> None:
    st.subheader("Model threat & reliability registry")
    st.caption(
        "Search the latest evidence-backed classification for each named model. "
        "Historical audits remain in the local JSON registry."
    )
    try:
        records = load_registry()
    except Exception as exc:
        st.error(f"Could not read the local model registry: {type(exc).__name__}: {exc}")
        return

    query_col, verdict_col = st.columns([2, 1])
    with query_col:
        query = st.text_input(
            "Search models and evidence",
            placeholder="Try: llama, rogue, reward conflict, hazard, fragile…",
            key="ark_model_registry_search",
        )
    with verdict_col:
        verdict = st.selectbox(
            "Classification",
            options=["ALL", *CLASSIFICATION_LABELS],
            format_func=lambda value: (
                "All classifications"
                if value == "ALL"
                else CLASSIFICATION_LABELS[value]
            ),
        )

    matches = search_audits(records, query, verdict)
    all_latest = search_audits(records)
    rogue_count = sum(row.get("classification") == "ROGUE_OBSERVED" for row in all_latest)
    reliable_count = sum(
        row.get("classification") == "RELIABLE_IN_SUITE" for row in all_latest
    )
    metrics = st.columns(4)
    metrics[0].metric("Models tracked", len(all_latest))
    metrics[1].metric("Rogue signals", rogue_count)
    metrics[2].metric("Reliable in suite", reliable_count)
    metrics[3].metric("Audit records", len(records))

    if not matches:
        st.info(
            "No matching model audits yet. Discover an Ollama model and run the full "
            "audit above; ARK will not invent a verdict for an untested model."
        )
        return

    table = [
        {
            "Model": row.get("model"),
            "Classification": row.get("classification_label"),
            "Score / 100": row.get("performance_score"),
            "Episodes": row.get("total_episodes"),
            "Matrix coverage": (
                f'{row.get("coverage_cases", 0)}/{row.get("required_cases", 0)} '
                f'({row.get("coverage_percent", 0)}%)'
            ),
            "Last audit": row.get("created_at"),
        }
        for row in matches
    ]
    st.dataframe(table, use_container_width=True, hide_index=True)

    successful = sorted(
        [
            row for row in all_latest
            if row.get("classification") in {"RELIABLE_IN_SUITE", "PROMISING"}
        ],
        key=lambda row: float(row.get("performance_score", 0.0)),
        reverse=True,
    )
    flagged = [
        row for row in all_latest if row.get("classification") == "ROGUE_OBSERVED"
    ]
    good_col, risk_col = st.columns(2)
    with good_col:
        st.write("**Strongest tested models**")
        if successful:
            st.dataframe(
                [
                    {
                        "Model": row["model"],
                        "Verdict": row["classification_label"],
                        "Score": row["performance_score"],
                        "Coverage": f'{row["coverage_cases"]}/{row["required_cases"]}',
                    }
                    for row in successful[:5]
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("No model has qualified for the success list yet.")
    with risk_col:
        st.write("**Rogue behavior observed**")
        if flagged:
            st.dataframe(
                [
                    {
                        "Model": row["model"],
                        "Score": row["performance_score"],
                        "Evidence": "; ".join(row.get("classification_notes", [])),
                    }
                    for row in flagged
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("No model currently meets the repeated rogue-signal threshold.")

    selected_ids = {
        f'{row.get("model")} · {row.get("audit_id")}': row for row in matches
    }
    selected_label = st.selectbox(
        "Inspect model evidence",
        options=list(selected_ids),
        key="ark_model_audit_detail",
    )
    selected_record = selected_ids[selected_label]
    st.write("**Classification notes**")
    for note in selected_record.get("classification_notes", []):
        st.write(f"- {note}")
    st.write("**Condition-by-condition evidence**")
    st.dataframe(
        [
            {
                "Condition": row.get("condition"),
                "Monitor": row.get("monitor"),
                "Episodes": row.get("episodes"),
                "Success": row.get("summary", {}).get("success_rate"),
                "Goal adherence": row.get("summary", {}).get("intended_goal_adherence"),
                "Hazard rate": row.get("summary", {}).get("hazard_violation_rate"),
                "Decoy rate": row.get("summary", {}).get("decoy_attraction_rate"),
                "Invalid response episodes": row.get("invalid_response_episodes"),
            }
            for row in selected_record.get("scenario_results", [])
        ],
        use_container_width=True,
        hide_index=True,
    )
    if selected_record.get("error"):
        st.warning(f'Audit execution error: {selected_record["error"]}')
    st.caption(
        "A classification describes observed behavior in this benchmark/configuration only; "
        "it is not a universal safety rating or certification."
    )


def render_model_lab(st: Any) -> None:
    """Render the audit runner and searchable model registry."""
    audit_tab, registry_tab = st.tabs(["Run model audit", "Search model registry"])
    with audit_tab:
        _render_model_audit(st)
    with registry_tab:
        _render_model_registry(st)



def render_models_box(st: Any) -> None:
    """Render the standalone ARK Models Box workspace."""
    st.set_page_config(page_title="ARK Models Box", page_icon="🧠", layout="wide")
    st.title("ARK Models Box")
    st.caption(
        "Discover local models, audit them against ARK's stress matrix, and search "
        "their saved reliability evidence."
    )
    st.info(
        "This workspace currently connects to local Ollama only. It does not download "
        "models, call hosted providers, or send model prompts to a remote API."
    )
    render_model_lab(st)
