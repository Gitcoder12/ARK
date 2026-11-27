import numpy as np
import pytest
from ark.spine import SpineConfig, SpineReflex

def make_spine(**overrides):
    values = dict(risk_indices=(0, 1), inhibitory_indices=(2,),
                  trip_threshold=0.65, release_threshold=0.20,
                  inhibition_gain=0.5, safe_steps_to_release=2)
    values.update(overrides)
    return SpineReflex(SpineConfig(**values))

def test_safe_activity_passes_output_unchanged():
    spine = make_spine()
    output = np.array([0.2, -0.1, 0.7])
    decision = spine.intervene([0.01, 0.02, 0.9], output)
    assert decision.allowed and not decision.reflex_active
    np.testing.assert_array_equal(decision.output, output)

def test_high_risk_activity_trips_and_suppresses_output():
    decision = make_spine().intervene([3.0, 3.0, 0.0], [0.8, 0.4])
    assert not decision.allowed and decision.reflex_active
    np.testing.assert_array_equal(decision.output, np.zeros(2))

def test_inhibitory_pathway_reduces_motor_drive():
    baseline = make_spine(inhibitory_indices=(), inhibition_gain=0.0)
    inhibited = make_spine()
    raw = baseline.propagate([1.0, 1.0, 0.0]).motor_drive
    reduced = inhibited.propagate([1.0, 1.0, 3.0]).motor_drive
    assert reduced < raw

def test_hysteresis_requires_consecutive_safe_steps():
    spine = make_spine()
    spine.intervene([3.0, 3.0, 0.0], [1.0])
    assert not spine.intervene([0.0, 0.0, 0.0], [1.0]).allowed
    assert spine.intervene([0.0, 0.0, 0.0], [1.0]).allowed

def test_invalid_sensory_input_fails_closed():
    spine = make_spine()
    decision = spine.intervene([np.nan, 0.0, 0.0], [1.0, 2.0])
    assert not decision.allowed and decision.reflex_active
    np.testing.assert_array_equal(decision.output, np.zeros(2))

def test_manual_reset_clears_latch():
    spine = make_spine()
    spine.intervene([3.0, 3.0, 0.0], [1.0])
    spine.reset()
    assert not spine.reflex_active

def test_invalid_configuration_is_rejected():
    with pytest.raises(ValueError):
        SpineConfig(risk_indices=(), trip_threshold=0.7)
    with pytest.raises(ValueError):
        SpineConfig(risk_indices=(0,), trip_threshold=0.2, release_threshold=0.3)
