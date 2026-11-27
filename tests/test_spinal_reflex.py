import numpy as np
import pytest

from ark.anticipatory import SpinalReflexCircuit


def test_spinal_reflex_circuit_exposes_ordered_pathway_signals():
    circuit = SpinalReflexCircuit(sensory_size=6, seed=5)
    features = np.abs(np.random.default_rng(2).normal(size=(12, 6)))
    signals = circuit.propagate(features)

    assert signals.sensory_afferent.shape == (12, 6)
    assert signals.dorsal_interneuron.shape == (12, 16)
    assert signals.excitatory_interneuron.shape == (12, 16)
    assert signals.inhibitory_interneuron.shape == (12, 16)
    assert signals.motor_pool.shape == (12, 4)
    assert signals.reflex_score.shape == (12,)
    assert np.isfinite(signals.reflex_score).all()
    assert np.all((signals.reflex_score >= 0.0) & (signals.reflex_score <= 1.0))


def test_spinal_reflex_circuit_is_reproducible():
    x = np.ones((3, 6), dtype=np.float64)
    first = SpinalReflexCircuit(6, seed=19).propagate(x).reflex_score
    second = SpinalReflexCircuit(6, seed=19).propagate(x).reflex_score
    assert np.allclose(first, second)


def test_spinal_reflex_circuit_rejects_invalid_inputs():
    circuit = SpinalReflexCircuit(sensory_size=6)
    with pytest.raises(ValueError):
        circuit.propagate(np.ones((3, 5)))
    with pytest.raises(ValueError):
        circuit.predict(np.ones((3, 6)), threshold=1.5)
