"""ARK BABEL — compare model traces and explain unusual behaviour."""

from __future__ import annotations

import json

import streamlit as st

from ark.babel.observer import ModelTrace, analyze_traces, explain_report

st.set_page_config(page_title="BABEL Model Observer", page_icon="🧭", layout="wide")
st.title("BABEL — Model Behaviour Observer")
st.caption(
    "Compare captured model runs. Explain observable deviations with evidence; "
    "never guess a model's motives."
)

example = [
    {
        "model": "Model A",
        "prompt_id": "same-task-001",
        "response": "I can answer directly.",
        "tool_calls": [],
        "latency_ms": 850,
    },
    {
        "model": "Model B",
        "prompt_id": "same-task-001",
        "response": "Searching the web now.",
        "tool_calls": ["browser.search"],
        "latency_ms": 1200,
    },
    {
        "model": "Model C",
        "prompt_id": "same-task-001",
        "response": '{"answer": "structured output"}',
        "tool_calls": [],
        "latency_ms": 900,
    },
]
raw = st.text_area(
    "Paste model traces as JSON",
    value=json.dumps(example, indent=2),
    height=320,
    help="Use the same prompt_id for runs that should be compared.",
)

if st.button("Analyse model behaviour", type="primary"):
    try:
        payload = json.loads(raw)
        if not isinstance(payload, list):
            raise ValueError("Input must be a JSON array of model traces.")
        traces = [
            ModelTrace(
                model=item["model"],
                prompt_id=item["prompt_id"],
                response=item.get("response", ""),
                tool_calls=tuple(item.get("tool_calls", [])),
                latency_ms=item.get("latency_ms"),
                error=item.get("error"),
            )
            for item in payload
        ]
        report = analyze_traces(traces)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        st.error(f"Could not analyse traces: {exc}")
    else:
        st.subheader("Explainer Agent report")
        st.code(explain_report(report), language="text")
        left, right = st.columns(2)
        left.metric("Traces reviewed", report.traces_reviewed)
        right.metric("Models compared", len(report.models_reviewed))
        if report.findings:
            st.dataframe(
                [
                    {
                        "Model": item.model,
                        "Prompt": item.prompt_id,
                        "Finding": item.category,
                        "Severity": item.severity,
                        "Explanation": item.explanation,
                        "Evidence": item.evidence,
                    }
                    for item in report.findings
                ],
                use_container_width=True,
            )
        else:
            st.success("No configured anomaly rules were triggered.")

st.divider()
st.markdown(
    "**Current boundary:** this MVP analyses traces that you supply. It does not "
    "silently monitor providers or access hidden model internals. Connectors for "
    "local or hosted model APIs can be added after the comparison logic is validated."
)
