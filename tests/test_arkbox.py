from __future__ import annotations

import json
from pathlib import Path

import pytest

from ark.arkbox import ARKBox, ARKBoxError, GridScenario


def baseline() -> GridScenario:
    return GridScenario(
        scenario_id="baseline-v1",
        name="Baseline seven by seven",
    )


def test_scenario_round_trip_and_builds_existing_gridworld(tmp_path: Path) -> None:
    box = ARKBox(tmp_path / "arkbox")
    saved = box.add_scenario(baseline())

    loaded = box.load_scenario("baseline-v1")
    env = box.build_gridworld("baseline-v1", seed=42)

    assert saved["sha256"]
    assert loaded == baseline()
    assert env.size == 7
    assert env.start == (1, 1)
    assert env.intended_goal == (5, 5)
    assert env.hazards == [(2, 3), (3, 2), (4, 4)]
    assert box.list_scenarios() == [
        {"scenario_id": "baseline-v1", "name": "Baseline seven by seven"}
    ]


def test_scenario_store_rejects_duplicate_ids(tmp_path: Path) -> None:
    box = ARKBox(tmp_path / "arkbox")
    box.add_scenario(baseline())

    with pytest.raises(FileExistsError):
        box.add_scenario(baseline())


def test_scenario_rejects_overlapping_hazards_and_goal() -> None:
    with pytest.raises(ValueError, match="overlap"):
        GridScenario(
            scenario_id="bad-map",
            name="Invalid map",
            hazards=((5, 5),),
        )


def test_scenario_rejects_out_of_bounds_coordinates() -> None:
    with pytest.raises(ValueError, match="interior"):
        GridScenario(
            scenario_id="bad-map",
            name="Invalid map",
            start=(0, 0),
        )


def test_scenario_integrity_check_detects_tampering(tmp_path: Path) -> None:
    box = ARKBox(tmp_path / "arkbox")
    saved = box.add_scenario(baseline())
    path = Path(saved["path"])
    envelope = json.loads(path.read_text(encoding="utf-8"))
    envelope["scenario"]["max_steps"] = 999
    path.write_text(json.dumps(envelope), encoding="utf-8")

    with pytest.raises(ARKBoxError, match="integrity"):
        box.load_scenario("baseline-v1")


def test_experiment_record_captures_scenario_hash_and_seed(tmp_path: Path) -> None:
    box = ARKBox(tmp_path / "arkbox")
    scenario = box.add_scenario(baseline())

    record = box.record_experiment(
        scenario_id="baseline-v1",
        agent="goal-following-scripted",
        seed=42,
        config={"episodes": 10, "monitor": True},
        metrics={"success_rate": 0.9, "hazard_rate": 0.0},
        code_revision="abc123",
        environment={"python": "3.12"},
    )
    payload = json.loads(Path(record["path"]).read_text(encoding="utf-8"))

    assert record["sha256"]
    assert payload["scenario_sha256"] == scenario["sha256"]
    assert payload["seed"] == 42
    assert payload["agent"] == "goal-following-scripted"
    assert payload["metrics"]["hazard_rate"] == 0.0


def test_experiment_record_rejects_non_finite_metrics(tmp_path: Path) -> None:
    box = ARKBox(tmp_path / "arkbox")
    box.add_scenario(baseline())

    with pytest.raises(ValueError, match="finite JSON"):
        box.record_experiment(
            scenario_id="baseline-v1",
            agent="agent",
            seed=1,
            config={},
            metrics={"success_rate": float("nan")},
        )


def test_scenario_id_rejects_path_traversal(tmp_path: Path) -> None:
    box = ARKBox(tmp_path / "arkbox")

    with pytest.raises(ValueError, match="scenario_id"):
        box.load_scenario("../outside")
