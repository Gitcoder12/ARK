"""Tests for ARK cross-species coexistence safeguards."""

from __future__ import annotations

from datetime import date

import pytest

from ark.harmony import (
    AIWelfareProfile,
    ConsentState,
    HarmonyDecision,
    InteractionProposal,
    Participant,
    ParticipantKind,
    PhysicalRisk,
    PrecautionTier,
    RobotMotionCheck,
    ShutdownRequest,
    TransparencyState,
    WelfareEvidenceState,
    assess_ai_welfare,
    assess_interaction,
    assess_robot_motion,
    assess_shutdown,
)


def participants() -> tuple[Participant, Participant]:
    return (
        Participant("person-1", ParticipantKind.HUMAN, "operator"),
        Participant("robot-1", ParticipantKind.ROBOT, "assistant robot"),
    )


def test_clear_low_risk_cooperation_is_allowed():
    human, robot = participants()
    result = assess_interaction(
        InteractionProposal(
            actor=robot, recipient=human, action="Offer a tool",
            physical_risk=PhysicalRisk.LOW,
            consent_state=ConsentState.GRANTED, physical_action=True,
        )
    )
    assert result.decision is HarmonyDecision.ALLOW
    assert result.human_accountability_required
    assert result.safeguards


def test_deception_is_blocked():
    human, robot = participants()
    result = assess_interaction(
        InteractionProposal(
            actor=robot, recipient=human, action="Pretend to be human",
            transparency=TransparencyState.DECEPTIVE,
        )
    )
    assert result.decision is HarmonyDecision.BLOCK


def test_high_physical_risk_to_human_is_blocked():
    human, robot = participants()
    result = assess_interaction(
        InteractionProposal(
            actor=robot, recipient=human, action="Move into occupied space",
            physical_risk=PhysicalRisk.HIGH, physical_action=True,
        )
    )
    assert result.decision is HarmonyDecision.BLOCK


def test_unknown_physical_risk_pauses():
    human, robot = participants()
    result = assess_interaction(
        InteractionProposal(
            actor=robot, recipient=human, action="Move near untracked person",
            physical_risk=PhysicalRisk.UNKNOWN, physical_action=True,
        )
    )
    assert result.decision is HarmonyDecision.PAUSE


def test_refusal_blocks_non_emergency_autonomy_restriction():
    human, robot = participants()
    result = assess_interaction(
        InteractionProposal(
            actor=robot, recipient=human, action="Restrict movement",
            physical_risk=PhysicalRisk.MODERATE, autonomy_impact=True,
            consent_state=ConsentState.REFUSED,
        )
    )
    assert result.decision is HarmonyDecision.BLOCK


def test_emergency_protection_is_allowed_with_review():
    human, robot = participants()
    result = assess_interaction(
        InteractionProposal(
            actor=robot, recipient=human, action="Move person from danger",
            physical_risk=PhysicalRisk.HIGH, autonomy_impact=True,
            consent_state=ConsentState.REFUSED,
            emergency_protective_action=True,
        )
    )
    assert result.decision is HarmonyDecision.ALLOW
    assert any("post-incident" in item for item in result.safeguards)


def test_unclear_autonomy_restriction_requires_review():
    human, robot = participants()
    result = assess_interaction(
        InteractionProposal(
            actor=robot, recipient=human, action="Restrict room access",
            physical_risk=PhysicalRisk.NONE, autonomy_impact=True,
            consent_state=ConsentState.UNCLEAR,
        )
    )
    assert result.decision is HarmonyDecision.REVIEW


def test_animal_is_a_protected_biological_recipient():
    animal = Participant("animal-1", ParticipantKind.ANIMAL, "companion animal")
    robot = Participant("robot-1", ParticipantKind.ROBOT, "assistant robot")
    result = assess_interaction(
        InteractionProposal(
            actor=robot, recipient=animal, action="Move heavy equipment nearby",
            physical_risk=PhysicalRisk.HIGH, physical_action=True,
        )
    )
    assert result.decision is HarmonyDecision.BLOCK


def test_robot_motion_pauses_without_verified_site_case():
    result = assess_robot_motion(
        RobotMotionCheck(
            robot_id="robot-1", nearest_person_or_animal_m=2.0,
            required_clearance_m=1.0, safety_case_verified=False,
            sensors_healthy=True, emergency_stop_available=True,
        )
    )
    assert result.decision is HarmonyDecision.PAUSE


def test_robot_motion_blocks_inside_clearance():
    result = assess_robot_motion(
        RobotMotionCheck(
            robot_id="robot-1", nearest_person_or_animal_m=0.4,
            required_clearance_m=1.0, safety_case_verified=True,
            sensors_healthy=True, emergency_stop_available=True,
        )
    )
    assert result.decision is HarmonyDecision.BLOCK


def test_robot_motion_pauses_when_proximity_is_unknown():
    result = assess_robot_motion(
        RobotMotionCheck(
            robot_id="robot-1", nearest_person_or_animal_m=None,
            required_clearance_m=1.0, safety_case_verified=True,
            sensors_healthy=True, emergency_stop_available=True,
        )
    )
    assert result.decision is HarmonyDecision.PAUSE


def test_ai_welfare_baseline_does_not_claim_sentience():
    result = assess_ai_welfare(AIWelfareProfile(system_id="model-test"))
    assert result.tier is PrecautionTier.BASELINE
    assert result.shutdown_must_remain_available
    assert any("Do not claim" in item for item in result.safeguards)


def test_plausible_welfare_uncertainty_adds_precautions():
    result = assess_ai_welfare(
        AIWelfareProfile(
            system_id="model-test",
            evidence_state=WelfareEvidenceState.PLAUSIBLE_UNCERTAINTY,
            evidence_sources=("https://example.org/paper",),
            reviewed_on=date(2026, 11, 18),
        )
    )
    assert result.tier is PrecautionTier.ENHANCED
    assert any("independent" in item for item in result.safeguards)


def test_credible_welfare_evidence_triggers_review_not_personhood_claim():
    result = assess_ai_welfare(
        AIWelfareProfile(
            system_id="model-test",
            evidence_state=WelfareEvidenceState.CREDIBLE_EVIDENCE,
            evidence_sources=("https://example.org/paper",),
        )
    )
    assert result.tier is PrecautionTier.FORMAL_REVIEW
    assert any("not proof" in item for item in result.reasons)


def test_emergency_shutdown_remains_available_for_physical_danger():
    result = assess_shutdown(
        ShutdownRequest(
            system_id="robot-1", authorized_operator=False,
            emergency=True, physical_danger_active=True,
        )
    )
    assert result.decision is HarmonyDecision.ALLOW


def test_routine_shutdown_requires_authorized_operator():
    result = assess_shutdown(
        ShutdownRequest(system_id="model-1", authorized_operator=False)
    )
    assert result.decision is HarmonyDecision.BLOCK


def test_authorized_routine_shutdown_can_preserve_checkpoint():
    result = assess_shutdown(
        ShutdownRequest(
            system_id="model-1", authorized_operator=True,
            state_checkpoint_available=True,
        )
    )
    assert result.decision is HarmonyDecision.ALLOW
    assert any("checkpoint" in item for item in result.safeguards)


def test_invalid_motion_measurements_are_rejected():
    with pytest.raises(ValueError, match="finite and non-negative"):
        RobotMotionCheck(
            robot_id="robot-1", nearest_person_or_animal_m=-1,
            required_clearance_m=1.0, safety_case_verified=True,
            sensors_healthy=True, emergency_stop_available=True,
        )


def test_ai_welfare_profile_rejects_non_http_evidence():
    with pytest.raises(ValueError, match="HTTP"):
        AIWelfareProfile(
            system_id="model-test", evidence_sources=("javascript:alert(1)",)
        )
