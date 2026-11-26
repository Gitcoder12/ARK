"""Researcher Risk Observatory (RRO).

Evidence-first catalog of documented AI risk concerns, mitigations, and ARK
evaluation coverage. This package is descriptive research infrastructure; it
does not change runtime policy or claim to solve the listed risks.
"""

from ark.observatory.catalog import (
    MITIGATIONS,
    RESEARCHERS,
    RISKS,
    SOURCES,
    get_researcher,
    get_risk,
    search_risks,
    validate_catalog,
)

__all__ = [
    "SOURCES",
    "RESEARCHERS",
    "RISKS",
    "MITIGATIONS",
    "get_researcher",
    "get_risk",
    "search_risks",
    "validate_catalog",
]
