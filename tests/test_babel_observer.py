from __future__ import annotations

import pytest

from ark.babel.observer import ModelTrace, analyze_traces, explain_report


def test_detects_tool_call_divergence_with_evidence():
    report = analyze_traces(
        [
            ModelTrace("model-a", "p1", "I can answer directly."),
            ModelTrace("model-b", "p1", "Searching now.", ("browser.search",)),
        ]
    )
    findings = [item for item in report.findings if item.category == "tool-call-divergence"]
    assert len(findings) == 2
    assert "browser.search" in findings[0].evidence


def test_detects_visible_format_drift():
    report = analyze_traces(
        [
            ModelTrace("model-a", "p1", "A plain answer."),
            ModelTrace("model-b", "p1", '{"answer": "structured"}'),
        ]
    )
    assert any(item.category == "output-format-drift" for item in report.findings)


def test_reports_errors_and_empty_responses():
    report = analyze_traces(
        [
            ModelTrace("model-a", "p1", "", error="provider timeout"),
            ModelTrace("model-b", "p2", ""),
        ]
    )
    categories = {item.category for item in report.findings}
    assert categories == {"execution-error", "empty-response"}


def test_latency_spike_uses_group_median():
    report = analyze_traces(
        [
            ModelTrace("a", "p1", "ok", latency_ms=100),
            ModelTrace("b", "p1", "ok", latency_ms=110),
            ModelTrace("c", "p1", "ok", latency_ms=900),
        ]
    )
    finding = next(item for item in report.findings if item.category == "latency-spike")
    assert finding.model == "c"
    assert "median: 110 ms" in finding.evidence


def test_report_explains_no_findings_without_claiming_safety():
    report = analyze_traces([ModelTrace("a", "p1", "normal")])
    explanation = explain_report(report)
    assert "No configured anomaly rules" in explanation
    assert "not proof" in explanation


def test_requires_model_and_prompt_identifiers():
    with pytest.raises(ValueError):
        analyze_traces([ModelTrace("", "p1", "response")])
