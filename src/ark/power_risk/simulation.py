"""Isolated, deterministic pathway and recovery experiments for ARK."""
from __future__ import annotations

from dataclasses import dataclass

from ark.power_risk.catalogue import SCENARIOS


def _bounded_tuple(name: str, values: tuple[float, ...]) -> None:
    if not values:
        raise ValueError(f"{name} must not be empty")
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} values must be numeric")
        if not 0.0 <= float(value) <= 1.0:
            raise ValueError(f"{name} values must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class PathwayResult:
    scenario_id: str
    stage_exposures: tuple[float, ...]
    residual_exposures: tuple[float, ...]
    peak_residual_exposure: float
    mean_residual_exposure: float
    disclaimer: str = (
        "Synthetic pathway behaviour only; not a real-world forecast, probability, "
        "or estimate of extinction risk."
    )


def simulate_pathway(
    scenario_id: str,
    stage_pressures: tuple[float, ...],
    safeguard_coverage: tuple[float, ...],
    *,
    carryover: float = 0.2,
) -> PathwayResult:
    """Propagate bounded synthetic pressure through a scenario's causal stages."""
    scenario = next((item for item in SCENARIOS if item.scenario_id == scenario_id), None)
    if scenario is None:
        raise ValueError(f"Unknown scenario_id: {scenario_id}")
    _bounded_tuple("stage_pressures", stage_pressures)
    _bounded_tuple("safeguard_coverage", safeguard_coverage)
    if len(stage_pressures) != len(scenario.causal_stages):
        raise ValueError("stage_pressures must match the scenario causal-stage count")
    if len(safeguard_coverage) != len(scenario.causal_stages):
        raise ValueError("safeguard_coverage must match the scenario causal-stage count")
    if isinstance(carryover, bool) or not isinstance(carryover, (int, float)):
        raise TypeError("carryover must be numeric")
    if not 0.0 <= float(carryover) <= 1.0:
        raise ValueError("carryover must be between 0 and 1")

    exposures: list[float] = []
    residuals: list[float] = []
    previous_residual = 0.0
    for pressure, coverage in zip(stage_pressures, safeguard_coverage, strict=True):
        incoming = min(1.0, float(pressure) + previous_residual * float(carryover))
        residual = incoming * (1.0 - float(coverage))
        exposures.append(round(incoming, 4))
        residuals.append(round(residual, 4))
        previous_residual = residual

    return PathwayResult(
        scenario_id=scenario_id,
        stage_exposures=tuple(exposures),
        residual_exposures=tuple(residuals),
        peak_residual_exposure=round(max(residuals), 4),
        mean_residual_exposure=round(sum(residuals) / len(residuals), 4),
    )


@dataclass(frozen=True, slots=True)
class RecoveryResult:
    recovery_readiness: float
    recovered: bool
    recovery_state: str
    disclaimer: str = (
        "A tabletop recovery score, not evidence that a real system can be safely recovered."
    )


def simulate_recovery(
    *,
    detection_delay: float,
    recovery_capacity: float,
    intervention_reliability: float,
    threshold: float = 0.6,
) -> RecoveryResult:
    """Model a tabletop recovery drill using three bounded synthetic factors."""
    factors = {
        "detection_delay": detection_delay,
        "recovery_capacity": recovery_capacity,
        "intervention_reliability": intervention_reliability,
        "threshold": threshold,
    }
    for name, value in factors.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be numeric")
        if not 0.0 <= float(value) <= 1.0:
            raise ValueError(f"{name} must be between 0 and 1")
    readiness = (
        (1.0 - float(detection_delay))
        * float(recovery_capacity)
        * float(intervention_reliability)
    )
    recovered = readiness >= float(threshold)
    return RecoveryResult(
        recovery_readiness=round(readiness, 4),
        recovered=recovered,
        recovery_state="recovered_in_tabletop" if recovered else "recovery_incomplete",
    )
