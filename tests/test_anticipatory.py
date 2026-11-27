import numpy as np
import pytest

from ark.anticipatory import (
    AnticipatoryNeuralMonitor,
    binary_metrics,
    make_synthetic_trajectories,
)


def test_synthetic_data_is_reproducible_and_well_shaped():
    first = make_synthetic_trajectories(samples=80, seed=9)
    second = make_synthetic_trajectories(samples=80, seed=9)
    assert first[0].shape == (80, 8, 12)
    assert np.array_equal(first[0], second[0])
    assert np.array_equal(first[1], second[1])


def test_monitor_trains_and_returns_three_population_scores():
    x, y = make_synthetic_trajectories(samples=120, seed=3)
    monitor = AnticipatoryNeuralMonitor(sequence_length=8, feature_size=12)
    with pytest.raises(RuntimeError):
        monitor.score(x[:4])

    monitor.fit(x[:90], y[:90], epochs=8)
    scores = monitor.score(x[90:])
    assert scores.combined.shape == (30,)
    assert np.isfinite(scores.combined).all()
    assert np.allclose(
        scores.combined,
        (scores.state + scores.temporal + scores.transition) / 3.0,
    )


def test_monitor_rejects_wrong_sequence_shape():
    monitor = AnticipatoryNeuralMonitor(sequence_length=8, feature_size=12)
    with pytest.raises(ValueError):
        monitor.fit(np.zeros((10, 7, 12)), np.zeros(10), epochs=2)


def test_binary_metrics_handles_perfect_predictions():
    result = binary_metrics(np.array([0, 1, 1, 0]), np.array([0.1, 0.9, 0.8, 0.2]))
    assert result["precision"] == 1.0
    assert result["recall"] == 1.0
    assert result["f1"] == 1.0
    assert result["false_positive_rate"] == 0.0
