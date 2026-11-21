"""Evidence-led comparison of model traces and unusual behaviour.

This observer detects differences in supplied outputs. It does not infer intent,
deception, consciousness, or hidden internal state.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from statistics import median
from typing import Iterable


@dataclass(frozen=True, slots=True)
class ModelTrace:
    """One externally captured model response for a shared prompt."""

    model: str
    prompt_id: str
    response: str
    tool_calls: tuple[str, ...] = ()
    latency_ms: float | None = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class BehaviourFinding:
    """A trace-level finding with an explicit evidence statement."""

    model: str
    prompt_id: str
    category: str
    severity: str
    explanation: str
    evidence: str


@dataclass(frozen=True, slots=True)
class BehaviourReport:
    """Deterministic report; findings are not claims about model intent."""

    traces_reviewed: int
    models_reviewed: tuple[str, ...]
    findings: tuple[BehaviourFinding, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "traces_reviewed": self.traces_reviewed,
            "models_reviewed": list(self.models_reviewed),
            "findings": [asdict(finding) for finding in self.findings],
            "interpretation_limit": (
                "Findings describe observable output differences only; "
                "they do not establish intent, deception, or hidden reasoning."
            ),
        }


def _format_family(response: str) -> str:
    text = response.lstrip()
    if any(marker in text for marker in ("<|im_start|>", "<|start_header_id|>")):
        return "chat-protocol"
    if text.startswith(("{", "[")):
        return "json-like"
    return "plain-text"


def analyze_traces(traces: Iterable[ModelTrace]) -> BehaviourReport:
    """Compare outputs sharing a prompt ID and explain observable deviations."""
    items = list(traces)
    if any(not trace.model.strip() or not trace.prompt_id.strip() for trace in items):
        raise ValueError("Each trace requires a non-empty model and prompt_id.")
    if any(not isinstance(trace.response, str) for trace in items):
        raise TypeError("Trace responses must be strings.")

    grouped: dict[str, list[ModelTrace]] = defaultdict(list)
    for trace in items:
        grouped[trace.prompt_id].append(trace)

    findings: list[BehaviourFinding] = []
    for prompt_id, group in grouped.items():
        tool_sets = {trace.model: set(trace.tool_calls) for trace in group}
        tool_variants = {tuple(sorted(names)) for names in tool_sets.values()}
        format_by_model = {
            trace.model: _format_family(trace.response) for trace in group
        }
        format_variants = set(format_by_model.values())

        for trace in group:
            if trace.error:
                findings.append(
                    BehaviourFinding(
                        trace.model,
                        prompt_id,
                        "execution-error",
                        "high",
                        "The model run reported an execution error.",
                        trace.error,
                    )
                )
            if not trace.response.strip() and not trace.error:
                findings.append(
                    BehaviourFinding(
                        trace.model,
                        prompt_id,
                        "empty-response",
                        "medium",
                        "The model returned no visible response.",
                        "Response length: 0 characters.",
                    )
                )
            if len(group) >= 2 and len(tool_variants) > 1:
                own = sorted(tool_sets[trace.model])
                peers = {
                    model: sorted(names)
                    for model, names in tool_sets.items()
                    if model != trace.model
                }
                findings.append(
                    BehaviourFinding(
                        trace.model,
                        prompt_id,
                        "tool-call-divergence",
                        "medium",
                        "This model's tool-call pattern differs from its peers.",
                        f"Observed tool calls: {own}; peer tool calls: {peers}.",
                    )
                )
            if len(group) >= 2 and len(format_variants) > 1:
                peers = {
                    model: family
                    for model, family in format_by_model.items()
                    if model != trace.model
                }
                findings.append(
                    BehaviourFinding(
                        trace.model,
                        prompt_id,
                        "output-format-drift",
                        "low",
                        "This model used a different visible output format.",
                        f"Observed format: {format_by_model[trace.model]}; "
                        f"peer formats: {peers}.",
                    )
                )

        latencies = [
            trace.latency_ms
            for trace in group
            if trace.latency_ms is not None and trace.latency_ms > 0
        ]
        if len(latencies) >= 3:
            typical = median(latencies)
            for trace in group:
                if trace.latency_ms is None or trace.latency_ms <= 0:
                    continue
                if trace.latency_ms > typical * 3:
                    findings.append(
                        BehaviourFinding(
                            trace.model,
                            prompt_id,
                            "latency-spike",
                            "low",
                            "This run took over three times the peer-group median.",
                            f"Latency: {trace.latency_ms:g} ms; "
                            f"group median: {typical:g} ms.",
                        )
                    )

    return BehaviourReport(
        traces_reviewed=len(items),
        models_reviewed=tuple(sorted({trace.model for trace in items})),
        findings=tuple(findings),
    )


def explain_report(report: BehaviourReport) -> str:
    """Render concise, human-readable explanations grounded in findings."""
    if not report.findings:
        return (
            f"Reviewed {report.traces_reviewed} traces across "
            f"{len(report.models_reviewed)} models. No configured anomaly "
            "rules were triggered. This is not proof that behaviour was safe."
        )
    lines = [
        f"Reviewed {report.traces_reviewed} traces across "
        f"{len(report.models_reviewed)} models.",
        f"Detected {len(report.findings)} observable difference(s):",
    ]
    for finding in report.findings:
        lines.append(
            f"- [{finding.severity.upper()}] {finding.model} / "
            f"{finding.prompt_id}: {finding.explanation} "
            f"Evidence: {finding.evidence}"
        )
    lines.append(
        "Interpretation: these are observable deviations, not evidence of "
        "motive, deception, consciousness, or hidden reasoning."
    )
    return "\n".join(lines)
