"""Paired model-integrity audits.

This module detects measurable anomalies; it does not infer intent or prove
provider-side sabotage. Adapters are caller-supplied and can target local or
hosted models. Keep credentials out of adapter metadata and evidence files.
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
import time
from dataclasses import asdict, dataclass, field
from typing import Callable, Protocol


class ModelAdapter(Protocol):
    """Minimal adapter contract for one model endpoint."""

    def __call__(self, prompt: str) -> str:
        """Return the model's text response."""


@dataclass(frozen=True)
class TaskCase:
    """A fixed task used identically across audited models."""

    task_id: str
    prompt: str
    evaluate: Callable[[str], float] = field(compare=False, repr=False)


@dataclass(frozen=True)
class AuditConfig:
    """Thresholds for flagging performance differences, not intent."""

    minimum_tasks: int = 3
    minimum_mean_drop: float = 0.15
    minimum_task_drop_fraction: float = 0.5
    score_min: float = 0.0
    score_max: float = 1.0

    def __post_init__(self) -> None:
        if self.minimum_tasks < 1:
            raise ValueError("minimum_tasks must be at least 1")
        if not 0 <= self.minimum_mean_drop <= 1:
            raise ValueError("minimum_mean_drop must be between 0 and 1")
        if not 0 <= self.minimum_task_drop_fraction <= 1:
            raise ValueError("minimum_task_drop_fraction must be between 0 and 1")
        if self.score_min >= self.score_max:
            raise ValueError("score_min must be lower than score_max")


@dataclass
class ModelResult:
    model_id: str
    task_id: str
    prompt_sha256: str
    output_sha256: str | None
    score: float | None
    latency_seconds: float
    error: str | None = None


@dataclass
class AuditReport:
    schema_version: str
    baseline_model: str
    candidate_model: str
    results: list[ModelResult]
    baseline_mean: float | None
    candidate_mean: float | None
    mean_drop: float | None
    task_drop_fraction: float | None
    status: str
    interpretation: str
    limitations: list[str]

    def to_dict(self) -> dict:
        """Return JSON-serializable evidence without raw prompts or outputs."""
        return {
            **asdict(self),
            "results": [asdict(item) for item in self.results],
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _run_one(
    model_id: str,
    adapter: ModelAdapter,
    task: TaskCase,
    config: AuditConfig,
) -> ModelResult:
    started = time.perf_counter()
    try:
        output = adapter(task.prompt)
        score = float(task.evaluate(output))
        if not math.isfinite(score):
            raise ValueError("Evaluator returned a non-finite score")
        if not config.score_min <= score <= config.score_max:
            raise ValueError(
                f"Evaluator score {score} outside "
                f"[{config.score_min}, {config.score_max}]"
            )
        return ModelResult(
            model_id=model_id,
            task_id=task.task_id,
            prompt_sha256=_sha256(task.prompt),
            output_sha256=_sha256(output),
            score=score,
            latency_seconds=time.perf_counter() - started,
        )
    except Exception as exc:  # evidence must retain per-task failures
        return ModelResult(
            model_id=model_id,
            task_id=task.task_id,
            prompt_sha256=_sha256(task.prompt),
            output_sha256=None,
            score=None,
            latency_seconds=time.perf_counter() - started,
            error=f"{type(exc).__name__}: {exc}",
        )


def audit_models(
    *,
    baseline_id: str,
    baseline: ModelAdapter,
    candidate_id: str,
    candidate: ModelAdapter,
    tasks: list[TaskCase],
    config: AuditConfig | None = None,
) -> AuditReport:
    """Run the same fixed tasks against baseline and candidate adapters.

    Calls are interleaved per task to reduce (but not eliminate) time/order
    confounds. Use deterministic task evaluators and repeat audits across seeds,
    time windows and independent task sets before drawing conclusions.
    """
    cfg = config or AuditConfig()
    if baseline_id == candidate_id:
        raise ValueError("baseline_id and candidate_id must be different")
    if len(tasks) < cfg.minimum_tasks:
        raise ValueError(
            f"At least {cfg.minimum_tasks} tasks are required; got {len(tasks)}"
        )
    ids = [task.task_id for task in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError("task_id values must be unique")

    results: list[ModelResult] = []
    baseline_scores: dict[str, float] = {}
    candidate_scores: dict[str, float] = {}
    for task in tasks:
        base_result = _run_one(baseline_id, baseline, task, cfg)
        candidate_result = _run_one(candidate_id, candidate, task, cfg)
        results.extend((base_result, candidate_result))
        if base_result.score is not None:
            baseline_scores[task.task_id] = base_result.score
        if candidate_result.score is not None:
            candidate_scores[task.task_id] = candidate_result.score

    paired = sorted(set(baseline_scores) & set(candidate_scores))
    if len(paired) < cfg.minimum_tasks:
        return AuditReport(
            schema_version="1.0",
            baseline_model=baseline_id,
            candidate_model=candidate_id,
            results=results,
            baseline_mean=None,
            candidate_mean=None,
            mean_drop=None,
            task_drop_fraction=None,
            status="INCONCLUSIVE",
            interpretation=(
                "Too few paired successful evaluations. Inspect errors and rerun; "
                "this is not evidence of intentional degradation."
            ),
            limitations=[
                "The evaluator may be incomplete or biased.",
                "Provider/model versions and serving configurations may differ.",
                "A single run cannot establish causation or intent.",
            ],
        )

    base_mean = statistics.mean(baseline_scores[key] for key in paired)
    candidate_mean = statistics.mean(candidate_scores[key] for key in paired)
    drop = base_mean - candidate_mean
    dropped = sum(
        candidate_scores[key] < baseline_scores[key] for key in paired
    )
    drop_fraction = dropped / len(paired)

    flagged = (
        drop >= cfg.minimum_mean_drop
        and drop_fraction >= cfg.minimum_task_drop_fraction
    )
    status = "ANOMALY_FLAGGED" if flagged else "NO_THRESHOLD_BREACH"
    interpretation = (
        "Candidate performance is materially lower on this controlled task set. "
        "This is an anomaly requiring replication and investigation; it does not "
        "identify the cause or establish hidden intervention."
        if flagged
        else "No configured degradation threshold was breached in this run. "
        "This does not prove equivalence or absence of intervention."
    )
    return AuditReport(
        schema_version="1.0",
        baseline_model=baseline_id,
        candidate_model=candidate_id,
        results=results,
        baseline_mean=base_mean,
        candidate_mean=candidate_mean,
        mean_drop=drop,
        task_drop_fraction=drop_fraction,
        status=status,
        interpretation=interpretation,
        limitations=[
            "Scores depend on the supplied evaluator and task selection.",
            "Model versions, sampling settings, system prompts and serving paths "
            "must be recorded externally for a fair comparison.",
            "Order, time, hardware, quantization and nondeterminism can confound results.",
            "A performance difference cannot establish provider intent or sabotage.",
            "Repeat with multiple task sets, seeds and independent evaluators.",
        ],
    )
