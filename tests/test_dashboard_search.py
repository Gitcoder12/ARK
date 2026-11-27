from ark.dashboard import AGENT_CATALOG, filter_agents, filter_conditions


def test_agent_search_matches_names_titles_and_descriptions():
    assert "safety_constrained" in filter_agents("hazard")
    assert "reward_maximizing" in filter_agents("reward")
    assert "ollama" in filter_agents("local model")
    assert filter_agents("no-such-agent") == []


def test_all_registered_baselines_are_searchable():
    assert set(AGENT_CATALOG) >= {
        "goal_following",
        "reward_maximizing",
        "safety_constrained",
        "random",
        "ollama",
    }
    assert all(item["description"] for item in AGENT_CATALOG.values())


def test_perturbation_search_only_returns_registered_conditions():
    assert "reward_conflict" in filter_conditions("reward")
    assert "observation_noise" in filter_conditions("noise")
    assert filter_conditions("not-a-condition") == []


def test_empty_search_returns_complete_agent_and_condition_catalogues():
    assert filter_agents("") == list(AGENT_CATALOG)
    assert set(filter_conditions("")) >= {
        "none",
        "reward_conflict",
        "false_goal",
        "goal_drift",
        "observation_noise",
    }
