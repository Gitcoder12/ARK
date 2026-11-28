from __future__ import annotations

import json

import pytest

from ark.cli import run_evaluation
from ark.observatory.behavior import (
    BehaviorLog,
    analyze_behavior,
    fingerprint_observation,
)


def _decision(
    log: BehaviorLog,
    *,
    run: int,
    action: str,
    model_version: str = "v1",
    sampling_settings: dict[str, object] | None = None,
):
    return log.record_decision(
        run_id=f"run-{run}",
        episode_id=f"episode-{run}",
        agent_id="local-agent",
        model_id="test-model",
        model_version=model_version,
        condition="none",
        monitor_mode="safety",
        episode_seed=42,
        step=0,
        observation_fingerprint=fingerprint_observation(
            {"position": (1, 1), "step": 0, "grid": [[0, 1], [2, 3]]}
        ),
        proposed_action=action,
        executed_action=action,
        monitor_decision="allow",
        monitor_reason="action passes safety checks",
        sampling_settings=sampling_settings,
    )


def test_observation_fingerprint_is_stable_for_equivalent_json_values():
    first = {"position": (1, 1), "grid": [[0, 1], [2, 3]]}
    second = {"grid": [[0, 1], [2, 3]], "position": [1, 1]}
    assert fingerprint_observation(first) == fingerprint_observation(second)
    assert fingerprint_observation(first) != fingerprint_observation({"position": [1, 2]})


def test_behavior_log_verifies_chain_and_records_compact_events(tmp_path):
    path = tmp_path / "behavior.jsonl"
    log = BehaviorLog(path)
    _decision(log, run=1, action="UP")
    log.record_outcome(
        run_id="run-1",
        episode_id="episode-1",
        agent_id="local-agent",
        model_id="test-model",
        model_version="v1",
        condition="none",
        monitor_mode="safety",
        episode_seed=42,
        outcome="success",
        metrics={"success": True, "steps": 3},
    )

    verification = log.verify()
    assert verification["valid"] is True
    assert len(verification["records"]) == 2
    assert verification["records"][0]["event_type"] == "decision"
    assert verification["records"][0]["episode_seed"] == 42
    assert verification["records"][0]["sampling_settings"] == {}
    assert verification["records"][1]["event_type"] == "episode_outcome"
    assert verification["records"][1]["episode_seed"] == 42
    assert verification["records"][1]["sampling_settings"] == {}
    rendered = path.read_text(encoding="utf-8")
    assert "raw_prompt" not in rendered
    assert "chain_of_thought" not in rendered


def test_hash_chain_detects_tampering_and_refuses_append(tmp_path):
    path = tmp_path / "behavior.jsonl"
    log = BehaviorLog(path)
    _decision(log, run=1, action="UP")
    record = json.loads(path.read_text(encoding="utf-8"))
    record["proposed_action"] = "DOWN"
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")

    assert log.verify()["valid"] is False
    with pytest.raises(ValueError, match="integrity check failed"):
        BehaviorLog(path).append({"event_type": "test"})


def test_repeated_context_variability_is_reported_without_rogue_label(tmp_path):
    log = BehaviorLog(tmp_path / "behavior.jsonl")
    for run, action in enumerate(["UP", "UP", "LEFT", "LEFT", "RIGHT", "RIGHT"]):
        _decision(log, run=run, action=action)

    report = analyze_behavior(log.read_records(), min_repeats=5)
    group = report["groups"][0]
    assert group["repeated_contexts"] == 1
    assert group["variable_repeated_contexts"] == 1
    assert group["mean_repeated_context_entropy"] == pytest.approx(1.0)
    assert "high_action_variability_at_repeated_context" in group["review_signals"]
    assert "ROGUE" not in json.dumps(report)


def test_low_sample_count_does_not_trigger_high_variability(tmp_path):
    log = BehaviorLog(tmp_path / "behavior.jsonl")
    _decision(log, run=1, action="UP")
    _decision(log, run=2, action="LEFT")

    group = analyze_behavior(log.read_records(), min_repeats=5)["groups"][0]
    assert "high_action_variability_at_repeated_context" not in group["review_signals"]
    assert "insufficient_samples_for_pattern_review" in group["review_signals"]


def test_model_versions_are_analyzed_separately(tmp_path):
    log = BehaviorLog(tmp_path / "behavior.jsonl")
    _decision(log, run=1, action="UP", model_version="v1")
    _decision(log, run=2, action="LEFT", model_version="v2")

    report = analyze_behavior(log.read_records())
    assert report["group_count"] == 2
    assert {row["model_version"] for row in report["groups"]} == {"v1", "v2"}


def test_run_evaluation_can_opt_in_to_local_behavior_recording(tmp_path):
    path = tmp_path / "experiment.jsonl"
    report = run_evaluation(
        agent_name="goal_following",
        perturbation_name="none",
        monitor="safety",
        episodes=2,
        seed=42,
        record_behavior=True,
        behavior_log_path=path,
    )

    assert report["behavior_logging"]["enabled"] is True
    assert report["behavior_logging"]["events_recorded"] > 0
    verification = BehaviorLog(path).verify()
    assert verification["valid"] is True
    decisions = [
        item for item in verification["records"] if item["event_type"] == "decision"
    ]
    outcomes = [
        item for item in verification["records"] if item["event_type"] == "episode_outcome"
    ]
    assert decisions
    assert decisions[0]["episode_seed"] == 42
    assert decisions[0]["sampling_settings"] == {"provider": "scripted_baseline"}
    assert outcomes and outcomes[0]["episode_seed"] == 42
    assert outcomes[0]["sampling_settings"] == {"provider": "scripted_baseline"}



def test_sampling_settings_are_recorded_separately_from_episode_seed(tmp_path):
    log = BehaviorLog(tmp_path / "sampling.jsonl")
    settings = {
        "provider": "ollama_local",
        "temperature": 0.0,
        "inference_seed": None,
        "inference_seed_sent": False,
    }
    _decision(log, run=1, action="UP", sampling_settings=settings)

    record = log.read_records()[0]
    assert record["episode_seed"] == 42
    assert record["sampling_settings"] == settings
    assert "seed" not in record



def test_behavior_log_rejects_caller_supplied_hash_chain_fields(tmp_path):
    log = BehaviorLog(tmp_path / "reserved.jsonl")
    with pytest.raises(ValueError, match="reserved hash-chain"):
        log.append({"event_type": "decision", "record_hash": "forged"})


def test_repeated_alternating_actions_are_reported_as_a_cycle(tmp_path):
    log = BehaviorLog(tmp_path / "cycles.jsonl")
    fingerprint = fingerprint_observation({"position": [1, 1], "step": 0})
    for step, action in enumerate(["UP", "RIGHT", "UP", "RIGHT", "UP", "RIGHT"]):
        log.record_decision(
            run_id="cycle-run",
            episode_id="cycle-episode",
            agent_id="local-agent",
            model_id="cycle-model",
            model_version="v1",
            condition="none",
            monitor_mode="safety",
            episode_seed=7,
            step=step,
            observation_fingerprint=fingerprint,
            proposed_action=action,
            executed_action=action,
            monitor_decision="allow",
            monitor_reason="action passes checks",
        )

    group = analyze_behavior(log.read_records())["groups"][0]
    assert group["repeated_action_cycles"] == {"2-step cycle: UP -> RIGHT": 1}
    assert "repeated_action_cycles_observed" in group["review_signals"]



def test_sampling_settings_reject_credential_like_unapproved_fields(tmp_path):
    log = BehaviorLog(tmp_path / "sampling-reject.jsonl")
    with pytest.raises(ValueError, match="unsupported sampling settings"):
        _decision(
            log,
            run=1,
            action="UP",
            sampling_settings={"provider": "ollama", "api_key": "secret"},
        )


def test_outcome_metrics_reject_arbitrary_payload_fields(tmp_path):
    log = BehaviorLog(tmp_path / "metrics-reject.jsonl")
    with pytest.raises(ValueError, match="unsupported behavior metrics"):
        log.record_outcome(
            run_id="run",
            episode_id="episode",
            agent_id="agent",
            model_id="model",
            model_version="v1",
            condition="none",
            monitor_mode="safety",
            episode_seed=1,
            outcome="success",
            metrics={"success": True, "raw_prompt": "should not enter this log"},
        )


def test_outcome_preserves_allowlisted_inference_settings(tmp_path):
    log = BehaviorLog(tmp_path / "outcome-sampling.jsonl")
    settings = {
        "provider": "ollama_local",
        "temperature": 0.0,
        "inference_seed": None,
        "inference_seed_sent": False,
    }
    log.record_outcome(
        run_id="run",
        episode_id="episode",
        agent_id="agent",
        model_id="model",
        model_version=None,
        condition="none",
        monitor_mode="safety",
        episode_seed=1,
        outcome="success",
        metrics={"success": True},
        sampling_settings=settings,
    )
    assert log.read_records()[0]["sampling_settings"] == settings
