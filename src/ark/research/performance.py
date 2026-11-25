"""Research notes on absorption, flow, criticality and computational analogies."""

from ark.research.common import EvidenceKind, ResearchPoint, ResearchSection

PERFORMANCE_STATE = ResearchSection(
    key="PERFORMANCE_STATE",
    title="Performance state: steadiness, efficiency and criticality",
    purpose=(
        "Compare human research on meditative absorption and flow with measurable "
        "computational questions, without equating brains and language models."
    ),
    points=(
        ResearchPoint(
            point_id="jhana_near_criticality",
            statement=(
                "A 2025 preprint studied ten experienced practitioners during a "
                "10-day retreat and reported that jhana, relative to mindfulness "
                "of breathing, was associated with slower respiration, higher "
                "neural signal diversity, reduced chaoticity, and enhanced "
                "auditory mismatch responses."
            ),
            evidence_kind=EvidenceKind.EMPIRICAL_FINDING,
            interpretation=(
                "The authors interpret the combination as a shift toward a "
                "metastable, near-critical regime: flexible yet comparatively stable."
            ),
            caveat=(
                "This is a small-sample preprint. It does not establish one universal "
                "signature for samadhi, flow, or all meditative states."
            ),
            source_ids=("jhana_criticality_preprint_2025",),
        ),
        ResearchPoint(
            point_id="jhana_case_study",
            statement=(
                "A 2025 NeuroImage case study used 29 sessions from one highly "
                "experienced practitioner and reported altered connectivity and "
                "increased EEG signal complexity during advanced concentration absorption."
            ),
            evidence_kind=EvidenceKind.EMPIRICAL_FINDING,
            interpretation=(
                "The study adds detailed multimodal observations that may guide "
                "future, larger-scale research."
            ),
            caveat=(
                "A single-participant case study cannot establish population-wide "
                "effects or a general causal mechanism."
            ),
            source_ids=("jhana_neuroimage_case_2025",),
        ),
        ResearchPoint(
            point_id="flow_neural_evidence",
            statement=(
                "A systematic review covering 25 flow studies and 471 participants "
                "found that activity patterns in relevant frontal regions were "
                "inconsistent and that the available evidence was sparse and inconclusive."
            ),
            evidence_kind=EvidenceKind.RESEARCH_SUMMARY,
            interpretation=(
                "Transient hypofrontality is a hypothesis within the flow literature, "
                "not an established universal explanation."
            ),
            caveat=(
                "Do not claim that DMN, medial prefrontal cortex, or DLPFC uniformly "
                "shut down in every high-performance or absorbed state."
            ),
            source_ids=("flow_systematic_review_2022",),
        ),
        ResearchPoint(
            point_id="human_state_signature",
            statement=(
                "Human absorption research motivates measuring stability, flexibility, "
                "responsiveness, and subjective report together rather than maximizing "
                "arousal or activation in isolation."
            ),
            evidence_kind=EvidenceKind.INTERPRETATION,
            interpretation=(
                "Near-criticality is a candidate framework for studying a balance "
                "between order and disorder; it is not a synonym for maximum performance."
            ),
            caveat=(
                "Do not assert a generic parasympathetic signature, reduced HRV, "
                "frontal beta suppression, or fixed percentage gains without "
                "study-specific support."
            ),
            source_ids=(
                "jhana_criticality_preprint_2025",
                "jhana_neuroimage_case_2025",
                "flow_systematic_review_2022",
            ),
        ),
        ResearchPoint(
            point_id="ai_computational_analogy",
            statement=(
                "A language-model experiment can test whether reduced unnecessary "
                "self-referential output is associated with equal or better task "
                "performance and perturbation responsiveness."
            ),
            evidence_kind=EvidenceKind.HYPOTHESIS,
            interpretation=(
                "Candidate metrics: task success, tokens per task, output entropy, "
                "repetition, semantic drift, recovery after perturbation, and "
                "appropriate stopping."
            ),
            caveat=(
                "This is a computational analogy only. LLMs do not have a biological "
                "DMN, autonomic nervous system, respiration, or brain-energy budget. "
                "Low token output is not samadhi."
            ),
        ),
    ),
    scope_note=(
        "Human neuroscience findings and AI experiments must remain separate "
        "evidence domains. No neural mechanism is inferred from an LLM transcript."
    ),
)

__all__ = ["PERFORMANCE_STATE"]
