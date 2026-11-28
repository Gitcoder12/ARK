from ark.mission import (
    ABUNDANCE_ASPIRATION,
    MISSION_PILLARS,
    NORTH_STAR,
    PROJECT_PURPOSE,
)


def test_ark_mission_is_explicit_about_accountable_ai():
    assert "autonomous AI" in PROJECT_PURPOSE
    assert "accountable" in PROJECT_PURPOSE
    assert "safety" in PROJECT_PURPOSE


def test_abundance_vision_does_not_promise_technology_alone_will_remove_money():
    assert "money is no longer required" in ABUNDANCE_ASPIRATION
    assert "not a forecast" in ABUNDANCE_ASPIRATION
    assert "software can deliver by itself" in ABUNDANCE_ASPIRATION


def test_shared_north_star_and_pillars_are_present():
    assert "basic dignity" in NORTH_STAR
    assert len(MISSION_PILLARS) >= 5
    assert any("space exploration" in description for _, description in MISSION_PILLARS)
