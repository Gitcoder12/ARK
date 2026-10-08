"""Threat / extinction meter — rising risk *index* for rogue behavior signals.

Not a real or accurate extinction forecast. Shows which experimental
factors (hazards, reward hacking, safety overrides, etc.) raised the score.
"""

from ark.threat.meter import (
    DEFAULT_WEIGHTS,
    FACTOR_CATALOG,
    ThreatEvent,
    ThreatLevel,
    ThreatMeter,
    explain_factors,
    level_from_score,
)

__all__ = [
    "ThreatMeter",
    "ThreatLevel",
    "ThreatEvent",
    "DEFAULT_WEIGHTS",
    "FACTOR_CATALOG",
    "level_from_score",
    "explain_factors",
]
