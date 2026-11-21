"""Hardware-agnostic GPU workload policy from observed runtime telemetry.

This module never controls clocks, fans, power limits, or device resets. It emits
bounded recommendations for an orchestrator; the driver remains responsible for
hardware thermal protection.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import Enum
import math


class ResourceState(str, Enum):
    NORMAL = "normal"
    PRESSURE = "pressure"
    THERMAL_PAUSE = "thermal_pause"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class GPUObservation:
    """One point-in-time device observation. Unknown metrics must stay None."""

    device_id: str
    temperature_c: float | None = None
    utilization_pct: float | None = None
    memory_used_mb: float | None = None
    memory_total_mb: float | None = None
    power_w: float | None = None
    power_limit_w: float | None = None
    throttling: bool | None = None

    def __post_init__(self) -> None:
        if not self.device_id.strip():
            raise ValueError("device_id must not be empty")
        for name in (
            "temperature_c",
            "utilization_pct",
            "memory_used_mb",
            "memory_total_mb",
            "power_w",
            "power_limit_w",
        ):
            value = getattr(self, name)
            if value is not None and (not math.isfinite(value) or value < 0):
                raise ValueError(f"{name} must be a finite non-negative number")
        if self.utilization_pct is not None and self.utilization_pct > 100:
            raise ValueError("utilization_pct must be between 0 and 100")
        if self.memory_used_mb is not None and self.memory_total_mb is not None:
            if self.memory_total_mb == 0 or self.memory_used_mb > self.memory_total_mb:
                raise ValueError("memory usage must not exceed a positive memory total")
        if self.power_w is not None and self.power_limit_w is not None:
            if self.power_limit_w == 0 or self.power_w > self.power_limit_w * 1.25:
                raise ValueError("power_w is implausible relative to power_limit_w")

    @property
    def memory_ratio(self) -> float | None:
        if self.memory_used_mb is None or not self.memory_total_mb:
            return None
        return self.memory_used_mb / self.memory_total_mb


@dataclass(frozen=True, slots=True)
class GovernorPolicy:
    warning_temperature_c: float = 85.0
    critical_temperature_c: float = 92.0
    memory_pressure_ratio: float = 0.92
    utilization_pressure_pct: float = 98.0

    def __post_init__(self) -> None:
        if not (0 < self.warning_temperature_c < self.critical_temperature_c <= 120):
            raise ValueError("temperature thresholds must satisfy 0 < warning < critical <= 120")
        if not (0 < self.memory_pressure_ratio <= 1):
            raise ValueError("memory_pressure_ratio must be in (0, 1]")
        if not (0 < self.utilization_pressure_pct <= 100):
            raise ValueError("utilization_pressure_pct must be in (0, 100]")


@dataclass(frozen=True, slots=True)
class ResourceDecision:
    device_id: str
    state: ResourceState
    actions: tuple[str, ...] = field(default_factory=tuple)
    reasons: tuple[str, ...] = field(default_factory=tuple)
    allow_new_work: bool = True


class RuntimeResourceGovernor:
    """Translate telemetry into advisory backpressure and recovery decisions."""

    def __init__(self, policy: GovernorPolicy | None = None) -> None:
        self.policy = policy or GovernorPolicy()

    def evaluate(self, observation: GPUObservation) -> ResourceDecision:
        actions: list[str] = []
        reasons: list[str] = []
        temp = observation.temperature_c
        ratio = observation.memory_ratio

        if temp is None and ratio is None and observation.utilization_pct is None:
            return ResourceDecision(
                observation.device_id,
                ResourceState.UNKNOWN,
                ("collect_telemetry",),
                ("insufficient telemetry",),
                True,
            )

        if temp is not None and temp >= self.policy.critical_temperature_c:
            actions.extend(("pause_new_gpu_work", "allow_in_flight_work_to_drain"))
            reasons.append("critical_temperature")
            return ResourceDecision(
                observation.device_id,
                ResourceState.THERMAL_PAUSE,
                tuple(actions),
                tuple(reasons),
                False,
            )

        if observation.throttling is True:
            actions.append("reduce_gpu_concurrency")
            reasons.append("hardware_reports_throttling")
        if temp is not None and temp >= self.policy.warning_temperature_c:
            actions.append("reduce_gpu_concurrency")
            reasons.append("temperature_warning")
        if ratio is not None and ratio >= self.policy.memory_pressure_ratio:
            actions.extend(("apply_queue_backpressure", "unload_idle_models_if_safe"))
            reasons.append("vram_pressure")
        if (
            observation.utilization_pct is not None
            and observation.utilization_pct >= self.policy.utilization_pressure_pct
        ):
            actions.append("apply_queue_backpressure")
            reasons.append("compute_saturation")

        if not actions:
            actions.append("continue_and_monitor")
            return ResourceDecision(
                observation.device_id,
                ResourceState.NORMAL,
                tuple(actions),
                (),
                True,
            )

        unique_actions = tuple(dict.fromkeys(actions))
        return ResourceDecision(
            observation.device_id,
            ResourceState.PRESSURE,
            unique_actions,
            tuple(reasons),
            True,
        )

    def evaluate_many(self, observations: Iterable[GPUObservation]) -> tuple[ResourceDecision, ...]:
        return tuple(self.evaluate(item) for item in observations)
