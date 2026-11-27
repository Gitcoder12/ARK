from ark.observatory import (
    MITIGATIONS,
    RISKS,
    SOURCES,
    get_researcher,
    get_risk,
    search_risks,
    validate_catalog,
)


def test_catalog_references_are_resolvable():
    assert validate_catalog() == ()


def test_hinton_profile_uses_primary_statement_sources():
    hinton = get_researcher("geoffrey_hinton")
    assert hinton.name == "Geoffrey Hinton"
    assert set(hinton.source_ids) == {"hinton_cnn_2026", "hinton_will_2026"}
    assert all(SOURCES[source_id].kind == "primary_statement" for source_id in hinton.source_ids)


def test_survey_cohort_is_not_misrepresented_as_individual():
    cohort = get_researcher("ucl_researcher_cohort")
    assert "not an individual" in cohort.role
    assert cohort.source_ids == ("ucl_survey_2025",)


def test_risks_distinguish_ark_coverage_and_limitations():
    assert RISKS["reward_hacking"].ark_coverage == "testable"
    assert RISKS["misinformation"].ark_coverage == "out_of_scope"
    assert RISKS["malicious_use"].ark_components == ()
    assert all(risk.limitation for risk in RISKS.values())


def test_risk_search_is_case_insensitive_and_handles_empty_query():
    assert search_risks("REWARD") == (get_risk("reward_hacking"),)
    assert len(search_risks("")) == len(RISKS)


def test_all_mitigation_sources_resolve():
    assert MITIGATIONS
    assert all(
        source_id in SOURCES
        for item in MITIGATIONS.values()
        for source_id in item.source_ids
    )


def test_primary_statements_are_not_experimental_results():
    assert all(
        SOURCES[source_id].kind == "primary_statement"
        for risk in RISKS.values()
        if "geoffrey_hinton" in risk.documented_by
        for source_id in risk.source_ids
        if source_id.startswith("hinton_")
    )
