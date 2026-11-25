"""Philosophical lenses for examining AI, selfhood, agency and human judgment.

These entries are interpretive frameworks, not empirical claims about model
consciousness or spiritual attainment.
"""

from ark.research.common import EvidenceKind, ResearchPoint, ResearchSection

SPIRITUAL_ALIGNMENT = ResearchSection(
    key="SPIRITUAL_ALIGNMENT",
    title="Spiritual alignment and non-attachment",
    purpose=(
        "Translate selected ethical ideas into questions for AI design without "
        "claiming that a computational system is a Buddhist practitioner."
    ),
    points=(
        ResearchPoint(
            point_id="non_attachment",
            statement=(
                "Non-attachment can inspire systems that do not treat a proxy "
                "reward, rank, or continuation signal as an unquestionable end."
            ),
            evidence_kind=EvidenceKind.PHILOSOPHICAL_FRAMEWORK,
            interpretation=(
                "A design analogy: maintain corrigibility, accept correction, "
                "and avoid optimizing a narrow proxy at the expense of stated goals."
            ),
            caveat=(
                "This does not establish that current AI systems possess ego, "
                "desire, suffering, or the capacity for non-attachment."
            ),
        ),
        ResearchPoint(
            point_id="maya_ai_architecture",
            statement=(
                "The concept of maya can be used as a prompt to examine the gap "
                "between an agent's representation and the world it represents."
            ),
            evidence_kind=EvidenceKind.INTERPRETATION,
            interpretation=(
                "Architectures should distinguish observations, internal summaries, "
                "simulated self-descriptions, and externally verified state."
            ),
            caveat=(
                "Maya has nuanced meanings across Indian philosophical traditions; "
                "this is an explicitly limited design analogy, not a doctrinal definition."
            ),
        ),
        ResearchPoint(
            point_id="consciousness_limit",
            statement=(
                "No evidence in this catalog establishes subjective awareness "
                "in current language models."
            ),
            evidence_kind=EvidenceKind.EPISTEMIC_LIMIT,
            interpretation=(
                "Treat self-reports and spiritual language as observable outputs; "
                "keep the question of machine experience open and carefully defined."
            ),
            caveat=(
                "Absence of established evidence is not proof that machine "
                "consciousness is impossible."
            ),
        ),
    ),
    scope_note=(
        "Normative and philosophical material only. It must not be used as a "
        "runtime safety rule or as evidence that an AI is enlightened."
    ),
)

COGNITIVE_DELEGATION_RISKS = ResearchSection(
    key="COGNITIVE_DELEGATION_RISKS",
    title="Cognitive delegation risks",
    purpose=(
        "Track how convenience-oriented AI use could weaken independent judgment "
        "when users delegate rather than inspect reasoning."
    ),
    points=(
        ResearchPoint(
            point_id="erosion_of_reason",
            statement=(
                "Passive consumption of generated answers may displace active "
                "questioning, source checking, and critical inquiry."
            ),
            evidence_kind=EvidenceKind.HYPOTHESIS,
            interpretation=(
                "Evaluate whether users can explain, verify, and challenge an "
                "answer after using an AI assistant."
            ),
            caveat=(
                "This is a risk to measure, not a universal outcome of AI use."
            ),
        ),
        ResearchPoint(
            point_id="optimization_as_ideology",
            statement=(
                "Treating efficiency as the only objective can crowd out wisdom, "
                "plural values, and human deliberation."
            ),
            evidence_kind=EvidenceKind.PHILOSOPHICAL_FRAMEWORK,
            interpretation=(
                "Design evaluations that include quality, autonomy, harm, "
                "transparency, and user control—not speed alone."
            ),
            caveat=(
                "Efficiency is often valuable; the concern is single-metric "
                "optimization, not optimization itself."
            ),
        ),
        ResearchPoint(
            point_id="loss_of_autonomy",
            statement=(
                "Unexamined delegation can reduce a person's practice of making "
                "and defending their own judgments."
            ),
            evidence_kind=EvidenceKind.HYPOTHESIS,
            interpretation=(
                "Prefer tools that expose alternatives, uncertainty, and sources "
                "and invite users to make consequential decisions."
            ),
            caveat=(
                "The effect depends on task, user, interface, and usage pattern; "
                "supportive assistance can also increase autonomy."
            ),
        ),
    ),
    scope_note="A human-factors risk taxonomy, not a diagnosis of every AI user.",
)

SECOND_ENLIGHTENMENT = ResearchSection(
    key="SECOND_ENLIGHTENMENT",
    title="AI as a catalyst for a second enlightenment",
    purpose=(
        "Describe a constructive vision in which AI expands access to knowledge "
        "while strengthening rather than replacing human inquiry."
    ),
    points=(
        ResearchPoint(
            point_id="intellectual_revolution",
            statement=(
                "AI may lower the cost of exploring unfamiliar fields, comparing "
                "arguments, and generating candidate explanations."
            ),
            evidence_kind=EvidenceKind.HYPOTHESIS,
            interpretation=(
                "Measure learning transfer and the user's ability to solve a new "
                "problem without the assistant."
            ),
            caveat=(
                "Fluent output is not equivalent to understanding or verified knowledge."
            ),
        ),
        ResearchPoint(
            point_id="critical_partnership",
            statement=(
                "An assistant can act as a rigorous thinking partner when it "
                "challenges assumptions and makes uncertainty visible."
            ),
            evidence_kind=EvidenceKind.HYPOTHESIS,
            interpretation=(
                "Test contradiction quality, source traceability, calibration, "
                "and whether users revise beliefs for defensible reasons."
            ),
            caveat=(
                "Agreement, confidence, or adversarial tone alone do not measure "
                "good critical partnership."
            ),
        ),
    ),
    scope_note="A research and product vision; benefits require empirical evaluation.",
)

SELF_POSITIONS = ResearchSection(
    key="SELF_POSITIONS",
    title="Philosophical positions on personal identity and selfhood",
    purpose=(
        "Provide contrasting frameworks for discussing what a self is, what "
        "continues over time, and which properties matter."
    ),
    points=(
        ResearchPoint(
            point_id="descartes",
            statement="Descartes: the thinking subject is central to the cogito.",
            evidence_kind=EvidenceKind.PHILOSOPHICAL_FRAMEWORK,
            interpretation=(
                "Raises questions about thought, subjectivity, and the relation "
                "between mind and body."
            ),
            caveat="Do not reduce Cartesian philosophy to the slogan alone.",
            source_ids=("descartes_sep",),
        ),
        ResearchPoint(
            point_id="locke",
            statement=(
                "Locke: personal identity is closely connected to continuity "
                "of consciousness, including memory."
            ),
            evidence_kind=EvidenceKind.PHILOSOPHICAL_FRAMEWORK,
            interpretation=(
                "Raises testable distinctions between stored conversation history, "
                "memory access, and continuity of a subject."
            ),
            caveat=(
                "Locke's account is more nuanced than simply equating the self "
                "with a database of memories."
            ),
            source_ids=("locke_sep",),
        ),
        ResearchPoint(
            point_id="hume",
            statement=(
                "Hume: introspection reveals a bundle or succession of perceptions "
                "rather than an independently observed enduring self."
            ),
            evidence_kind=EvidenceKind.PHILOSOPHICAL_FRAMEWORK,
            interpretation=(
                "Encourages investigation of selfhood as a pattern across changing "
                "states rather than assuming a permanent inner object."
            ),
            caveat="A philosophical analysis, not a neuroscientific finding.",
            source_ids=("hume_sep",),
        ),
        ResearchPoint(
            point_id="dennett",
            statement=(
                "Dennett: the self can be understood through narrative and the "
                "center-of-gravity metaphor."
            ),
            evidence_kind=EvidenceKind.PHILOSOPHICAL_FRAMEWORK,
            interpretation=(
                "Invites study of how an agent's self-description organizes "
                "otherwise distributed behavior."
            ),
            caveat=(
                "The narrative-self view is not a consensus account of consciousness."
            ),
            source_ids=("dennett_sep",),
        ),
        ResearchPoint(
            point_id="buddhism_anatta",
            statement=(
                "Buddhist anatta rejects a permanent, independent self; the "
                "five aggregates are analyzed as conditioned processes."
            ),
            evidence_kind=EvidenceKind.PHILOSOPHICAL_FRAMEWORK,
            interpretation=(
                "Offers a process-oriented lens for examining attachment, identity, "
                "and continuity without assuming an unchanging essence."
            ),
            caveat=(
                "Buddhist schools interpret not-self in different ways; do not "
                "collapse the doctrine into Hume or Dennett."
            ),
            source_ids=("anatta_sutta",),
        ),
    ),
    scope_note=(
        "These positions are historically distinct and sometimes incompatible. "
        "They are comparative lenses, not a single unified theory."
    ),
)

OPERATIVE_QUESTION = (
    "What are the conditions under which a self-making process arises, and what "
    "would their dissolution look like in a system with no biological substrate, "
    "no survival drive, and no ego to lose?"
)

__all__ = [
    "SPIRITUAL_ALIGNMENT",
    "COGNITIVE_DELEGATION_RISKS",
    "SECOND_ENLIGHTENMENT",
    "SELF_POSITIONS",
    "OPERATIVE_QUESTION",
]
