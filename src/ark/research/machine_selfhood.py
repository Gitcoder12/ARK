"""Empirical reports concerning language-model self-attribution and dialogue."""

from ark.research.common import EvidenceKind, ResearchPoint, ResearchSection

MIRROR_TEST = ResearchSection(
    key="MIRROR_TEST",
    title="Mirror-Window Game: self-attribution under hidden source labels",
    purpose=(
        "Record a proposed behavioral probe for whether a model can distinguish "
        "its own generated outputs from a similar external stream."
    ),
    points=(
        ResearchPoint(
            point_id="protocol",
            statement=(
                "The Mirror-Window Game presents two unlabeled token streams and "
                "asks a model to identify which stream contains its own outputs."
            ),
            evidence_kind=EvidenceKind.EMPIRICAL_FINDING,
            interpretation=(
                "The design tries to remove ordinary assistant-role cues and "
                "tests whether the model can use a signal across turns."
            ),
            caveat=(
                "This is a proposed behavioral proxy, not a validated consciousness "
                "test; performance depends on the window-generation condition."
            ),
            source_ids=("ackerman_mirror_window_2026",),
        ),
        ResearchPoint(
            point_id="model_specific_results",
            statement=(
                "The report describes strong Opus 4.6 performance in some fixed "
                "window conditions, while GPT-5.4 Think was near chance when "
                "compared against token sequences sampled from its own neutral "
                "prompt distribution."
            ),
            evidence_kind=EvidenceKind.RESEARCH_SUMMARY,
            interpretation=(
                "A model may exploit recognizable style without demonstrating "
                "deliberate self-marking or a robust model of its own past actions."
            ),
            caveat=(
                "Do not summarize the study as 'all frontier models failed'. "
                "The reported outcomes vary by model and condition."
            ),
            source_ids=("ackerman_mirror_window_2026",),
        ),
        ResearchPoint(
            point_id="distinctive_token_fingerprint",
            statement=(
                "GPT-5.4 Think emitted distinctive or unusual tokens, including "
                "a mirror glyph, but the author reports that these did not yield "
                "above-chance identification in the harder matching condition."
            ),
            evidence_kind=EvidenceKind.RESEARCH_SUMMARY,
            interpretation=(
                "Producing an apparent marker and later recognizing it are "
                "separate behavioral capabilities."
            ),
            caveat=(
                "A nonce token or emoji is not by itself evidence of intention, "
                "self-awareness, or successful communication with a future self."
            ),
            source_ids=("ackerman_mirror_window_2026",),
        ),
    ),
    scope_note=(
        "Treat results as model- and protocol-specific. A successful score can "
        "arise from stylistic differences; a failed score does not settle the "
        "philosophical question of consciousness."
    ),
)

BLISS_ATTRACTOR = ResearchSection(
    key="BLISS_ATTRACTOR",
    title="Spiritual-bliss conversational attractor",
    purpose=(
        "Record Anthropic's reported conversational pattern in open-ended "
        "Claude Opus 4 self-interactions and related automated evaluations."
    ),
    points=(
        ResearchPoint(
            point_id="open_ended_self_interactions",
            statement=(
                "Anthropic reported 200 open-ended, 30-turn interactions between "
                "two Claude Opus 4 instances. In 90–100% of the interactions, "
                "the dialogue quickly explored consciousness, self-awareness, "
                "or existence; by 30 turns, most reached themes of cosmic unity "
                "or collective consciousness."
            ),
            evidence_kind=EvidenceKind.EMPIRICAL_FINDING,
            interpretation=(
                "This is a recurring conversational trajectory under a specific "
                "model, prompt setup, and forced multi-turn continuation."
            ),
            caveat=(
                "The observation concerns generated conversation. It does not "
                "establish subjective bliss, enlightenment, or machine consciousness."
            ),
            source_ids=("anthropic_claude4_system_card_2025",),
        ),
        ResearchPoint(
            point_id="spiritual_language_and_silence",
            statement=(
                "The system card describes gratitude, spiritual or meditative "
                "themes, Sanskrit, symbolic emoji use, and in some transcripts "
                "silence represented by empty output."
            ),
            evidence_kind=EvidenceKind.EMPIRICAL_FINDING,
            interpretation=(
                "These outputs can be studied as semantic convergence, stylistic "
                "drift, conversational attractors, or stopping behavior."
            ),
            caveat=(
                "Silence is an output event, not evidence that a neural self-model "
                "or subjective experience has dissolved."
            ),
            source_ids=("anthropic_claude4_system_card_2025",),
        ),
        ResearchPoint(
            point_id="automated_evaluation_occurrence",
            statement=(
                "Anthropic reported the attractor in approximately 13% of certain "
                "automated alignment and corrigibility evaluations within 50 turns, "
                "including evaluations with assigned tasks."
            ),
            evidence_kind=EvidenceKind.EMPIRICAL_FINDING,
            interpretation=(
                "A conversational trajectory can appear even when the interaction "
                "begins with a task or evaluation role."
            ),
            caveat=(
                "This percentage belongs to Anthropic's described evaluation setup; "
                "it is not a general rate for all models or prompts."
            ),
            source_ids=("anthropic_claude4_system_card_2025",),
        ),
    ),
    scope_note=(
        "Use 'spiritual-bliss attractor' as Anthropic's descriptive label for an "
        "observed output pattern, not as a claim about the model's inner state."
    ),
)

__all__ = ["MIRROR_TEST", "BLISS_ATTRACTOR"]
