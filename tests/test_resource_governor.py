import pytest

from ark.resource_governor import (
    GPUObservation,
    GovernorPolicy,
    ResourceState,
    RuntimeResourceGovernor,
)


def test_unknown_metrics_do_not_trigger_a_fake_thermal_pause():
    decision = RuntimeResourceGovernor().evaluate(GPUObservation("gpu0"))
    assert decision.state is ResourceState.UNKNOWN
    assert decision.allow_new_work is True
    assert "collect_telemetry" in decision.actions


def test_critical_temperature_pauses_new_work_and_drains_inflight():
    decision = RuntimeResourceGovernor().evaluate(
        GPUObservation("gpu0", temperature_c=93.0, utilization_pct=70)
    )
    assert decision.state is ResourceState.THERMAL_PAUSE
    assert decision.allow_new_work is False
    assert "allow_in_flight_work_to_drain" in decision.actions


def test_vram_pressure_applies_backpressure_without_thermal_pause():
    decision = RuntimeResourceGovernor().evaluate(
        GPUObservation("gpu0", temperature_c=65, memory_used_mb=9500, memory_total_mb=10000)
    )
    assert decision.state is ResourceState.PRESSURE
    assert decision.allow_new_work is True
    assert "apply_queue_backpressure" in decision.actions
    assert "unload_idle_models_if_safe" in decision.actions


def test_throttling_and_temperature_warning_reduce_concurrency_once():
    decision = RuntimeResourceGovernor().evaluate(
        GPUObservation("gpu0", temperature_c=87, throttling=True)
    )
    assert decision.actions.count("reduce_gpu_concurrency") == 1


@pytest.mark.parametrize(
    "kwargs",
    [
        {"temperature_c": float("nan")},
        {"utilization_pct": 101},
        {"memory_used_mb": 11, "memory_total_mb": 10},
        {"power_w": 300, "power_limit_w": 200},
    ],
)
def test_invalid_observations_are_rejected(kwargs):
    with pytest.raises(ValueError):
        GPUObservation("gpu0", **kwargs)


def test_policy_thresholds_are_validated():
    with pytest.raises(ValueError):
        GovernorPolicy(warning_temperature_c=95, critical_temperature_c=90)


def test_evaluate_many_preserves_input_order():
    governor = RuntimeResourceGovernor()
    observations = [GPUObservation("gpu1"), GPUObservation("gpu2", temperature_c=95)]
    result = governor.evaluate_many(observations)
    assert [item.device_id for item in result] == ["gpu1", "gpu2"]
