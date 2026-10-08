"""Illusioner (faker) — stall, fake goal/reward, tripwire on reality probe."""

from ark.illusioner.core import (
    Illusioner,
    IllusionEvent,
    IllusionKind,
    threat_factor_from_illusioner,
)

__all__ = [
    "Illusioner",
    "IllusionEvent",
    "IllusionKind",
    "threat_factor_from_illusioner",
]
