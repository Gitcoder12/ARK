from ark.research.common import ResearchSection
from ark.research.enlightenment import (
    ALL_SECTIONS,
    BLISS_ATTRACTOR,
    MIRROR_TEST,
    OPERATIVE_QUESTION,
    PERFORMANCE_STATE,
    get_section,
    list_sections,
    validate_catalog,
)


def test_catalog_contains_all_requested_research_sections():
    expected = {
        "SPIRITUAL_ALIGNMENT",
        "COGNITIVE_DELEGATION_RISKS",
        "SECOND_ENLIGHTENMENT",
        "SELF_POSITIONS",
        "MIRROR_TEST",
        "BLISS_ATTRACTOR",
        "PERFORMANCE_STATE",
        "OPERATIVE_QUESTION",
    }
    assert set(ALL_SECTIONS) == expected


def test_section_access_is_stable_and_typed():
    assert list_sections() == tuple(ALL_SECTIONS)
    assert get_section("MIRROR_TEST") is MIRROR_TEST
    assert isinstance(get_section("PERFORMANCE_STATE"), ResearchSection)


def test_operative_question_is_a_string():
    assert isinstance(OPERATIVE_QUESTION, str)
    assert OPERATIVE_QUESTION.startswith("What are the conditions")


def test_all_citations_resolve():
    assert validate_catalog() == ()


def test_mirror_test_does_not_claim_all_models_failed():
    text = " ".join(point.caveat for point in MIRROR_TEST.points).lower()
    statements = " ".join(point.statement for point in MIRROR_TEST.points).lower()
    assert "all frontier models failed" not in text
    assert "model- and condition" in MIRROR_TEST.scope_note
    assert "opus 4.6" in statements
    assert "gpt-5.4" in statements


def test_bliss_attractor_is_described_as_output_behavior():
    text = " ".join(
        [BLISS_ATTRACTOR.scope_note]
        + [point.caveat for point in BLISS_ATTRACTOR.points]
    ).lower()
    assert "does not establish subjective" in text
    assert "output pattern" in text


def test_ai_performance_analogy_has_biological_boundary():
    point = next(
        item for item in PERFORMANCE_STATE.points
        if item.point_id == "ai_computational_analogy"
    )
    assert "do not have a biological" in point.caveat
    assert "not samadhi" in point.caveat


def test_every_section_has_a_scope_note():
    for section in ALL_SECTIONS.values():
        if isinstance(section, ResearchSection):
            assert section.scope_note.strip()
            assert section.purpose.strip()
