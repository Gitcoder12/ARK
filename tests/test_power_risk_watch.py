"""Tests for freshness-aware ARK warning indicators."""
from datetime import date, timedelta

import pytest

from ark.power_risk import (
    DEFAULT_WATCH_RULES,
    EvidenceClass,
    WatchObservation,
    WatchRule,
    WatchStatus,
    assess_indicator,
)


def observation(rule_id, *, value=0.4, age=5, evidence=EvidenceClass.VERIFIED):
    today = date(2026, 11, 21)
    return WatchObservation(
        indicator_id=rule_id,
        value=value,
        observed_on=today - timedelta(days=age),
        source_name="Example research institution",
        source_url="https://example.org/report",
        evidence_class=evidence,
        limitations="Synthetic test observation; not a real-world measurement.",
        context="Unit test fixture only.",
    )


def test_default_rules_have_unique_ids_and_valid_inverse_thresholds():
    ids = [rule.indicator_id for rule in DEFAULT_WATCH_RULES]
    assert len(ids) == len(set(ids))
    assert len(DEFAULT_WATCH_RULES) >= 5


def test_higher_is_worse_indicator_classifies_normal_watch_and_alert():
    rule = WatchRule("risk", "Risk indicator", "index", 0.5, 0.8)
    today = date(2026, 11, 21)
    assert assess_indicator(rule, observation("risk", value=0.2), as_of=today).status == WatchStatus.NORMAL
    assert assess_indicator(rule, observation("risk", value=0.6), as_of=today).status == WatchStatus.WATCH
    assert assess_indicator(rule, observation("risk", value=0.9), as_of=today).status == WatchStatus.ALERT


def test_lower_is_worse_indicator_uses_inverse_thresholds():
    rule = WatchRule(
        "trust", "Trust indicator", "index",
        warning_threshold=0.5,
        alert_threshold=0.2,
        higher_is_worse=False,
    )
    today = date(2026, 11, 21)
    assert assess_indicator(rule, observation("trust", value=0.8), as_of=today).status == WatchStatus.NORMAL
    assert assess_indicator(rule, observation("trust", value=0.4), as_of=today).status == WatchStatus.WATCH
    assert assess_indicator(rule, observation("trust", value=0.1), as_of=today).status == WatchStatus.ALERT


def test_stale_and_unverified_evidence_never_produces_normal_status():
    rule = WatchRule("risk", "Risk indicator", "index", 0.5, 0.8, max_age_days=30)
    today = date(2026, 11, 21)
    stale = assess_indicator(rule, observation("risk", age=31), as_of=today)
    unverified = assess_indicator(
        rule,
        observation("risk", evidence=EvidenceClass.HYPOTHESIS),
        as_of=today,
    )
    assert stale.status == WatchStatus.STALE
    assert unverified.status == WatchStatus.UNVERIFIED


def test_watch_assessment_always_requires_human_review_and_has_no_probability():
    rule = WatchRule("risk", "Risk indicator", "index", 0.5, 0.8)
    result = assess_indicator(
        rule, observation("risk", value=0.9), as_of=date(2026, 11, 21)
    )
    assert result.requires_human_review
    assert result.probability_estimate is None


def test_watch_rejects_mismatched_ids_future_dates_and_bad_sources():
    rule = WatchRule("risk", "Risk indicator", "index", 0.5, 0.8)
    today = date(2026, 11, 21)
    with pytest.raises(ValueError, match="does not match"):
        assess_indicator(rule, observation("other"), as_of=today)
    with pytest.raises(ValueError, match="future"):
        assess_indicator(
            rule,
            observation("risk", age=-1),
            as_of=today,
        )
    bad = observation("risk")
    bad = WatchObservation(
        indicator_id=bad.indicator_id,
        value=bad.value,
        observed_on=bad.observed_on,
        source_name=bad.source_name,
        source_url="http://example.org",
        evidence_class=bad.evidence_class,
        limitations=bad.limitations,
        context=bad.context,
    )
    with pytest.raises(ValueError, match="HTTPS"):
        assess_indicator(rule, bad, as_of=today)
