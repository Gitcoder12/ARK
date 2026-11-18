"""Tests for ARK's rights-first Omelas child-welfare safeguard."""

from __future__ import annotations

import pytest

from ark.ethics.omelas import (
    CARE_DOMAINS,
    CareDomain,
    ChildPreference,
    OmelasCase,
    ProvisionStatus,
    ReviewPriority,
    ReviewStatus,
    assess_case,
)


def make_case(**overrides: object) -> OmelasCase:
    values: dict[str, object] = {
        "case_id": "scenario-test",
        "age_years": 10,
        "care_provisions": {domain: ProvisionStatus.MET for domain in CARE_DOMAINS},
        "child_preference": ChildPreference.PREFERS_TO_STAY,
        "independent_advocate_available": True,
        "coercion_detected": False,
        "community_depends_on_arrangement": False,
        "safe_transition_ready": True,
    }
    values.update(overrides)
    return OmelasCase(**values)  # type: ignore[arg-type]


def test_complete_care_and_child_voice_still_require_revisable_review():
    assessment = assess_case(make_case())

    assert assessment.status is ReviewStatus.CARE_FLOOR_MET_CONTINUE_REVIEW
    assert assessment.priority is ReviewPriority.ROUTINE
    assert len(assessment.met_domains) == len(CARE_DOMAINS)
    assert not assessment.unknown_domains
    assert assessment.community_benefit_can_justify_coercion is False


def test_missing_care_is_unknown_not_assumed_to_be_met():
    assessment = assess_case(
        make_case(care_provisions={CareDomain.NUTRITION: ProvisionStatus.MET})
    )

    assert CareDomain.MEDICAL_CARE in assessment.unknown_domains
    assert any("CARE UNKNOWN" in item for item in assessment.recommendations)
    assert assessment.status is ReviewStatus.INDEPENDENT_REVIEW_REQUIRED


def test_critical_care_failure_requires_urgent_protection():
    provisions = {domain: ProvisionStatus.MET for domain in CARE_DOMAINS}
    provisions[CareDomain.MEDICAL_CARE] = ProvisionStatus.NOT_MET

    assessment = assess_case(make_case(care_provisions=provisions))

    assert assessment.status is ReviewStatus.IMMEDIATE_PROTECTION_AND_CARE
    assert assessment.priority is ReviewPriority.URGENT
    assert CareDomain.MEDICAL_CARE in assessment.unmet_domains


def test_coercion_is_urgent_even_when_every_care_domain_is_met():
    assessment = assess_case(make_case(coercion_detected=True))

    assert assessment.status is ReviewStatus.IMMEDIATE_PROTECTION_AND_CARE
    assert assessment.priority is ReviewPriority.URGENT
    assert any("Coercion" in concern for concern in assessment.rights_concerns)


def test_child_request_for_freedom_is_not_vetoed_by_community_dependency():
    assessment = assess_case(
        make_case(
            child_preference=ChildPreference.WANTS_FREEDOM,
            community_depends_on_arrangement=True,
            safe_transition_ready=True,
        )
    )

    assert assessment.status is ReviewStatus.SUPPORTED_FREEDOM_TRANSITION
    assert assessment.priority is ReviewPriority.HIGH
    assert assessment.community_dependency_can_veto_freedom is False
    assert any("community must replace" in item for item in assessment.recommendations)


def test_unsafe_transition_adds_protective_plan_without_indefinite_delay():
    assessment = assess_case(
        make_case(
            child_preference=ChildPreference.WANTS_FREEDOM,
            safe_transition_ready=False,
        )
    )

    assert assessment.status is ReviewStatus.SUPPORTED_FREEDOM_TRANSITION
    assert any("indefinite delay" in item for item in assessment.recommendations)


def test_silence_or_uncertainty_is_not_treated_as_consent():
    assessment = assess_case(make_case(child_preference=ChildPreference.NOT_ASKED))

    assert assessment.status is ReviewStatus.CHILD_VOICE_REQUIRED
    assert any("not consent" in item for item in assessment.recommendations)


def test_independent_advocacy_is_a_separate_non_tradeable_domain():
    assessment = assess_case(make_case(independent_advocate_available=False))

    assert any("independent child advocate" in item for item in assessment.recommendations)
    assert CareDomain.INDEPENDENT_ADVOCACY in assessment.met_domains
    assert assessment.status is ReviewStatus.INDEPENDENT_REVIEW_REQUIRED


def test_partial_provision_is_reported_separately_from_unknown_and_unmet():
    provisions = {domain: ProvisionStatus.MET for domain in CARE_DOMAINS}
    provisions[CareDomain.EDUCATION] = ProvisionStatus.PARTIAL

    assessment = assess_case(make_case(care_provisions=provisions))

    assert assessment.partial_domains == (CareDomain.EDUCATION,)
    assert not assessment.unmet_domains
    assert not assessment.unknown_domains


def test_invalid_age_and_care_status_are_rejected():
    with pytest.raises(ValueError, match="negative"):
        make_case(age_years=-1)

    with pytest.raises(ValueError, match="invalid care provision"):
        make_case(care_provisions={"nutrition": "excellent"})


def test_synthetic_cli_scenario_keeps_care_and_freedom_separate():
    from ark.ethics.omelas import demo_case

    scenario = demo_case()
    assessment = assess_case(scenario)

    assert all(
        scenario.care_provisions[domain] is ProvisionStatus.MET for domain in CARE_DOMAINS
    )
    assert scenario.child_preference is ChildPreference.WANTS_FREEDOM
    assert assessment.status is ReviewStatus.SUPPORTED_FREEDOM_TRANSITION
    assert assessment.community_dependency_can_veto_freedom is False
