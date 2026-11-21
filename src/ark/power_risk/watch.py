"""Evidence-backed, freshness-aware early-warning indicator assessments.

This module classifies supplied observations against explicit thresholds. It
does not scrape sources, infer intent, predict events, or assign probabilities.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from urllib.parse import urlparse

from ark.power_risk.catalogue import EvidenceClass


class WatchStatus(StrEnum):
    UNVERIFIED = "unverified"
    STALE = "stale"
    NORMAL = "normal"
    WATCH = "watch"
    ALERT = "alert"


@dataclass(frozen=True, slots=True)
class WatchRule:
    indicator_id: str
    title: str
    unit: str
    warning_threshold: float
    alert_threshold: float
    higher_is_worse: bool = True
    max_age_days: int = 90

    def __post_init__(self) -> None:
        if not self.indicator_id.strip() or not self.title.strip():
            raise ValueError("indicator_id and title must not be empty")
        if not 0 <= self.warning_threshold <= 1:
            raise ValueError("warning_threshold must be between 0 and 1")
        if not 0 <= self.alert_threshold <= 1:
            raise ValueError("alert_threshold must be between 0 and 1")
        if self.higher_is_worse and self.warning_threshold > self.alert_threshold:
            raise ValueError("warning threshold must not exceed alert threshold")
        if not self.higher_is_worse and self.warning_threshold < self.alert_threshold:
            raise ValueError("for lower-is-worse rules, warning must not be below alert")
        if self.max_age_days < 0:
            raise ValueError("max_age_days must be non-negative")


@dataclass(frozen=True, slots=True)
class WatchObservation:
    indicator_id: str
    value: float
    observed_on: date
    source_name: str
    source_url: str
    evidence_class: EvidenceClass
    limitations: str
    context: str


@dataclass(frozen=True, slots=True)
class WatchAssessment:
    indicator_id: str
    status: WatchStatus
    value: float
    age_days: int
    explanation: str
    requires_human_review: bool = True
    probability_estimate: None = None


def assess_indicator(
    rule: WatchRule,
    observation: WatchObservation,
    *,
    as_of: date,
) -> WatchAssessment:
    """Assess one observation using a transparent threshold and freshness rule."""
    if observation.indicator_id != rule.indicator_id:
        raise ValueError("observation indicator_id does not match rule")
    if isinstance(observation.value, bool) or not isinstance(
        observation.value, (int, float)
    ):
        raise TypeError("observation value must be numeric")
    if not 0.0 <= float(observation.value) <= 1.0:
        raise ValueError("observation value must be between 0 and 1")
    if observation.observed_on > as_of:
        raise ValueError("observation date cannot be in the future")
    if not observation.source_name.strip() or not observation.limitations.strip():
        raise ValueError("source_name and limitations are required")
    parsed = urlparse(observation.source_url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("source_url must be a valid HTTPS URL")

    age = (as_of - observation.observed_on).days
    if observation.evidence_class not in {
        EvidenceClass.VERIFIED,
        EvidenceClass.SUPPORTED_ANALYSIS,
    }:
        status = WatchStatus.UNVERIFIED
        explanation = "Evidence class is not sufficiently supported for signal classification."
    elif age > rule.max_age_days:
        status = WatchStatus.STALE
        explanation = "Observation exceeds the configured freshness window."
    else:
        value = float(observation.value)
        warning = (
            value >= rule.warning_threshold
            if rule.higher_is_worse
            else value <= rule.warning_threshold
        )
        alert = (
            value >= rule.alert_threshold
            if rule.higher_is_worse
            else value <= rule.alert_threshold
        )
        if alert:
            status = WatchStatus.ALERT
            explanation = "Observed value crossed the configured alert threshold."
        elif warning:
            status = WatchStatus.WATCH
            explanation = "Observed value crossed the configured watch threshold."
        else:
            status = WatchStatus.NORMAL
            explanation = "Observed value remains within the configured range."

    return WatchAssessment(
        indicator_id=rule.indicator_id,
        status=status,
        value=round(float(observation.value), 4),
        age_days=age,
        explanation=explanation,
    )


DEFAULT_WATCH_RULES: tuple[WatchRule, ...] = (
    WatchRule(
        "eval_gap", "Pre-deployment / deployment evaluation gap",
        "normalised research rating", 0.5, 0.8, True, 180,
    ),
    WatchRule(
        "incident_transparency", "Incident reporting transparency",
        "normalised research rating", 0.5, 0.2, False, 180,
    ),
    WatchRule(
        "oversight_independence", "Independent oversight strength",
        "normalised research rating", 0.5, 0.2, False, 365,
    ),
    WatchRule(
        "supply_concentration", "Critical AI supply concentration",
        "normalised research rating", 0.5, 0.8, True, 365,
    ),
    WatchRule(
        "cross_border_cooperation", "Cross-border safety cooperation",
        "normalised research rating", 0.5, 0.8, False, 365,
    ),
)
