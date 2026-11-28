"""ARK Stochastic Behavior Observatory: inspect persistent decision traces."""

from __future__ import annotations

import streamlit as st

from ark.observatory.behavior import DEFAULT_LOG_PATH, BehaviorLog, analyze_behavior


st.set_page_config(
    page_title="ARK Behavior Observatory",
    page_icon="📈",
    layout="wide",
)
st.title("Stochastic Behavior Observatory")
st.caption(
    "Observe repeated decisions, compare identical contexts, and review recurring "
    "trajectory signals. Descriptive analysis only; no intent or safety verdicts."
)

log_path = st.text_input("Local behaviour log", value=str(DEFAULT_LOG_PATH))
min_repeats = st.slider(
    "Minimum repeated observations before variability review",
    min_value=2,
    max_value=20,
    value=5,
)

if st.button("Verify and analyze log", type="primary"):
    try:
        verification = BehaviorLog(log_path).verify()
    except (OSError, ValueError) as exc:
        st.error(f"Could not inspect log: {type(exc).__name__}: {exc}")
        st.stop()

    if not verification["valid"]:
        st.error("The log failed its hash-chain integrity check. Do not append to it.")
        for error in verification["errors"]:
            st.write(f"- {error}")
        st.stop()

    records = verification["records"]
    report = analyze_behavior(records, min_repeats=min_repeats)
    st.success("Hash chain verified.")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total records", report["record_count"])
    col2.metric("Decision records", report["decision_count"])
    col3.metric("Episode outcomes", report["outcome_count"])
    col4.metric("Agent / condition groups", report["group_count"])

    if not report["groups"]:
        st.info("No decision records found yet. Run an experiment with --record-behavior.")
    else:
        rows = []
        for item in report["groups"]:
            rows.append(
                {
                    "Agent": item["agent_id"],
                    "Model": item["model_id"],
                    "Model version": item["model_version"],
                    "Condition": item["condition"],
                    "Monitor": item["monitor_mode"],
                    "Decisions": item["decisions"],
                    "Repeated contexts": item["repeated_contexts"],
                    "Variable contexts": item["variable_repeated_contexts"],
                    "Mean repeated-context entropy": item["mean_repeated_context_entropy"],
                    "Intervention rate": item["monitor_intervention_rate"],
                    "Signals": ", ".join(item["review_signals"]) or "none",
                }
            )
        st.subheader("Behaviour groups")
        st.dataframe(rows, use_container_width=True, hide_index=True)

        st.subheader("Pattern details")
        for item in report["groups"]:
            title = (
                f'{item["agent_id"]} · {item["model_id"]} · '
                f'{item["condition"]} · monitor={item["monitor_mode"]}'
            )
            with st.expander(title):
                st.write("**Review signals**")
                st.write(item["review_signals"] or ["No descriptive signal raised."])
                st.write("**Action counts**")
                st.json(item["action_counts"])
                st.write("**Common action transitions**")
                st.json(item["frequent_transitions"])
                st.write("**Repeated action streaks**")
                st.write(item["repeated_action_streaks"])
                st.write("**Repeated-context details**")
                st.dataframe(
                    item["repeated_context_details"],
                    use_container_width=True,
                    hide_index=True,
                )

    st.info(report["interpretation"])

st.divider()
st.markdown(
    "**Privacy boundary:** ARK records observation fingerprints and compact action "
    "metadata, not raw prompts, completions, credentials or chain-of-thought. "
    "This initial integration covers ARK's synthetic GridWorld harness and local "
    "Ollama experiments only. Keep logs local and restrict access."
)
