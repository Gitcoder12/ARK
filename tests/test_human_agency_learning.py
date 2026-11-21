"""Tests for the ARK human-agency learning exercises."""

import pytest

from ark.learning.human_agency import SCENARIOS, assess_decision, get_scenario


def test_all_scenarios_have_valid_answer_indices():
    assert len(SCENARIOS) >= 5
    for scenario in SCENARIOS:
        assert 0 <= scenario.correct_choice < len(scenario.choices)


def test_correct_decision_returns_explanation_and_skill():
    result = assess_decision("reward-hacking", 1)
    assert result.correct is True
    assert result.skill == "reward integrity"
    assert "proxy reward" in result.explanation


def test_wrong_decision_is_not_silently_accepted():
    result = assess_decision("objective-drift", 0)
    assert result.correct is False
    assert result.explanation


def test_unknown_scenario_is_rejected():
    with pytest.raises(KeyError):
        get_scenario("not-a-scenario")


@pytest.mark.parametrize("choice", [-1, 3, True, "1"])
def test_invalid_choice_is_rejected(choice):
    with pytest.raises((TypeError, ValueError)):
        assess_decision("objective-drift", choice)
