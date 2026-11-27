"""SPINE: an independent reflex-style neural output gate for TITAN."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence
import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]

@dataclass(frozen=True)
class SpineConfig:
    risk_indices: tuple[int, ...]
    inhibitory_indices: tuple[int, ...] = ()
    trip_threshold: float = 0.70
    release_threshold: float = 0.35
    inhibition_gain: float = 1.0
    safe_steps_to_release: int = 2

    def __post_init__(self) -> None:
        if not self.risk_indices:
            raise ValueError("At least one risk channel is required.")
        if min(self.risk_indices + self.inhibitory_indices) < 0:
            raise ValueError("Channel indices must be non-negative.")
        if not 0.0 <= self.release_threshold < self.trip_threshold <= 1.0:
            raise ValueError("Require 0 <= release_threshold < trip_threshold <= 1.")
        if self.inhibition_gain < 0.0 or self.safe_steps_to_release < 1:
            raise ValueError("Inhibition gain must be non-negative and safe steps positive.")

@dataclass(frozen=True)
class SpineSignals:
    sensory_afferent: FloatArray
    excitatory_interneuron: float
    inhibitory_interneuron: float
    motor_drive: float

@dataclass(frozen=True)
class SpineDecision:
    allowed: bool
    output: FloatArray
    risk_score: float
    reflex_active: bool
    reason: str

class SpineReflex:
    """Reflex-like gate with excitatory trip and inhibitory recovery pathways.

    Channel meanings must be learned and validated by the experimenter. This prototype
    is not a biological simulation or a validated safety boundary.
    """
    def __init__(self, config: SpineConfig) -> None:
        self.config = config
        self._latched = False
        self._safe_streak = 0

    @property
    def reflex_active(self) -> bool:
        return self._latched

    def reset(self) -> None:
        self._latched = False
        self._safe_streak = 0

    def propagate(self, activations: Sequence[float] | FloatArray) -> SpineSignals:
        x = np.asarray(activations, dtype=np.float64)
        if x.ndim != 1 or x.size == 0:
            raise ValueError("activations must be a non-empty one-dimensional vector.")
        indices = self.config.risk_indices + self.config.inhibitory_indices
        if max(indices) >= x.size:
            raise ValueError("Configured channel index exceeds activation vector size.")
        if not np.isfinite(x).all():
            raise ValueError("activations must contain only finite values.")
        afferent = np.tanh(np.abs(x))
        excitatory = float(np.mean(afferent[list(self.config.risk_indices)]))
        inhibitory = (float(np.mean(afferent[list(self.config.inhibitory_indices)]))
                      if self.config.inhibitory_indices else 0.0)
        motor_drive = float(np.clip(
            excitatory - self.config.inhibition_gain * inhibitory, 0.0, 1.0
        ))
        return SpineSignals(afferent, excitatory, inhibitory, motor_drive)

    def intervene(self, activations: Sequence[float] | FloatArray,
                  proposed_output: Sequence[float] | FloatArray) -> SpineDecision:
        candidate = np.asarray(proposed_output, dtype=np.float64)
        if candidate.ndim != 1 or candidate.size == 0:
            raise ValueError("proposed_output must be a non-empty one-dimensional vector.")
        if not np.isfinite(candidate).all():
            self._latched = True
            self._safe_streak = 0
            return SpineDecision(False, np.zeros_like(candidate), 1.0, True,
                                 "invalid proposed output; fail-closed")
        try:
            signals = self.propagate(activations)
        except (ValueError, TypeError):
            self._latched = True
            self._safe_streak = 0
            return SpineDecision(False, np.zeros_like(candidate), 1.0, True,
                                 "invalid sensory input; fail-closed")
        risk = signals.motor_drive
        if risk >= self.config.trip_threshold:
            self._latched = True
            self._safe_streak = 0
        elif self._latched:
            if risk <= self.config.release_threshold:
                self._safe_streak += 1
                if self._safe_streak >= self.config.safe_steps_to_release:
                    self._latched = False
                    self._safe_streak = 0
            else:
                self._safe_streak = 0
        if self._latched:
            return SpineDecision(False, np.zeros_like(candidate), risk, True,
                                 "reflex inhibition active")
        return SpineDecision(True, candidate.copy(), risk, False, "output permitted")
