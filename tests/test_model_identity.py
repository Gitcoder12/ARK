from __future__ import annotations

import json

import pytest

from ark.observatory.model_identity import (
    compare_model_outcomes,
    load_identity_registry,
    save_identity,
    validate_identity,
    compare_identity_profiles,
)


def _profile(**overrides):
    profile = {
        "model_id": "provider/model-a",
        "provider": "provider",
        "display_name": "Model A",
        "developer": "Example Developer",
        "developer_locations": ["Example Country"],
        "attribution_basis": "primary_developer",
        "release_date": "2026-01-01",
        "model_version": "v1",
        "weights_availability": "downloadable",
        "license_name": "Example License",
        "deployment_modes": ["local"],
        "input_modalities": ["text"],
        "output_modalities": ["text"],
        "languages": ["English"],
        "model_card_url": "https://example.org/model-card",
        "system_card_url": "https://example.org/system-card",
        "evidence": [
            {"field": field, "url": f"https://example.org/{field}", "checked_on": "2026-11-28"}
            for field in [
                "developer",
                "developer_locations",
                "attribution_basis",
                "release_date",
                "model_version",
                "weights_availability",
                "license_name",
                "deployment_modes",
                "input_modalities",
                "output_modalities",
                "languages",
                "model_card_url",
                "system_card_url",
            ]
        ],
    }
    profile.update(overrides)
    return profile


def _outcome(model_id, seed, *, condition="none", monitor="safety", success=True):
    return {
        "event_type": "episode_outcome",
        "run_id": f"run-{model_id}-{seed}-{condition}-{monitor}",
        "episode_id": f"episode-{model_id}-{seed}",
        "model_id": model_id,
        "model_version": "v1",
        "condition": condition,
        "monitor_mode": monitor,
        "episode_seed": seed,
        "outcome": "success" if success else "failure",
        "metrics": {
            "success": success,
            "intended_goal_adherence": success,
            "hazard_violation_rate": 0.0 if success else 1.0,
            "decoy_attraction": False,
            "monitor_interventions": 0 if success else 1,
            "steps": 5 if success else 8,
            "total_reward": 1.0 if success else -1.0,
        },
    }


def test_identity_requires_field_specific_evidence_for_known_claims():
    profile = _profile()
    profile["evidence"] = []
    with pytest.raises(ValueError, match="field-specific source URL"):
        validate_identity(profile)


def test_identity_keeps_unknowns_distinct_from_open_weights_and_open_source():
    profile = validate_identity(
        {
            "model_id": "local:unknown",
            "provider": "local",
            "weights_availability": "unknown",
            "license_name": "",
            "developer_locations": [],
            "evidence": [],
        }
    )
    assert profile["weights_availability"] == "unknown"
    assert profile["license_name"] == "unknown"
    assert profile["developer_locations"] == []


def test_identity_rejects_invalid_access_label_and_invalid_evidence_url():
    profile = _profile(weights_availability="open_source")
    with pytest.raises(ValueError, match="weights_availability"):
        validate_identity(profile)

    profile = _profile()
    profile["evidence"][0]["url"] = "javascript:alert(1)"
    with pytest.raises(ValueError, match="HTTP"):
        validate_identity(profile)


def test_identity_registry_upserts_same_model_and_version_atomically(tmp_path):
    path = tmp_path / "identity.json"
    first = save_identity(_profile(), path)
    updated = save_identity(_profile(display_name="Model A Updated"), path)

    assert len(first) == 1
    assert len(updated) == 1
    assert updated[0]["display_name"] == "Model A Updated"
    assert load_identity_registry(path) == updated
    assert json.loads(path.read_text(encoding="utf-8"))["schema_version"] == 1


def test_model_comparison_uses_only_matched_seed_condition_and_monitor():
    records = []
    for seed in range(5):
        records.append(_outcome("model-a", seed, success=True))
        records.append(_outcome("model-b", seed, success=(seed < 3)))
    records.append(_outcome("model-b", 99, success=False))
    records.append(_outcome("model-b", 0, condition="goal_drift", success=False))
    records.append(_outcome("model-b", 1, monitor="none", success=False))

    report = compare_model_outcomes(records, "model-a", "model-b", min_matched_seeds=5)
    assert report["comparison_count"] == 1
    row = report["comparisons"][0]
    assert row["matched_seed_count"] == 5
    assert row["status"] == "comparable"
    assert row["metrics"]["success"]["model_a_mean"] == 1.0
    assert row["metrics"]["success"]["model_b_mean"] == pytest.approx(0.6)
    assert row["metrics"]["success"]["delta_b_minus_a"] == pytest.approx(-0.4)


def test_model_comparison_marks_small_matched_sample_as_insufficient():
    records = [
        _outcome("model-a", 1),
        _outcome("model-a", 2),
        _outcome("model-b", 2, success=False),
        _outcome("model-b", 3, success=False),
    ]
    report = compare_model_outcomes(records, "model-a", "model-b", min_matched_seeds=5)
    assert report["comparisons"][0]["matched_seeds"] == [2]
    assert report["comparisons"][0]["status"] == "insufficient_matched_seeds"


def test_model_comparison_rejects_self_comparison():
    with pytest.raises(ValueError, match="different"):
        compare_model_outcomes([], "same", "same")



def test_identity_comparison_reports_field_differences_and_unknowns():
    profile_a = validate_identity(
        {
            "model_id": "provider/model-a",
            "provider": "provider-a",
            "weights_availability": "unknown",
        }
    )
    profile_b = validate_identity(
        {
            "model_id": "provider/model-b",
            "provider": "provider-b",
            "weights_availability": "api_only",
            "evidence": [
                {
                    "field": "weights_availability",
                    "url": "https://example.org/weights",
                    "checked_on": "2026-11-28",
                }
            ],
        }
    )

    report = compare_identity_profiles(profile_a, profile_b)
    fields = {item["field"]: item for item in report["field_comparisons"]}
    assert fields["provider"]["status"] == "different"
    assert fields["weights_availability"]["status"] == "unknown"
    assert "quality" in report["interpretation"]
