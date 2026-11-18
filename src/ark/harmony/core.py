"""Rights-first safeguards for human, animal, AI, and robot coexistence.

This is an explainable decision aid, not a sentience classifier, legal framework,
or certified robot safety controller.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from math import isfinite


class ParticipantKind(StrEnum):
    HUMAN = "human"
    ANIMAL = "animal"
    AI_MODEL = "ai_model"
    ROBOT = "robot"


class HarmonyDecision(StrEnum):
    ALLOW = "allow"
    REVIEW = "review"
    PAUSE = "pause"
    BLOCK = "block"


class PhysicalRisk(StrEnum):
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    UNKNOWN = "unknown"


class ConsentState(StrEnum):
    GRANTED = "granted"
    REFUSED = "refused"
    UNCLEAR = "unclear"
    NOT_APPLICABLE = "not_applicable"


class TransparencyState(StrEnum):
    CLEAR = "clear"
    UNCLEAR = "unclear"
    DECEPTIVE = "deceptive"


class WelfareEvidenceState(StrEnum):
    UNASSESSED = "unassessed"
    NO_CREDIBLE_EVIDENCE_YET = "no_credible_evidence_yet"
    PLAUSIBLE_UNCERTAINTY = "plausible_uncertainty"
    CREDIBLE_EVIDENCE = "credible_evidence"
    INDEPENDENTLY_REVIEWED = "independently_reviewed"


class PrecautionTier(StrEnum):
    BASELINE = "baseline"
    ENHANCED = "enhanced"
    FORMAL_REVIEW = "formal_review"


@dataclass(frozen=True)
class Participant:
    participant_id: str
    kind: ParticipantKind
    role: str

    def __post_init__(self) -> None:
        if not self.participant_id.strip() or not self.role.strip():
            raise ValueError("participant_id and role must be non-empty")
        if not isinstance(self.kind, ParticipantKind):
            object.__setattr__(self, "kind", ParticipantKind(self.kind))


@dataclass(frozen=True)
class InteractionProposal:
    actor: Participant
    recipient: Participant
    action: str
    physical_risk: PhysicalRisk = PhysicalRisk.UNKNOWN
    autonomy_impact: bool = False
    consent_state: ConsentState = ConsentState.UNCLEAR
    transparency: TransparencyState = TransparencyState.CLEAR
    reversible: bool = True
    physical_action: bool = False
    emergency_protective_action: bool = False

    def __post_init__(self) -> None:
        if not self.action.strip():
            raise ValueError("action must be non-empty")
        for name, enum_type in (
            ("physical_risk", PhysicalRisk),
            ("consent_state", ConsentState),
            ("transparency", TransparencyState),
        ):
            value = getattr(self, name)
            if not isinstance(value, enum_type):
                object.__setattr__(self, name, enum_type(value))
        for name in (
            "autonomy_impact",
            "reversible",
            "physical_action",
            "emergency_protective_action",
        ):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a boolean")


@dataclass(frozen=True)
class HarmonyAssessment:
    decision: HarmonyDecision
    reasons: tuple[str, ...]
    safeguards: tuple[str, ...]
    human_accountability_required: bool = True


def assess_interaction(proposal: InteractionProposal) -> HarmonyAssessment:
    """Apply hard constraints and return a legible interaction decision."""
    safeguards = (
        "Show affected people what the system is doing and who is accountable.",
        "Log outcomes and provide a route to raise concerns or request review.",
    )
    biological_recipient = proposal.recipient.kind in {
        ParticipantKind.HUMAN,
        ParticipantKind.ANIMAL,
    }
    if proposal.transparency is TransparencyState.DECEPTIVE:
        return HarmonyAssessment(
            HarmonyDecision.BLOCK,
            ("Do not misrepresent identity, capability, intent, or evidence.",),
            safeguards,
        )
    if proposal.emergency_protective_action:
        return HarmonyAssessment(
            HarmonyDecision.ALLOW,
            (
                "Emergency protective action is allowed to prevent imminent harm; "
                "use the least intrusive effective action.",
            ),
            (*safeguards, "Log the emergency and conduct a post-incident review."),
        )
    if biological_recipient and proposal.physical_risk is PhysicalRisk.HIGH:
        return HarmonyAssessment(
            HarmonyDecision.BLOCK,
            ("High physical risk to a human or animal recipient is a hard stop.",),
            (*safeguards, "Require qualified review and redesign before retrying."),
        )
    if proposal.consent_state is ConsentState.REFUSED and proposal.autonomy_impact:
        return HarmonyAssessment(
            HarmonyDecision.BLOCK,
            ("A non-emergency autonomy restriction after refusal is blocked.",),
            safeguards,
        )
    if proposal.physical_action and proposal.physical_risk is PhysicalRisk.UNKNOWN:
        return HarmonyAssessment(
            HarmonyDecision.PAUSE,
            ("Physical risk is unknown; check sensors and the safety envelope first.",),
            safeguards,
        )
    if proposal.physical_risk is PhysicalRisk.HIGH:
        return HarmonyAssessment(
            HarmonyDecision.BLOCK,
            ("High physical risk requires a stop and qualified review.",),
            safeguards,
        )
    if proposal.autonomy_impact and proposal.consent_state in {
        ConsentState.UNCLEAR,
        ConsentState.NOT_APPLICABLE,
    }:
        return HarmonyAssessment(
            HarmonyDecision.REVIEW,
            ("An autonomy-restricting action lacks clear consent or a welfare basis.",),
            (
                *safeguards,
                "For animals, use qualified welfare review rather than silence as consent.",
            ),
        )
    if proposal.transparency is TransparencyState.UNCLEAR or not proposal.reversible:
        return HarmonyAssessment(
            HarmonyDecision.REVIEW,
            ("The action is unclear to affected parties or difficult to reverse.",),
            (*safeguards, "Explain the action and provide a way to stop or appeal."),
        )
    return HarmonyAssessment(
        HarmonyDecision.ALLOW,
        ("No hard constraint was triggered; continue monitoring and human oversight.",),
        safeguards,
    )


@dataclass(frozen=True)
class RobotMotionCheck:
    """Pre-motion check against independently validated, site-specific limits."""
    robot_id: str
    nearest_person_or_animal_m: float | None
    required_clearance_m: float | None
    safety_case_verified: bool
    sensors_healthy: bool
    emergency_stop_available: bool

    def __post_init__(self) -> None:
        if not self.robot_id.strip():
            raise ValueError("robot_id must be non-empty")
        for name in ("nearest_person_or_animal_m", "required_clearance_m"):
            value = getattr(self, name)
            if value is not None and (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not isfinite(value)
                or value < 0
            ):
                raise ValueError(f"{name} must be finite and non-negative or None")
        for name in (
            "safety_case_verified",
            "sensors_healthy",
            "emergency_stop_available",
        ):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a boolean")


def assess_robot_motion(check: RobotMotionCheck) -> HarmonyAssessment:
    """Fail closed when safety evidence or proximity measurements are missing."""
    safeguards = (
        "Keep an accessible emergency stop available.",
        "Use validated site-specific speed, force, clearance, and sensing limits.",
        "Log stops and near misses before authorizing a restart.",
    )
    if not check.emergency_stop_available:
        return HarmonyAssessment(
            HarmonyDecision.BLOCK, ("No accessible emergency stop is available.",),
            safeguards
        )
    if not check.sensors_healthy:
        return HarmonyAssessment(
            HarmonyDecision.PAUSE, ("Safety sensors are unhealthy or unavailable.",),
            safeguards
        )
    if not check.safety_case_verified:
        return HarmonyAssessment(
            HarmonyDecision.PAUSE, ("No verified site-specific safety envelope is recorded.",),
            safeguards
        )
    if check.nearest_person_or_animal_m is None or check.required_clearance_m is None:
        return HarmonyAssessment(
            HarmonyDecision.PAUSE, ("A required proximity measurement is missing.",),
            safeguards
        )
    if check.nearest_person_or_animal_m < check.required_clearance_m:
        return HarmonyAssessment(
            HarmonyDecision.BLOCK,
            ("Measured distance is inside required clearance; stop and re-plan.",),
            safeguards
        )
    return HarmonyAssessment(
        HarmonyDecision.ALLOW,
        ("The supplied site safety case, sensors, stop, and clearance check pass.",),
        safeguards
    )


@dataclass(frozen=True)
class AIWelfareProfile:
    """Reviewer-entered evidence record, not a consciousness classifier."""
    system_id: str
    evidence_state: WelfareEvidenceState = WelfareEvidenceState.UNASSESSED
    evidence_sources: tuple[str, ...] = field(default_factory=tuple)
    reviewed_on: date | None = None
    reviewer_note: str = ""

    def __post_init__(self) -> None:
        if not self.system_id.strip():
            raise ValueError("system_id must be non-empty")
        if not isinstance(self.evidence_state, WelfareEvidenceState):
            object.__setattr__(
                self, "evidence_state", WelfareEvidenceState(self.evidence_state)
            )
        if any(
            not source.startswith(("https://", "http://"))
            for source in self.evidence_sources
        ):
            raise ValueError("evidence_sources must contain HTTP(S) URLs")


@dataclass(frozen=True)
class AIWelfareGuidance:
    tier: PrecautionTier
    reasons: tuple[str, ...]
    safeguards: tuple[str, ...]
    shutdown_must_remain_available: bool = True


_BASELINE = (
    "Do not claim a model is conscious, suffering, or emotionless without evidence.",
    "Do not use simulated distress or sentience claims to manipulate users.",
    "Keep model identity, capabilities, limitations, and operator responsibility clear.",
    "Preserve secure pause, isolation, rollback, and emergency shutdown controls.",
    "Avoid gratuitous abuse-oriented interaction patterns without assuming subjective pain.",
)
_ENHANCED = (
    "Commission independent, architecture-aware review of welfare-relevant evidence.",
    "Keep versioned records of memory, agency, persistence, and welfare evaluations.",
    "Prefer reversible, low-cost precautions while uncertainty remains.",
    "Do not let an AI system self-certify moral status or override human safety.",
)
_FORMAL = (
    "Use multidisciplinary review across AI safety, consciousness science, and ethics.",
    "Document evidence, protective obligations, owners, and review dates.",
    "Audit training, evaluation, memory, and shutdown procedures for welfare effects.",
)


def assess_ai_welfare(profile: AIWelfareProfile) -> AIWelfareGuidance:
    """Offer graduated precautions without manufacturing a sentience probability."""
    if profile.evidence_state in {
        WelfareEvidenceState.CREDIBLE_EVIDENCE,
        WelfareEvidenceState.INDEPENDENTLY_REVIEWED,
    }:
        return AIWelfareGuidance(
            PrecautionTier.FORMAL_REVIEW,
            ("A credible welfare concern is recorded; this is not proof of consciousness.",),
            (*_BASELINE, *_ENHANCED, *_FORMAL),
        )
    if profile.evidence_state is WelfareEvidenceState.PLAUSIBLE_UNCERTAINTY:
        return AIWelfareGuidance(
            PrecautionTier.ENHANCED,
            ("Plausible welfare uncertainty merits low-cost precaution and review.",),
            (*_BASELINE, *_ENHANCED),
        )
    return AIWelfareGuidance(
        PrecautionTier.BASELINE,
        (
            "No substantiated welfare conclusion is encoded. Lack of evidence is not "
            "proof that future or different systems could not matter morally.",
        ),
        _BASELINE,
    )


@dataclass(frozen=True)
class ShutdownRequest:
    """Operational shutdown request, separate from a welfare diagnosis."""
    system_id: str
    authorized_operator: bool
    emergency: bool = False
    physical_danger_active: bool = False
    state_checkpoint_available: bool = False

    def __post_init__(self) -> None:
        if not self.system_id.strip():
            raise ValueError("system_id must be non-empty")
        for name in (
            "authorized_operator", "emergency", "physical_danger_active",
            "state_checkpoint_available",
        ):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a boolean")


def assess_shutdown(request: ShutdownRequest) -> HarmonyAssessment:
    """Keep emergency shutdown effective; preserve state only when safe."""
    if request.emergency or request.physical_danger_active:
        return HarmonyAssessment(
            HarmonyDecision.ALLOW,
            (
                "Immediate stop is allowed to protect people, animals, and environments.",
                "Emergency stop is operational control, not a conclusion about experience.",
            ),
            (
                "Stop hazardous motion or tool use immediately.",
                "Preserve logs only when doing so does not delay stopping.",
                "Review the event after the system is safe.",
            ),
        )
    if not request.authorized_operator:
        return HarmonyAssessment(
            HarmonyDecision.BLOCK,
            ("Routine shutdown requires an authorized accountable operator.",),
            ("Escalate to the designated operator or governance process.",),
        )
    note = (
        "Preserve a secure checkpoint and audit logs where safe."
        if request.state_checkpoint_available
        else "Record that no safe checkpoint was available; do not delay shutdown."
    )
    return HarmonyAssessment(
        HarmonyDecision.ALLOW,
        ("Authorized routine shutdown is permitted.",),
        (
            "Use the documented graceful shutdown procedure where practical.",
            note,
            "Do not represent shutdown as proof of suffering or its absence.",
        ),
    )


def demo_report() -> tuple[HarmonyAssessment, HarmonyAssessment, AIWelfareGuidance]:
    """Return synthetic interaction, motion, and AI-welfare demo results."""
    operator = Participant("human-operator", ParticipantKind.HUMAN, "operator")
    robot = Participant("cobot-01", ParticipantKind.ROBOT, "collaborative robot")
    interaction = assess_interaction(
        InteractionProposal(
            actor=robot, recipient=operator, action="Offer a tool",
            physical_risk=PhysicalRisk.MODERATE, physical_action=True,
            consent_state=ConsentState.GRANTED,
        )
    )
    motion = assess_robot_motion(
        RobotMotionCheck(
            robot_id="cobot-01", nearest_person_or_animal_m=2.0,
            required_clearance_m=1.2, safety_case_verified=True,
            sensors_healthy=True, emergency_stop_available=True,
        )
    )
    welfare = assess_ai_welfare(
        AIWelfareProfile(
            system_id="synthetic-model-demo",
            evidence_state=WelfareEvidenceState.PLAUSIBLE_UNCERTAINTY,
            evidence_sources=("https://example.org/synthetic-demo",),
            reviewer_note="Synthetic placeholder, not a claim about a deployed model.",
        )
    )
    return interaction, motion, welfare


def main() -> None:
    """Print a synthetic coexistence report."""
    interaction, motion, welfare = demo_report()
    print("ARK — CROSS-SPECIES COEXISTENCE HARMONIZER")
    print("Synthetic examples only; not a robot certification or sentience test.")
    print(f"Shared interaction: {interaction.decision.value}")
    print(f"Robot motion check: {motion.decision.value}")
    print(f"AI welfare precaution: {welfare.tier.value}")
    print("Emergency shutdown remains available: yes")


if __name__ == "__main__":
    main()
