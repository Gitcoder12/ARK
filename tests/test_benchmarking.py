from __future__ import annotations

import json

import pytest

from ark.benchmarking import benchmark, write_json


def test_benchmark_records_latency_throughput_and_memory():
    calls = []
    result = benchmark(
        "append",
        lambda: calls.append(1),
        iterations=3,
        warmups=1,
        workload_units=10,
        metadata={"fixture": "unit"},
    )
    assert len(calls) == 4
    assert result.iterations == 3
    assert result.median_seconds >= 0
    assert result.p95_seconds >= result.min_seconds
    assert result.p99_seconds <= result.max_seconds
    assert result.throughput_units_per_second is not None
    assert result.peak_python_bytes >= 0
    assert result.metadata["fixture"] == "unit"


def test_benchmark_rejects_invalid_parameters():
    with pytest.raises(ValueError):
        benchmark("x", lambda: None, iterations=0)
    with pytest.raises(ValueError):
        benchmark("x", lambda: None, warmups=-1)
    with pytest.raises(ValueError):
        benchmark(" ", lambda: None)


def test_write_json_preserves_raw_samples_and_metadata(tmp_path):
    result = benchmark("noop", lambda: None, iterations=2, warmups=0)
    output = tmp_path / "nested" / "run.json"
    write_json([result], output, run_metadata={"seed": 7})
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["run_metadata"]["seed"] == 7
    assert len(payload["results"][0]["durations_seconds"]) == 2
