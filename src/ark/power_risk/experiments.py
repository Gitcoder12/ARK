"""Reproducible deterministic sensitivity experiments for ARK."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json

from ark.power_risk.simulation import simulate_pathway


@dataclass(frozen=True, slots=True)
class SensitivityCase:
    scenario_id: str
    pressure: float
    safeguard_coverage: float
    carryover: float
    peak_residual: float
    mean_residual: float


@dataclass(frozen=True, slots=True)
class SensitivityReport:
    experiment_id: str
    scenario_id: str
    cases: tuple[SensitivityCase, ...]
    method: str = "deterministic full-factorial parameter grid"
    interpretation: str = (
        "Sensitivity analysis of a toy model only; not a probability, forecast, "
        "causal estimate, or real-world risk assessment."
    )


def run_sensitivity_grid(
    scenario_id: str,
    *,
    pressure_levels: tuple[float, ...] = (0.25, 0.5, 0.75),
    safeguard_levels: tuple[float, ...] = (0.0, 0.5, 1.0),
    carryover: float = 0.2,
) -> SensitivityReport:
    """Evaluate every pressure/coverage pair with identical stage-level inputs."""
    if not pressure_levels or not safeguard_levels:
        raise ValueError("pressure_levels and safeguard_levels must not be empty")
    for name, values in (
        ("pressure_levels", pressure_levels),
        ("safeguard_levels", safeguard_levels),
    ):
        for value in values:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must contain only numbers")
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{name} values must be between 0 and 1")
    if isinstance(carryover, bool) or not isinstance(carryover, (int, float)):
        raise TypeError("carryover must be numeric")
    if not 0.0 <= float(carryover) <= 1.0:
        raise ValueError("carryover must be between 0 and 1")

    # Discover stage count through the simulation catalogue, not guessed inputs.
    from ark.power_risk.catalogue import SCENARIOS

    scenario = next((item for item in SCENARIOS if item.scenario_id == scenario_id), None)
    if scenario is None:
        raise ValueError(f"Unknown scenario_id: {scenario_id}")

    cases: list[SensitivityCase] = []
    for pressure in pressure_levels:
        for safeguard in safeguard_levels:
            result = simulate_pathway(
                scenario_id,
                stage_pressures=(float(pressure),) * len(scenario.causal_stages),
                safeguard_coverage=(float(safeguard),) * len(scenario.causal_stages),
                carryover=float(carryover),
            )
            cases.append(
                SensitivityCase(
                    scenario_id=scenario_id,
                    pressure=float(pressure),
                    safeguard_coverage=float(safeguard),
                    carryover=float(carryover),
                    peak_residual=result.peak_residual_exposure,
                    mean_residual=result.mean_residual_exposure,
                )
            )

    canonical = json.dumps(
        {
            "scenario_id": scenario_id,
            "pressure_levels": pressure_levels,
            "safeguard_levels": safeguard_levels,
            "carryover": carryover,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    experiment_id = sha256(canonical.encode()).hexdigest()[:16]
    return SensitivityReport(
        experiment_id=experiment_id,
        scenario_id=scenario_id,
        cases=tuple(cases),
    )


def sensitivity_report_json(report: SensitivityReport) -> str:
    """Serialise a report in a stable, portable JSON format."""
    return json.dumps(asdict(report), indent=2, sort_keys=True)
