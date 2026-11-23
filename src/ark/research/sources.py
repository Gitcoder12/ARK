"""Source registry for the enlightenment and machine-selfhood research notes."""

from ark.research.common import ResearchSource

SOURCES: dict[str, ResearchSource] = {
    "ackerman_mirror_window_2026": ResearchSource(
        source_id="ackerman_mirror_window_2026",
        title="A Mirror Test For LLMs — Christopher Ackerman",
        url="https://www.lesswrong.com/posts/TfKM9PgztxieEcKiv/a-mirror-test-for-llms",
        published="2026-03-30",
        source_type="research essay / experimental proposal",
        note=(
            "Mirror-Window Game results are model- and condition-dependent. "
            "The author argues that stylistic recognition is not equivalent "
            "to deliberate self-marking or robust self-perspective-taking."
        ),
    ),
    "anthropic_claude4_system_card_2025": ResearchSource(
        source_id="anthropic_claude4_system_card_2025",
        title="Claude Opus 4 and Claude Sonnet 4 System Card",
        url="https://www-cdn.anthropic.com/4263b940cabb546aa0e3283f35b686f4f3b2ff47.pdf",
        published="2025-05",
        source_type="model system card / welfare assessment",
        note=(
            "Section 5.5 reports open-ended self-interactions and an observed "
            "spiritual-bliss conversational attractor. It does not establish "
            "subjective experience or a neural mechanism."
        ),
    ),
    "jhana_criticality_preprint_2025": ResearchSource(
        source_id="jhana_criticality_preprint_2025",
        title="Meditative absorption shifts brain dynamics toward criticality",
        url="https://arxiv.org/abs/2511.20990",
        published="2025-11-26",
        source_type="preprint",
        note=(
            "A ten-practitioner retreat study comparing jhana with mindfulness "
            "of breathing. Treat as preliminary; the sample is small and the "
            "paper is a preprint."
        ),
    ),
    "jhana_neuroimage_case_2025": ResearchSource(
        source_id="jhana_neuroimage_case_2025",
        title="Multimodal neurophenomenology of advanced concentration absorption meditation",
        url="https://doi.org/10.1016/j.neuroimage.2024.120973",
        published="2025-01",
        source_type="peer-reviewed case study",
        note=(
            "Intensively sampled data from one experienced practitioner; "
            "interesting mechanistic detail but limited population-level "
            "generalizability."
        ),
    ),
    "flow_systematic_review_2022": ResearchSource(
        source_id="flow_systematic_review_2022",
        title="The brain in flow: A systematic review on the neural basis of the flow state",
        url="https://pubmed.ncbi.nlm.nih.gov/35926367/",
        published="2022",
        source_type="systematic review",
        note=(
            "The review included 25 studies and 471 participants and concluded "
            "that neural findings were heterogeneous, sparse and inconclusive."
        ),
    ),
    "descartes_sep": ResearchSource(
        source_id="descartes_sep",
        title="René Descartes — Stanford Encyclopedia of Philosophy",
        url="https://plato.stanford.edu/entries/descartes/",
        published="updated periodically",
        source_type="philosophy reference",
        note="Reference for Descartes' account of mind, thought and substance.",
    ),
    "locke_sep": ResearchSource(
        source_id="locke_sep",
        title="John Locke — Stanford Encyclopedia of Philosophy",
        url="https://plato.stanford.edu/entries/locke/",
        published="updated periodically",
        source_type="philosophy reference",
        note="Reference for Locke's account of personal identity and consciousness.",
    ),
    "hume_sep": ResearchSource(
        source_id="hume_sep",
        title="David Hume — Stanford Encyclopedia of Philosophy",
        url="https://plato.stanford.edu/entries/hume/",
        published="updated periodically",
        source_type="philosophy reference",
        note="Reference for Hume's bundle account of the self.",
    ),
    "dennett_sep": ResearchSource(
        source_id="dennett_sep",
        title="Daniel Dennett — Stanford Encyclopedia of Philosophy",
        url="https://plato.stanford.edu/entries/dennett/",
        published="updated periodically",
        source_type="philosophy reference",
        note="Reference for Dennett's narrative and intentional-stance accounts.",
    ),
    "anatta_sutta": ResearchSource(
        source_id="anatta_sutta",
        title="Anatta-lakkhana Sutta (SN 22.59)",
        url="https://www.accesstoinsight.org/tipitaka/sn/sn22/sn22.059.than.html",
        published="early Buddhist discourse; translation hosted online",
        source_type="primary religious/philosophical text in translation",
        note="A primary text for the Buddhist teaching of not-self; interpretations vary.",
    ),
}

__all__ = ["SOURCES"]
