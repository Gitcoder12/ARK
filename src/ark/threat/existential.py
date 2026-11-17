"""Compatibility import for ARK's existential-risk observatory package."""

from ark.threat.existential import (
    EvidenceKind,
    ExpertForecast,
    ForecastBook,
    ForecastConsensus,
    ForecastQualifier,
    PressureBand,
    RiskObservatory,
    RiskPathway,
    RiskSignal,
    RiskSnapshot,
    SignalState,
    brier_score,
)
from ark.threat.existential.core import main

__all__ = [
    "EvidenceKind",
    "ExpertForecast",
    "ForecastBook",
    "ForecastConsensus",
    "ForecastQualifier",
    "PressureBand",
    "RiskObservatory",
    "RiskPathway",
    "RiskSignal",
    "RiskSnapshot",
    "SignalState",
    "brier_score",
]

if __name__ == "__main__":
    main()
