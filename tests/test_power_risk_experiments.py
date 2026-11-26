"""Tests for deterministic full-factorial sensitivity experiments."""
import json

import pytest

from ark.power_risk import (
    SCENARIOS,
    run_sensitivity_grid,
    sensitivity_report_json,
)


def test_sensitivity_grid_is_complete_and_reproducible():
    scenario_id = SCENARIOS[0].scenario_id
    first = run_sensitivity_grid(scenario_id)
    second = run_sensitivity_grid(scenario_id)
    assert len(first.cases) == 9
    assert first.experiment_id == second.experiment_id
    assert first.cases == second.cases
    assert first.method == "deterministic full-factorial parameter grid"


def test_sensitivity_grid_improves_with_increased_safeguard_coverage():
    scenario_id = SCENARIOS[0].scenario_id
    report = run_sensitivity_grid(
        scenario_id,
        pressure_levels=(0.7,),
        safeguard_levels=(0.0, 0.5, 1.0),
    )
    peaks = [case.peak_residual for case in report.cases]
    assert peaks[0] > peaks[1] > peaks[2]


def test_sensitivity_grid_exports_valid_json():
    report = run_sensitivity_grid(SCENARIOS[0].scenario_id)
    parsed = json.loads(sensitivity_report_json(report))
    assert parsed["experiment_id"] == report.experiment_id
    assert len(parsed["cases"]) == 9
    assert "not a probability" in parsed["interpretation"]


def test_sensitivity_grid_rejects_invalid_inputs():
    scenario_id = SCENARIOS[0].scenario_id
    with pytest.raises(ValueError, match="must not be empty"):
        run_sensitivity_grid(scenario_id, pressure_levels=())
    with pytest.raises(ValueError, match="between 0 and 1"):
        run_sensitivity_grid(scenario_id, pressure_levels=(1.2,))
    with pytest.raises(ValueError, match="Unknown scenario_id"):
        run_sensitivity_grid("ARK-EXT-999")
