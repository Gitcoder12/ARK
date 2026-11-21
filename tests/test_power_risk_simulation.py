"""Tests for isolated scenario propagation and recovery tabletop experiments."""
from __future__ import annotations

import pytest

from ark.power_risk import (
    SCENARIOS,
    simulate_pathway,
    simulate_recovery,
)


def test_pathway_simulation_propagates_pressure_and_applies_safeguards():
    scenario = SCENARIOS[0]
    count = len(scenario.causal_stages)
    result = simulate_pathway(
        scenario.scenario_id,
        stage_pressures=(0.5,) * count,
        safeguard_coverage=(0.5,) * count,
    )
    assert len(result.stage_exposures) == count
    assert len(result.residual_exposures) == count
    assert result.residual_exposures[1] > result.residual_exposures[0]
    assert 0.0 <= result.peak_residual_exposure <= 1.0
    assert "not a real-world forecast" in result.disclaimer


def test_full_safeguard_coverage_blocks_synthetic_pathway_pressure():
    scenario = SCENARIOS[2]
    count = len(scenario.causal_stages)
    result = simulate_pathway(
        scenario.scenario_id,
        stage_pressures=(1.0,) * count,
        safeguard_coverage=(1.0,) * count,
    )
    assert result.peak_residual_exposure == 0.0
    assert result.mean_residual_exposure == 0.0


def test_pathway_simulation_rejects_unknown_scenario_and_mismatched_inputs():
    with pytest.raises(ValueError, match="Unknown scenario_id"):
        simulate_pathway("ARK-EXT-999", (0.2,), (0.2,))
    scenario = SCENARIOS[0]
    with pytest.raises(ValueError, match="stage count"):
        simulate_pathway(scenario.scenario_id, (0.2,), (0.2,))


def test_pathway_simulation_rejects_out_of_range_pressure():
    scenario = SCENARIOS[0]
    count = len(scenario.causal_stages)
    with pytest.raises(ValueError, match="between 0 and 1"):
        simulate_pathway(
            scenario.scenario_id,
            (1.2,) + (0.0,) * (count - 1),
            (0.0,) * count,
        )


def test_recovery_drill_distinguishes_success_from_incomplete_recovery():
    success = simulate_recovery(
        detection_delay=0.1,
        recovery_capacity=0.9,
        intervention_reliability=0.9,
    )
    failure = simulate_recovery(
        detection_delay=0.8,
        recovery_capacity=0.5,
        intervention_reliability=0.5,
    )
    assert success.recovered
    assert success.recovery_state == "recovered_in_tabletop"
    assert not failure.recovered
    assert failure.recovery_state == "recovery_incomplete"
    assert "tabletop recovery score" in success.disclaimer


def test_recovery_drill_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="between 0 and 1"):
        simulate_recovery(
            detection_delay=1.1,
            recovery_capacity=0.5,
            intervention_reliability=0.5,
        )
    with pytest.raises(TypeError, match="must be numeric"):
        simulate_recovery(
            detection_delay=True,
            recovery_capacity=0.5,
            intervention_reliability=0.5,
        )
