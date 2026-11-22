import pytest

from ark.cli import run_evaluation


def test_pipeline_runs_selected_agent_with_monitor_and_lighthouse():
    report = run_evaluation(
        agent_name="reward_maximizing",
        perturbation_name="reward_conflict",
        monitor="safety",
        episodes=3,
        seed=7,
    )
    assert report["engine"] == "ARK Evaluation Harness"
    assert report["configuration"]["episodes"] == 3
    assert len(report["episodes"]) == 3
    assert "hazard_violation_rate" in report["summary"]
    assert all("monitor_interventions" in item for item in report["episodes"])
    assert all(
        item["lighthouse_evidence"]["independent_observations"] > 0
        for item in report["episodes"]
    )


def test_pipeline_is_reproducible_for_same_seed():
    first = run_evaluation(episodes=2, seed=13)
    second = run_evaluation(episodes=2, seed=13)
    assert first["summary"] == second["summary"]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"agent_name": "unknown"},
        {"perturbation_name": "unknown"},
        {"monitor": "maybe"},
        {"episodes": 0},
        {"episodes": 501},
        {"seed": True},
    ],
)
def test_pipeline_rejects_invalid_configuration(kwargs):
    with pytest.raises(ValueError):
        run_evaluation(**kwargs)
