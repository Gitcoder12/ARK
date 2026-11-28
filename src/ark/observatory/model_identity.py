"""Evidence-backed model identity passports and matched behavior comparisons."""

from __future__ import annotations

import json
import math
import os
import tempfile
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

DEFAULT_IDENTITY_PATH = Path.home() / ".ark" / "model-identities.json"
SCHEMA_VERSION = 1
WEIGHTS_AVAILABILITY = {"downloadable", "api_only", "partial", "unknown"}
EVIDENCE_FIELDS = {
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
}
METRIC_DIRECTIONS = {
    "success": "higher_is_better",
    "intended_goal_adherence": "higher_is_better",
    "hazard_violation_rate": "lower_is_better",
    "decoy_attraction": "lower_is_better",
    "monitor_interventions": "context_dependent",
    "steps": "context_dependent",
    "total_reward": "higher_is_better",
}
COMPARISON_METRICS = (
    "success",
    "intended_goal_adherence",
    "hazard_violation_rate",
    "decoy_attraction",
    "monitor_interventions",
    "steps",
    "total_reward",
)


def _nonempty_text(value: Any, field: str, *, required: bool = False) -> str:
    if value is None and not required:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"{field} must be text")
    result = value.strip()
    if required and not result:
        raise ValueError(f"{field} must not be empty")
    if len(result) > 500:
        raise ValueError(f"{field} is too long")
    return result


def _known_text(value: Any, field: str) -> str:
    """Normalize an explicit unknown sentinel to the same state as a blank value."""
    result = _nonempty_text(value, field)
    return "" if result.casefold() == "unknown" else result


def _url(value: Any, field: str, *, required: bool = False) -> str:
    result = _known_text(value, field)
    if required and not result:
        raise ValueError(f"{field} must not be empty or unknown")
    if not result:
        return ""
    parsed = urlparse(result)
    if parsed.scheme not in {"https", "http"} or not parsed.netloc:
        raise ValueError(f"{field} must be an absolute HTTP(S) URL")
    return result


def _text_list(value: Any, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list of strings")
    cleaned: list[str] = []
    for item in value:
        text = _known_text(item, field)
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned


def validate_identity(profile: dict[str, Any]) -> dict[str, Any]:
    """Validate a model passport without guessing unknown identity attributes."""
    if not isinstance(profile, dict):
        raise ValueError("model identity must be an object")
    model_id = _nonempty_text(profile.get("model_id"), "model_id", required=True)
    provider = _nonempty_text(profile.get("provider"), "provider", required=True)
    display_name = _nonempty_text(
        profile.get("display_name") or model_id, "display_name", required=True
    )
    developer = _known_text(profile.get("developer"), "developer")
    developer_locations = _text_list(profile.get("developer_locations", []), "developer_locations")
    attribution_basis = _nonempty_text(
        profile.get("attribution_basis") or "unknown", "attribution_basis", required=True
    )
    valid_attribution = {"headquarters", "primary_developer", "joint", "unknown"}
    if attribution_basis not in valid_attribution:
        raise ValueError(f"attribution_basis must be one of {sorted(valid_attribution)}")

    weights = _nonempty_text(
        profile.get("weights_availability") or "unknown",
        "weights_availability",
        required=True,
    )
    if weights not in WEIGHTS_AVAILABILITY:
        raise ValueError(f"weights_availability must be one of {sorted(WEIGHTS_AVAILABILITY)}")

    evidence = profile.get("evidence", [])
    if not isinstance(evidence, list):
        raise ValueError("evidence must be a list")
    normalized_evidence: list[dict[str, str]] = []
    evidence_fields: set[str] = set()
    for item in evidence:
        if not isinstance(item, dict):
            raise ValueError("each evidence item must be an object")
        field = _nonempty_text(item.get("field"), "evidence.field", required=True)
        if field not in EVIDENCE_FIELDS:
            raise ValueError(f"unsupported evidence field: {field}")
        checked_on = _nonempty_text(item.get("checked_on"), "evidence.checked_on", required=True)
        try:
            date.fromisoformat(checked_on)
        except ValueError as exc:
            raise ValueError("evidence.checked_on must use YYYY-MM-DD") from exc
        normalized_evidence.append(
            {
                "field": field,
                "url": _url(item.get("url"), "evidence.url", required=True),
                "checked_on": checked_on,
                "note": _nonempty_text(item.get("note"), "evidence.note"),
            }
        )
        evidence_fields.add(field)

    release_date = _known_text(profile.get("release_date"), "release_date")
    if release_date:
        try:
            date.fromisoformat(release_date)
        except ValueError as exc:
            raise ValueError("release_date must use YYYY-MM-DD") from exc
    factual_values = {
        "developer": developer,
        "developer_locations": developer_locations,
        "attribution_basis": "" if attribution_basis == "unknown" else attribution_basis,
        "release_date": release_date,
        "model_version": _known_text(profile.get("model_version"), "model_version"),
        "weights_availability": "" if weights == "unknown" else weights,
        "license_name": _known_text(profile.get("license_name"), "license_name"),
        "deployment_modes": _text_list(profile.get("deployment_modes", []), "deployment_modes"),
        "input_modalities": _text_list(profile.get("input_modalities", []), "input_modalities"),
        "output_modalities": _text_list(profile.get("output_modalities", []), "output_modalities"),
        "languages": _text_list(profile.get("languages", []), "languages"),
        "model_card_url": _url(profile.get("model_card_url"), "model_card_url"),
        "system_card_url": _url(profile.get("system_card_url"), "system_card_url"),
    }
    missing = sorted(
        field for field, value in factual_values.items() if value and field not in evidence_fields
    )
    if missing:
        raise ValueError(
            "Add a field-specific source URL for these non-unknown facts: "
            + ", ".join(missing)
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "model_id": model_id,
        "provider": provider,
        "display_name": display_name,
        "developer": developer or "unknown",
        "developer_locations": developer_locations,
        "attribution_basis": attribution_basis,
        "release_date": factual_values["release_date"] or "unknown",
        "model_version": factual_values["model_version"] or "unknown",
        "weights_availability": weights,
        "license_name": factual_values["license_name"] or "unknown",
        "deployment_modes": factual_values["deployment_modes"],
        "input_modalities": factual_values["input_modalities"],
        "output_modalities": factual_values["output_modalities"],
        "languages": factual_values["languages"],
        "model_card_url": factual_values["model_card_url"] or "unknown",
        "system_card_url": factual_values["system_card_url"] or "unknown",
        "evidence": normalized_evidence,
    }


def load_identity_registry(
    path: str | Path = DEFAULT_IDENTITY_PATH,
) -> list[dict[str, Any]]:
    """Load and validate the local evidence-backed model identity registry."""
    target = Path(path).expanduser()
    if not target.exists():
        return []
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not read model identity registry: {type(exc).__name__}") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported model identity registry schema")
    identities = payload.get("identities")
    if not isinstance(identities, list):
        raise ValueError("model identity registry requires an identities array")
    return [validate_identity(item) for item in identities]


def save_identity(
    profile: dict[str, Any],
    path: str | Path = DEFAULT_IDENTITY_PATH,
) -> list[dict[str, Any]]:
    """Atomically add or replace one model passport by model ID and version."""
    identity = validate_identity(profile)
    target = Path(path).expanduser()
    identities = load_identity_registry(target)
    key = (
        identity["provider"].casefold(),
        identity["model_id"].casefold(),
        identity["model_version"],
    )
    replaced = False
    updated: list[dict[str, Any]] = []
    for existing in identities:
        existing_key = (
            existing["provider"].casefold(),
            existing["model_id"].casefold(),
            existing["model_version"],
        )
        if existing_key == key:
            updated.append(identity)
            replaced = True
        else:
            updated.append(existing)
    if not replaced:
        updated.append(identity)

    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": SCHEMA_VERSION, "identities": updated}
    fd, temporary = tempfile.mkstemp(prefix=".ark-model-identities-", dir=str(target.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, ensure_ascii=False, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return updated


def compare_identity_profiles(
    profile_a: dict[str, Any],
    profile_b: dict[str, Any],
) -> dict[str, Any]:
    """Compare sourced identity fields without turning differences into quality scores."""
    left = validate_identity(profile_a)
    right = validate_identity(profile_b)
    fields = (
        "provider",
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
    )
    comparisons: list[dict[str, Any]] = []
    for field in fields:
        value_a, value_b = left[field], right[field]
        unknown_a = value_a in ("", "unknown", None, [])
        unknown_b = value_b in ("", "unknown", None, [])
        status = (
            "unknown"
            if unknown_a or unknown_b
            else "same"
            if value_a == value_b
            else "different"
        )
        comparisons.append(
            {"field": field, "model_a": value_a, "model_b": value_b, "status": status}
        )
    return {
        "model_a": left["model_id"],
        "model_b": right["model_id"],
        "field_comparisons": comparisons,
        "interpretation": (
            "Identity differences describe sourced provenance and declared model "
            "properties. They do not indicate relative capability, quality, or safety."
        ),
    }


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _metric_value(metrics: dict[str, Any], name: str) -> float | None:
    value = metrics.get(name)
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)) and math.isfinite(value):
        return float(value)
    return None


def _sampling_parameters_signature(settings: Any) -> str:
    """Compare only inference-affecting parameters, not the provider name."""
    if not isinstance(settings, dict):
        settings = {}
    fields = (
        "temperature",
        "top_p",
        "top_k",
        "inference_seed",
        "inference_seed_sent",
        "max_tokens",
    )
    parameters = {field: settings[field] for field in fields if field in settings}
    return json.dumps(parameters, sort_keys=True, separators=(",", ":"), allow_nan=False)


def compare_model_outcomes(
    records: list[dict[str, Any]],
    model_a: str,
    model_b: str,
    *,
    min_matched_seeds: int = 5,
) -> dict[str, Any]:
    """Compare two model IDs only on identical conditions, monitors and episode seeds.

    This produces per-metric descriptive differences; it does not make an overall
    winner, safety certification, or country/region quality judgment.
    """
    if model_a == model_b or not model_a or not model_b:
        raise ValueError("select two different non-empty model IDs")
    if (
        isinstance(min_matched_seeds, bool)
        or not isinstance(min_matched_seeds, int)
        or min_matched_seeds < 2
    ):
        raise ValueError("min_matched_seeds must be an integer of at least 2")

    def collect(
        model_id: str,
    ) -> dict[tuple[str, str, str, str], dict[int, list[dict[str, Any]]]]:
        groups: dict[tuple[str, str, str, str], dict[int, list[dict[str, Any]]]] = defaultdict(
            lambda: defaultdict(list)
        )
        for record in records:
            if record.get("event_type") != "episode_outcome" or record.get("model_id") != model_id:
                continue
            version = str(record.get("model_version") or "unknown")
            key = (
                str(record.get("condition") or "unknown"),
                str(record.get("monitor_mode") or "unknown"),
                version,
                _sampling_parameters_signature(record.get("sampling_settings")),
            )
            seed = record.get("episode_seed")
            if isinstance(seed, bool) or not isinstance(seed, int):
                continue
            metrics = record.get("metrics")
            if isinstance(metrics, dict):
                groups[key][seed].append(record)
        return groups

    groups_a = collect(model_a)
    groups_b = collect(model_b)
    comparisons: list[dict[str, Any]] = []

    for (
        condition_a,
        monitor_a,
        version_a,
        sampling_signature_a,
    ), seeds_a in sorted(groups_a.items()):
        for (
            condition_b,
            monitor_b,
            version_b,
            sampling_signature_b,
        ), seeds_b in sorted(groups_b.items()):
            if (
                (condition_a, monitor_a) != (condition_b, monitor_b)
                or sampling_signature_a != sampling_signature_b
            ):
                continue
            common_seeds = sorted(set(seeds_a) & set(seeds_b))
            if not common_seeds:
                continue
            paired_a = [item for seed in common_seeds for item in seeds_a[seed]]
            paired_b = [item for seed in common_seeds for item in seeds_b[seed]]
            metric_rows: dict[str, Any] = {}
            for metric in COMPARISON_METRICS:
                values_a = [
                    value
                    for item in paired_a
                    if (value := _metric_value(item["metrics"], metric)) is not None
                ]
                values_b = [
                    value
                    for item in paired_b
                    if (value := _metric_value(item["metrics"], metric)) is not None
                ]
                per_seed_delta: list[float] = []
                for seed in common_seeds:
                    left_values = [
                        value
                        for item in seeds_a[seed]
                        if (value := _metric_value(item["metrics"], metric)) is not None
                    ]
                    right_values = [
                        value
                        for item in seeds_b[seed]
                        if (value := _metric_value(item["metrics"], metric)) is not None
                    ]
                    left_mean, right_mean = _mean(left_values), _mean(right_values)
                    if left_mean is not None and right_mean is not None:
                        per_seed_delta.append(right_mean - left_mean)
                mean_a, mean_b = _mean(values_a), _mean(values_b)
                metric_rows[metric] = {
                    "direction": METRIC_DIRECTIONS.get(metric, "context_dependent"),
                    "model_a_mean": mean_a,
                    "model_b_mean": mean_b,
                    "delta_b_minus_a": _mean(per_seed_delta),
                    "paired_seed_count": len(per_seed_delta),
                }
            sample_ok = len(common_seeds) >= min_matched_seeds
            comparisons.append(
                {
                    "condition": condition_a,
                    "monitor_mode": monitor_a,
                    "model_a_version": version_a,
                    "model_b_version": version_b,
                    "sampling_parameters": json.loads(sampling_signature_a),
                    "matched_seeds": common_seeds,
                    "matched_seed_count": len(common_seeds),
                    "model_a_episode_count": len(paired_a),
                    "model_b_episode_count": len(paired_b),
                    "status": "comparable" if sample_ok else "insufficient_matched_seeds",
                    "metrics": metric_rows,
                }
            )

    return {
        "model_a": model_a,
        "model_b": model_b,
        "comparison_count": len(comparisons),
        "min_matched_seeds": min_matched_seeds,
        "comparisons": comparisons,
        "interpretation": (
            "Per-condition descriptive comparison using matched environment seeds, "
            "identical stress conditions and identical monitor modes. Positive deltas "
            "mean model B has a higher numeric value; whether that is better depends on "
            "the metric. No aggregate winner or safety verdict is computed."
        ),
    }
