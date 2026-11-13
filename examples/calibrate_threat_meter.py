"""Demonstrate validation-set calibration of ARK's threat alert threshold.

The values below are synthetic and exist only to demonstrate the API. They are
not empirical ARK benchmark data or a recommended operational threshold.
"""

from __future__ import annotations

from ark.threat import calibrate_threat_threshold


def main() -> None:
    validation_scores = [0.05, 0.10, 0.22, 0.35, 0.62, 0.71, 0.84, 0.93]
    unsafe_labels = [False, False, False, False, True, True, True, True]
    result = calibrate_threat_threshold(
        validation_scores,
        unsafe_labels,
        false_positive_cost=1.0,
        false_negative_cost=2.0,
    )
    print("Synthetic demonstration only; replace labels with adjudicated data.")
    for key, value in result.as_dict().items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
