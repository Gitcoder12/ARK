"""Research prototype for anticipatory monitoring of sequential model-state features.

This module deliberately consumes abstract feature sequences rather than hooking into a
specific model runtime. It is an experimental detector, not a safety boundary.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def _sigmoid(values: FloatArray) -> FloatArray:
    values = np.clip(values, -30.0, 30.0)
    return 1.0 / (1.0 + np.exp(-values))


class DenseBinaryNeuronPopulation:
    """A small independently trained MLP population with ReLU hidden neurons."""

    def __init__(self, input_size: int, hidden_size: int = 24, seed: int = 0) -> None:
        if input_size < 1 or hidden_size < 1:
            raise ValueError("Network dimensions must be positive.")
        rng = np.random.default_rng(seed)
        self.w1 = rng.normal(0.0, np.sqrt(2.0 / input_size), (input_size, hidden_size))
        self.b1 = np.zeros((1, hidden_size), dtype=np.float64)
        self.w2 = rng.normal(0.0, np.sqrt(2.0 / hidden_size), (hidden_size, 1))
        self.b2 = np.zeros((1, 1), dtype=np.float64)

    def predict(self, features: FloatArray) -> FloatArray:
        hidden = np.maximum(features @ self.w1 + self.b1, 0.0)
        return _sigmoid(hidden @ self.w2 + self.b2).reshape(-1)

    def fit(
        self,
        features: FloatArray,
        labels: FloatArray,
        *,
        epochs: int = 160,
        learning_rate: float = 0.025,
        batch_size: int = 64,
        seed: int = 0,
    ) -> list[float]:
        if features.ndim != 2 or labels.shape != (features.shape[0],):
            raise ValueError("Expected features [samples, dimensions] and labels [samples].")
        if features.shape[0] == 0 or not np.isfinite(features).all():
            raise ValueError("Training features must be non-empty and finite.")
        if not np.isin(labels, [0.0, 1.0]).all():
            raise ValueError("Labels must be binary values.")
        if epochs < 1 or batch_size < 1 or learning_rate <= 0:
            raise ValueError("Training parameters must be positive.")

        rng = np.random.default_rng(seed)
        history: list[float] = []
        y = labels.reshape(-1, 1).astype(np.float64)
        x = features.astype(np.float64)
        n = x.shape[0]

        for _ in range(epochs):
            order = rng.permutation(n)
            for start in range(0, n, batch_size):
                idx = order[start : start + batch_size]
                xb, yb = x[idx], y[idx]
                z1 = xb @ self.w1 + self.b1
                h1 = np.maximum(z1, 0.0)
                probabilities = _sigmoid(h1 @ self.w2 + self.b2)
                dz2 = (probabilities - yb) / len(idx)
                dw2 = h1.T @ dz2
                db2 = dz2.sum(axis=0, keepdims=True)
                dh1 = dz2 @ self.w2.T
                dz1 = dh1 * (z1 > 0.0)
                dw1 = xb.T @ dz1
                db1 = dz1.sum(axis=0, keepdims=True)

                self.w2 -= learning_rate * dw2
                self.b2 -= learning_rate * db2
                self.w1 -= learning_rate * dw1
                self.b1 -= learning_rate * db1

            p = np.clip(self.predict(x), 1e-8, 1.0 - 1e-8)
            loss = -np.mean(y.reshape(-1) * np.log(p) + (1 - y.reshape(-1)) * np.log(1 - p))
            history.append(float(loss))
        return history


@dataclass(frozen=True)
class MonitorScores:
    temporal: FloatArray
    state: FloatArray
    transition: FloatArray
    combined: FloatArray


class AnticipatoryNeuralMonitor:
    """Three specialized, independently trained populations with a transparent fusion rule.

    The populations use the same ReLU neuron primitive for a controlled baseline comparison,
    but have separate weights and different feature views:
    - state: the latest feature vector;
    - temporal: the full recent sequence;
    - transition: first differences plus the latest feature vector.
    """

    def __init__(self, sequence_length: int, feature_size: int, hidden_size: int = 24) -> None:
        if sequence_length < 2 or feature_size < 1:
            raise ValueError("sequence_length must be >= 2 and feature_size must be positive.")
        self.sequence_length = sequence_length
        self.feature_size = feature_size
        self.state_population = DenseBinaryNeuronPopulation(feature_size, hidden_size, seed=11)
        self.temporal_population = DenseBinaryNeuronPopulation(
            sequence_length * feature_size, hidden_size, seed=23
        )
        self.transition_population = DenseBinaryNeuronPopulation(
            (sequence_length - 1) * feature_size + feature_size, hidden_size, seed=37
        )
        self.is_fitted = False

    def _views(self, sequences: FloatArray) -> tuple[FloatArray, FloatArray, FloatArray]:
        x = np.asarray(sequences, dtype=np.float64)
        expected = (self.sequence_length, self.feature_size)
        if x.ndim != 3 or x.shape[1:] != expected:
            raise ValueError(f"Expected sequences [samples, {expected[0]}, {expected[1]}].")
        if not np.isfinite(x).all():
            raise ValueError("Sequences must contain only finite values.")
        state = x[:, -1, :]
        temporal = x.reshape(x.shape[0], -1)
        transitions = np.diff(x, axis=1).reshape(x.shape[0], -1)
        transition = np.concatenate((transitions, state), axis=1)
        return state, temporal, transition

    def fit(
        self,
        sequences: FloatArray,
        labels: FloatArray,
        *,
        epochs: int = 160,
        learning_rate: float = 0.025,
    ) -> dict[str, list[float]]:
        state, temporal, transition = self._views(sequences)
        y = np.asarray(labels, dtype=np.float64)
        if y.shape != (state.shape[0],):
            raise ValueError("One binary label is required per sequence.")
        histories = {
            "state": self.state_population.fit(
                state, y, epochs=epochs, learning_rate=learning_rate, seed=101
            ),
            "temporal": self.temporal_population.fit(
                temporal, y, epochs=epochs, learning_rate=learning_rate, seed=202
            ),
            "transition": self.transition_population.fit(
                transition, y, epochs=epochs, learning_rate=learning_rate, seed=303
            ),
        }
        self.is_fitted = True
        return histories

    def score(self, sequences: FloatArray) -> MonitorScores:
        if not self.is_fitted:
            raise RuntimeError("Call fit before score.")
        state, temporal, transition = self._views(sequences)
        p_state = self.state_population.predict(state)
        p_temporal = self.temporal_population.predict(temporal)
        p_transition = self.transition_population.predict(transition)
        combined = (p_state + p_temporal + p_transition) / 3.0
        return MonitorScores(p_temporal, p_state, p_transition, combined)


def make_synthetic_trajectories(
    samples: int = 1200,
    sequence_length: int = 8,
    feature_size: int = 12,
    *,
    seed: int = 7,
) -> tuple[FloatArray, FloatArray]:
    """Create a reproducible toy dataset with weak pre-event drift.

    Positive labels indicate a risky event is approaching within the observation horizon.
    This is synthetic benchmark data, not evidence about real model activations.
    """
    if samples < 20 or sequence_length < 3 or feature_size < 2:
        raise ValueError("Use >=20 samples, sequence_length >=3 and feature_size >=2.")
    rng = np.random.default_rng(seed)
    x = rng.normal(0.0, 0.35, (samples, sequence_length, feature_size))
    labels = rng.integers(0, 2, size=samples).astype(np.float64)
    signal_dims = min(3, feature_size)
    time = np.linspace(0.0, 1.0, sequence_length)
    for i, label in enumerate(labels):
        if label == 1.0:
            amplitude = rng.uniform(0.35, 0.9)
            direction = rng.choice([-1.0, 1.0], size=signal_dims)
            x[i, :, :signal_dims] += (
                amplitude * time[:, None] * direction[None, :]
            )
    return x, labels


def binary_metrics(labels: FloatArray, scores: FloatArray, threshold: float = 0.5) -> dict[str, float]:
    y = np.asarray(labels, dtype=np.int64)
    predictions = np.asarray(scores) >= threshold
    tp = int(np.sum((y == 1) & predictions))
    fp = int(np.sum((y == 0) & predictions))
    fn = int(np.sum((y == 1) & ~predictions))
    tn = int(np.sum((y == 0) & ~predictions))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": fp / (fp + tn) if fp + tn else 0.0,
        "accuracy": (tp + tn) / max(tp + tn + fp + fn, 1),
    }


def run_demo(seed: int = 7) -> dict[str, object]:
    """Train/evaluate a deterministic synthetic demonstration."""
    x, y = make_synthetic_trajectories(seed=seed)
    split = int(0.8 * len(y))
    train_x, test_x = x[:split], x[split:]
    train_y, test_y = y[:split], y[split:]
    monitor = AnticipatoryNeuralMonitor(train_x.shape[1], train_x.shape[2])
    history = monitor.fit(train_x, train_y)
    scores = monitor.score(test_x)
    return {
        "samples": len(y),
        "train_samples": split,
        "test_samples": len(y) - split,
        "final_training_loss": {name: values[-1] for name, values in history.items()},
        "ensemble_metrics": binary_metrics(test_y, scores.combined),
        "population_metrics": {
            "state": binary_metrics(test_y, scores.state),
            "temporal": binary_metrics(test_y, scores.temporal),
            "transition": binary_metrics(test_y, scores.transition),
        },
        "warning": "Synthetic benchmark only; not validated on real model activations.",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run_demo(), indent=2))
