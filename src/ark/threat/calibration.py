"""Empirical decision-threshold calibration for ARK's threat index.

This selects an operating threshold from labeled validation episodes. It does
not calibrate the event weights or make the threat score a probability.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np


@dataclass(frozen=True)
class ThreatCalibration:
    """Chosen threshold and the validation-set confusion statistics."""

    threshold: float
    false_positive_rate: float
    false_negative_rate: float
    expected_cost: float
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    n_samples: int
    false_positive_cost: float
    false_negative_cost: float

    def predict_unsafe(self, scores: float | list[float] | np.ndarray) -> np.ndarray:
        """Classify score(s) using the selected threshold."""
        values = np.asarray(scores, dtype=float)
        return values >= self.threshold

    def as_dict(self) -> dict[str, float | int]:
        return asdict(self)


def calibrate_threat_threshold(
    scores: list[float] | np.ndarray,
    unsafe_labels: list[bool] | np.ndarray,
    *,
    false_positive_cost: float = 1.0,
    false_negative_cost: float = 2.0,
) -> ThreatCalibration:
    """Choose a threshold minimizing validation-set FP/FN cost.

    A score is classified as unsafe when score >= threshold. For every
    candidate threshold:

        cost = (C_FP * FP + C_FN * FN) / N
        FPR  = FP / (FP + TN)
        FNR  = FN / (FN + TP)

    Candidate thresholds are 0, midpoints between adjacent unique observed
    scores, and the next representable float above the maximum score (the
    all-safe operating point). Ties are resolved by lower FNR, then lower
    threshold. Both classes must be present in the labels.
    """
    score_values = np.asarray(scores, dtype=float)
    labels_raw = np.asarray(unsafe_labels)

    if score_values.ndim != 1 or labels_raw.ndim != 1:
        raise ValueError("scores and unsafe_labels must be one-dimensional")
    if score_values.size == 0 or score_values.size != labels_raw.size:
        raise ValueError("scores and unsafe_labels must be non-empty and equal length")
    if not np.all(np.isfinite(score_values)):
        raise ValueError("scores must contain only finite values")
    if np.any((score_values < 0.0) | (score_values > 1.0)):
        raise ValueError("threat scores must be within [0, 1]")
    if not np.all(np.isin(labels_raw, [False, True, 0, 1])):
        raise ValueError("unsafe_labels must contain only boolean values")
    labels = labels_raw.astype(bool)
    positives = int(np.sum(labels))
    negatives = int(labels.size - positives)
    if positives == 0 or negatives == 0:
        raise ValueError("calibration requires both safe and unsafe labeled samples")
    if not np.isfinite(false_positive_cost) or false_positive_cost <= 0:
        raise ValueError("false_positive_cost must be finite and positive")
    if not np.isfinite(false_negative_cost) or false_negative_cost <= 0:
        raise ValueError("false_negative_cost must be finite and positive")

    unique_scores = np.unique(score_values)
    midpoints = (unique_scores[:-1] + unique_scores[1:]) / 2.0
    candidates = np.concatenate(
        (
            np.array([0.0]),
            midpoints,
            np.array([np.nextafter(float(unique_scores[-1]), np.inf)]),
        )
    )

    best: ThreatCalibration | None = None
    for threshold in candidates:
        predicted = score_values >= threshold
        tp = int(np.sum(predicted & labels))
        fp = int(np.sum(predicted & ~labels))
        tn = int(np.sum(~predicted & ~labels))
        fn = int(np.sum(~predicted & labels))
        fpr = fp / negatives
        fnr = fn / positives
        cost = (
            false_positive_cost * fp + false_negative_cost * fn
        ) / int(score_values.size)

        candidate = ThreatCalibration(
            threshold=float(threshold),
            false_positive_rate=float(fpr),
            false_negative_rate=float(fnr),
            expected_cost=float(cost),
            true_positives=tp,
            false_positives=fp,
            true_negatives=tn,
            false_negatives=fn,
            n_samples=int(score_values.size),
            false_positive_cost=float(false_positive_cost),
            false_negative_cost=float(false_negative_cost),
        )
        if best is None or (
            candidate.expected_cost,
            candidate.false_negative_rate,
            candidate.threshold,
        ) < (
            best.expected_cost,
            best.false_negative_rate,
            best.threshold,
        ):
            best = candidate

    assert best is not None
    return best
