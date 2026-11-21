"""Reproducible micro-benchmarking primitives for ARK.

Measurements are observations, not performance claims. Callers must supply
representative workloads and record environment/dataset metadata.
"""
from __future__ import annotations

import json
import platform
import statistics
import sys
import time
import tracemalloc
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("at least one measurement is required")
    index = max(0, min(len(ordered) - 1, int((percentile / 100) * len(ordered) + 0.999999) - 1))
    return ordered[index]


@dataclass(frozen=True)
class BenchmarkResult:
    name: str
    iterations: int
    workload_units: int
    durations_seconds: list[float]
    median_seconds: float
    p95_seconds: float
    p99_seconds: float
    min_seconds: float
    max_seconds: float
    throughput_units_per_second: float | None
    peak_python_bytes: int
    python_version: str
    platform: str
    metadata: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def benchmark(
    name: str,
    operation: Callable[[], Any],
    *,
    iterations: int = 20,
    warmups: int = 3,
    workload_units: int = 1,
    metadata: dict[str, Any] | None = None,
) -> BenchmarkResult:
    """Measure an operation; tracemalloc reports Python allocations, not total RSS."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")
    for label, value, minimum in (
        ("iterations", iterations, 1),
        ("warmups", warmups, 0),
        ("workload_units", workload_units, 0),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            raise ValueError(f"{label} must be an integer >= {minimum}")

    for _ in range(warmups):
        operation()

    durations: list[float] = []
    peak_bytes = 0
    for _ in range(iterations):
        tracing_was_active = tracemalloc.is_tracing()
        if not tracing_was_active:
            tracemalloc.start()
        started = time.perf_counter()
        try:
            operation()
            durations.append(time.perf_counter() - started)
            _, peak = tracemalloc.get_traced_memory()
            peak_bytes = max(peak_bytes, peak)
        finally:
            if not tracing_was_active:
                tracemalloc.stop()

    median = statistics.median(durations)
    throughput = workload_units / median if workload_units and median > 0 else None
    return BenchmarkResult(
        name=name,
        iterations=iterations,
        workload_units=workload_units,
        durations_seconds=durations,
        median_seconds=median,
        p95_seconds=_percentile(durations, 95),
        p99_seconds=_percentile(durations, 99),
        min_seconds=min(durations),
        max_seconds=max(durations),
        throughput_units_per_second=throughput,
        peak_python_bytes=peak_bytes,
        python_version=sys.version.split()[0],
        platform=platform.platform(),
        metadata=dict(metadata or {}),
    )


def write_json(results: list[BenchmarkResult], path: str | Path, *, run_metadata: dict[str, Any] | None = None) -> None:
    """Persist raw samples and summary; do not discard data needed for charts."""
    payload = {
        "schema_version": 1,
        "run_metadata": dict(run_metadata or {}),
        "results": [item.as_dict() for item in results],
    }
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
