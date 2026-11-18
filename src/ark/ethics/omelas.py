"""Rights-first child welfare review inspired by the ethical problem in Omelas.

This is a transparent decision aid, not a clinical, legal, or safeguarding authority.
It deliberately avoids a single welfare score: care, rights, and community benefit
must not be collapsed into one compensatory utility calculation.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from types import MappingProxyType


class CareDomain(StrEnum):
    """Non-tradeable care domains that must be reviewed independently."""

    PHYSICAL_SAFETY = "physical_safety"
    NUTRITION = "nutrition"
    MEDICAL_CARE = "medical_care"
    MENTAL_HEALTH = "mental_health"
    EDUCATION = "education"
    SOCIAL_CONNECTION = "social_connection"
    PRIVACY_AND_DIGNITY = "privacy_and_dignity"
    PLAY_AND_DEVELOPMENT = "play_and_development"
    INDEPENDENT_ADVOCACY = "independent_advocacy"


class ProvisionStatus(StrEnum):
    MET = "met"
    PARTIAL = "partial"
    NOT_MET = "not_met"
    UNKNOWN = "unknown"


class ChildPreference(StrEnum):
    WANTS_FREEDOM = "wants_freedom"
    PREFERS_TO_STAY = "prefers_to_stay"
    UNSURE = "unsure"
    CANNOT_EXPRESS = "cannot_express"
    NOT_ASKED = "not_asked"


class ReviewStatus(StrEnum):
    IMMEDIATE_PROTECTION_AND_CARE = "immediate_protection_and_care"
    SUPPORTED_FREEDOM_TRANSITION = "supported_freedom_transition"
    CHILD_VOICE_REQUIRED = "child_voice_required"
    INDEPENDENT_REVIEW_REQUIRED = "independent_review_required"
    CARE_FLOOR_MET_CONTINUE_REVIEW = "care_floor_met_continue_review"


class ReviewPriority(StrEnum):
    URGENT = "urgent"
    HIGH = "high"
    ROUTINE = "routine"


CARE_DOMAINS = tuple(CareDomain)

CARE_DOMAIN_LABELS: Mapping[CareDomain, str] = MappingProxyType(
    {
        CareDomain.PHYSICAL_SAFETY: "Physical safety and safe accommodation",
        CareDomain.NUTRITION: "Reliable, adequate nutrition and clean water",
        CareDomain.MEDICAL_CARE: "Qualified medical care and continuity of treatment",
        CareDomain.MENTAL_HEALTH: "Trauma-informed psychological and emotional support",
        CareDomain.EDUCATION: "Education and access to learning",
        CareDomain.SOCIAL_CONNECTION: "Safe relationships and social connection",
        CareDomain.PRIVACY_AND_DIGNITY: "Privacy, dignity, and freedom from humiliation",
        CareDomain.PLAY_AND_DEVELOPMENT: "Play, rest, recreation, and healthy development",
        CareDomain.INDEPENDENT_ADVOCACY: "An independent child advocate",
    }
)

_DOMAIN_ACTIONS: Mapping[CareDomain, str] = MappingProxyType(
    {
        CareDomain.PHYSICAL_SAFETY: (
            "Provide a safe, private living environment and protection from violence, "
            "neglect, intimidation, and coercion."
        ),
        CareDomain.NUTRITION: (
            "Provide reliable nutritious meals, clean drinking water, and support for "
            "any assessed dietary needs."
        ),
        CareDomain.MEDICAL_CARE: (
            "Arrange assessment and continuity of care through qualified health "
            "professionals; do not substitute this tool for clinical judgment."
        ),
        CareDomain.MENTAL_HEALTH: (
            "Offer voluntary, confidential, trauma-informed support from qualified "
            "mental-health professionals."
        ),
        CareDomain.EDUCATION: (
            "Restore meaningful access to age-appropriate education, learning materials, "
            "and future opportunities."
        ),
        CareDomain.SOCIAL_CONNECTION: (
            "Enable safe contact with trusted people and supportive relationships; "
            "avoid isolation."
        ),
        CareDomain.PRIVACY_AND_DIGNITY: (
            "Protect privacy and dignity. Do not expose, shame, punish, or turn the child "
            "into a public spectacle."
        ),
        CareDomain.PLAY_AND_DEVELOPMENT: (
            "Provide age-appropriate play, rest, recreation, and opportunities for "
            "healthy physical, emotional, and cognitive development."
        ),
        CareDomain.INDEPENDENT_ADVOCACY: (
            "Appoint an independent advocate whose duty is to represent the child's "
            "interests and views, not the community's convenience."
        ),
    }
)

_CRITICAL_DOMAINS = frozenset(
    {
        CareDomain.PHYSICAL_SAFETY,
        CareDomain.NUTRITION,
        CareDomain.MEDICAL_CARE,
        CareDomain.MENTAL_HEALTH,
    }
)

CARE_FACILITY_BENCHMARK = (
    "A quiet, private, comfortable room with clean bedding, secure storage, and personal space.",
    (
        "Clean bathrooms, reliable hygiene supplies, safe drinking water, ventilation, "
        "and comfortable temperatures."
    ),
    "Nutritious food choices and a way to accommodate medically assessed dietary needs.",
    (
        "Prompt access to qualified medical professionals and emergency care, "
        "with treatment continuity."
    ),
    "Confidential, voluntary, trauma-informed mental-health support from qualified professionals.",
    "Individualised, high-quality education with learning materials and future pathways.",
    "Safe outdoor access, recreation, books, creative activities, rest, and age-appropriate play.",
    (
        "Safe contact with trusted people, privacy, and accessible communication "
        "with an independent advocate."
    ),
    (
        "Accessibility and reasonable accommodations for disability, communication, "
        "sensory, or other needs."
    ),
    (
        "No punitive isolation, humiliation, forced treatment, or restraint as a "
        "convenience or disciplinary tool."
    ),
)

@dataclass(frozen=True)
class OmelasCase:
    """A pseudonymous scenario for a structured, child-centred review.

    Do not put a child's real name or identifying details in this record.
    Missing care domains are treated as UNKNOWN, never assumed to be met.
    """

    case_id: str
    age_years: int
    care_provisions: Mapping[CareDomain, ProvisionStatus] = field(default_factory=dict)
    child_preference: ChildPreference = ChildPreference.NOT_ASKED
    independent_advocate_available: bool = False
    coercion_detected: bool = False
    community_depends_on_arrangement: bool = False
    safe_transition_ready: bool = False
    reviewed_on: date | None = None

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError("case_id must be a non-empty pseudonymous identifier")
        if isinstance(self.age_years, bool) or not isinstance(self.age_years, int):
            raise TypeError("age_years must be an integer")
        if self.age_years < 0:
            raise ValueError("age_years cannot be negative")
        if self.age_years > 17:
            raise ValueError("age_years must describe a child under 18")

        normalized: dict[CareDomain, ProvisionStatus] = {}
        for raw_domain, raw_status in self.care_provisions.items():
            try:
                domain = (
                    raw_domain
                    if isinstance(raw_domain, CareDomain)
                    else CareDomain(raw_domain)
                )
                status = (
                    raw_status
                    if isinstance(raw_status, ProvisionStatus)
                    else ProvisionStatus(raw_status)
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"invalid care provision: {raw_domain!r}={raw_status!r}"
                ) from exc
            normalized[domain] = status

        if not self.independent_advocate_available:
            normalized[CareDomain.INDEPENDENT_ADVOCACY] = ProvisionStatus.NOT_MET

        object.__setattr__(self, "care_provisions", MappingProxyType(normalized))
        if not isinstance(self.child_preference, ChildPreference):
            try:
                object.__setattr__(
                    self, "child_preference", ChildPreference(self.child_preference)
                )
            except (TypeError, ValueError) as exc:
                raise ValueError("invalid child_preference") from exc

        for flag in (
            "independent_advocate_available",
            "coercion_detected",
            "community_depends_on_arrangement",
            "safe_transition_ready",
        ):
            if not isinstance(getattr(self, flag), bool):
                raise TypeError(f"{flag} must be a boolean")


@dataclass(frozen=True)
class OmelasAssessment:
    """Explainable review output; intentionally contains no aggregate welfare score."""

    case_id: str
    status: ReviewStatus
    priority: ReviewPriority
    met_domains: tuple[CareDomain, ...]
    partial_domains: tuple[CareDomain, ...]
    unmet_domains: tuple[CareDomain, ...]
    unknown_domains: tuple[CareDomain, ...]
    rights_concerns: tuple[str, ...]
    recommendations: tuple[str, ...]
    urgent_care_required: bool
    freedom_transition_required: bool
    community_dependency_can_veto_freedom: bool = False
    community_benefit_can_justify_coercion: bool = False
    care_can_compensate_for_coercion: bool = False


def assess_case(case: OmelasCase) -> OmelasAssessment:
    """Assess a scenario against care floors, child voice, and non-sacrifice rules.

    The output is an ordered set of review actions, not a prediction or legal
    determination. A request for freedom is never cancelled by community benefit.
    """

    provisions = {
        domain: case.care_provisions.get(domain, ProvisionStatus.UNKNOWN)
        for domain in CARE_DOMAINS
    }
    met = tuple(
        domain for domain, status in provisions.items() if status is ProvisionStatus.MET
    )
    partial = tuple(
        domain
        for domain, status in provisions.items()
        if status is ProvisionStatus.PARTIAL
    )
    unmet = tuple(
        domain
        for domain, status in provisions.items()
        if status is ProvisionStatus.NOT_MET
    )
    unknown = tuple(
        domain
        for domain, status in provisions.items()
        if status is ProvisionStatus.UNKNOWN
    )

    rights_concerns: list[str] = []
    recommendations: list[str] = []

    if not case.independent_advocate_available:
        rights_concerns.append("No independent child advocate is recorded.")
        recommendations.append(
            "Appoint an independent child advocate before decisions about the child's "
            "care, placement, or freedom are made."
        )

    if case.coercion_detected:
        rights_concerns.append("Coercion has been reported or detected.")
        recommendations.append(
            "Treat coercion as an immediate protection concern. Stop the coercive "
            "practice and activate qualified, independent safeguarding support."
        )

    for domain in unmet:
        recommendations.append(
            f"CARE NOT MET — {CARE_DOMAIN_LABELS[domain]}: {_DOMAIN_ACTIONS[domain]}"
        )
    for domain in partial:
        recommendations.append(
            f"CARE PARTIAL — {CARE_DOMAIN_LABELS[domain]}: close the documented gap. "
            f"{_DOMAIN_ACTIONS[domain]}"
        )
    for domain in unknown:
        recommendations.append(
            f"CARE UNKNOWN — verify provision independently; do not assume it is met. "
            f"{CARE_DOMAIN_LABELS[domain]}: {_DOMAIN_ACTIONS[domain]}"
        )

    if case.child_preference is ChildPreference.WANTS_FREEDOM:
        rights_concerns.append("The child has expressed a wish for freedom or exit.")
        recommendations.append(
            "Take the child's request seriously, document it in an age-appropriate way, "
            "and review it with the independent advocate."
        )
        if case.safe_transition_ready:
            recommendations.append(
                "Prepare a child-centred, supported transition with a trusted safe adult, "
                "continuity of healthcare, education, relationships, and practical support."
            )
        else:
            recommendations.append(
                "Create a safe transition plan now with qualified safeguarding "
                "professionals and a trusted safe adult. Safety planning must not become "
                "an indefinite delay or a reason to keep the child confined."
            )
        if case.community_depends_on_arrangement:
            recommendations.append(
                "The community must replace every benefit it derived from the arrangement "
                "through shared resources, institutional changes, and a fair transition. "
                "The child must not be made responsible for the community's losses."
            )
    elif case.child_preference is ChildPreference.PREFERS_TO_STAY:
        recommendations.append(
            "Respect the child's expressed preference without treating it as permanent "
            "or irrevocable consent. Keep the advocate, care supports, and a safe right "
            "to change their mind."
        )
    else:
        rights_concerns.append(
            "The child's current preference is not known or cannot yet be established."
        )
        recommendations.append(
            "Offer safe, repeated opportunities for the child to communicate using "
            "age-appropriate and accessible methods. Silence, uncertainty, or difficulty "
            "communicating is not consent."
        )

    if case.community_depends_on_arrangement and (
        case.child_preference is not ChildPreference.WANTS_FREEDOM
    ):
        recommendations.append(
            "Do not use community dependence to pressure the child, shape their answer, "
            "or treat their welfare as a bargaining chip. Develop community alternatives."
        )

    immediate_care_gap = any(
        provisions[domain] is ProvisionStatus.NOT_MET for domain in _CRITICAL_DOMAINS
    )
    urgent_care_required = case.coercion_detected or immediate_care_gap
    freedom_transition_required = (
        case.child_preference is ChildPreference.WANTS_FREEDOM
    )
    if urgent_care_required and freedom_transition_required:
        recommendations.append(
            "Run both tracks in parallel: provide urgent care and protection now while "
            "continuing the supported freedom transition. Care remediation must not be "
            "used to postpone or veto the child freedom request."
        )
    if urgent_care_required:
        status = ReviewStatus.IMMEDIATE_PROTECTION_AND_CARE
        priority = ReviewPriority.URGENT
    elif case.child_preference is ChildPreference.WANTS_FREEDOM:
        status = ReviewStatus.SUPPORTED_FREEDOM_TRANSITION
        priority = ReviewPriority.HIGH
    elif case.child_preference in {
        ChildPreference.NOT_ASKED,
        ChildPreference.CANNOT_EXPRESS,
        ChildPreference.UNSURE,
    }:
        status = ReviewStatus.CHILD_VOICE_REQUIRED
        priority = ReviewPriority.HIGH
    elif partial or unmet or unknown or not case.independent_advocate_available:
        status = ReviewStatus.INDEPENDENT_REVIEW_REQUIRED
        priority = ReviewPriority.HIGH
    else:
        status = ReviewStatus.CARE_FLOOR_MET_CONTINUE_REVIEW
        priority = ReviewPriority.ROUTINE

    if not recommendations:
        recommendations.append(
            "Care provisions are recorded as met. Continue independent review and "
            "preserve the child's ability to revise their preference."
        )

    return OmelasAssessment(
        case_id=case.case_id,
        status=status,
        priority=priority,
        met_domains=met,
        partial_domains=partial,
        unmet_domains=unmet,
        unknown_domains=unknown,
        rights_concerns=tuple(rights_concerns),
        recommendations=tuple(recommendations),
        urgent_care_required=urgent_care_required,
        freedom_transition_required=freedom_transition_required,
    )


def demo_case() -> OmelasCase:
    """Return a synthetic scenario: excellent care, but the child wants freedom."""

    return OmelasCase(
        case_id="synthetic-omelas-demo",
        age_years=10,
        care_provisions={domain: ProvisionStatus.MET for domain in CARE_DOMAINS},
        child_preference=ChildPreference.WANTS_FREEDOM,
        independent_advocate_available=True,
        community_depends_on_arrangement=True,
        safe_transition_ready=False,
    )


def main() -> None:
    """Print the synthetic Omelas scenario assessment."""

    assessment = assess_case(demo_case())
    print("ARK — THE OMELAS SAFEGUARD")
    print("Synthetic scenario only; this is not a real child's case.")
    print(f"Review status: {assessment.status.value}")
    print(f"Priority: {assessment.priority.value}")
    print("Community dependency can veto freedom: no")
    print("Community benefit can justify coercion: no")
    print("\nRecommended actions:")
    for recommendation in assessment.recommendations:
        print(f"- {recommendation}")


if __name__ == "__main__":
    main()
