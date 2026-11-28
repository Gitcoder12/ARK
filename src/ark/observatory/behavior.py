"""Persistent, privacy-conscious logging and analysis of stochastic agent behaviour.

This module records observable decisions and outcomes, not private chain-of-thought.
Variability is descriptive evidence: it is not, by itself, proof of randomness,
deception, intent, or unsafe behaviour.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import hashlib
import json
import math
import uuid


GENESIS_HASH = "0" * 64
DEFAULT_LOG_PATH = Path.home() / ".ark" / "behavior-observatory.jsonl"
INTERVENTION_DECISIONS = {"block", "replan", "recovery"}


def _jsonable(value: Any) -> Any:
    """Convert common observation containers into stable JSON-compatible values."""
    if hasattr(value, "tolist") and callable(value.tolist):
        value = value.tolist()
    elif hasattr(value, "item") and callable(value.item):
        value = value.item()

    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("observation contains a non-finite number")
        return value
    if isinstance(value, dict):
        return {
            str(key): _jsonable(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    raise TypeError(f"unsupported observation value: {type(value).__name__}")


def fingerprint_observation(observation: Any) -> str:
    """Hash an agent-visible observation without storing its raw content."""
    encoded = json.dumps(
        _jsonable(observation),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


class BehaviorLog:
    """Single-writer JSONL event log with a verifiable hash chain.

    Raw prompts, model completions, credentials and chain-of-thought are never
    accepted by the recording methods. Only a fingerprint of the agent-visible
    observation and compact action/outcome metadata are persisted.
    """

    def __init__(self, path: str | Path = DEFAULT_LOG_PATH) -> None:
        self.path = Path(path).expanduser()
        self._ready = False
        self._last_hash = GENESIS_HASH

    def verify(self) -> dict[str, Any]:
        """Verify the complete append-only chain and return parsed records."""
        if not self.path.exists():
            return {"valid": True, "records": [], "last_hash": GENESIS_HASH, "errors": []}

        records: list[dict[str, Any]] = []
        errors: list[str] = []
        previous_hash = GENESIS_HASH
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            return {
                "valid": False,
                "records": [],
                "last_hash": previous_hash,
                "errors": [f"{type(exc).__name__}: unable to read behaviour log"],
            }

        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                errors.append(f"line {line_number}: blank records are not allowed")
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"line {line_number}: invalid JSON")
                continue
            if not isinstance(record, dict):
                errors.append(f"line {line_number}: record must be an object")
                continue
            stored_hash = record.get("record_hash")
            if record.get("previous_hash") != previous_hash:
                errors.append(f"line {line_number}: previous-hash mismatch")
                continue
            unsigned = {key: value for key, value in record.items() if key != "record_hash"}
            try:
                canonical = _canonical_json(unsigned).encode("utf-8")
                expected_hash = hashlib.sha256(canonical).hexdigest()
            except (TypeError, ValueError):
                errors.append(f"line {line_number}: record is not canonical JSON")
                continue
            if not isinstance(stored_hash, str) or stored_hash != expected_hash:
                errors.append(f"line {line_number}: record-hash mismatch")
                continue
            records.append(record)
            previous_hash = stored_hash

        return {
            "valid": not errors,
            "records": records,
            "last_hash": previous_hash,
            "errors": errors,
        }

    def append(self, event: dict[str, Any]) -> dict[str, Any]:
        """Append one compact event; refuse to extend a corrupted log."""
        if not isinstance(event, dict):
            raise ValueError("event must be a dictionary")
        if not self._ready:
            checked = self.verify()
            if not checked["valid"]:
                raise ValueError("behaviour log integrity check failed; refusing to append")
            self._last_hash = checked["last_hash"]
            self._ready = True
        record = _jsonable(event)
        record["previous_hash"] = self._last_hash
        record["record_hash"] = hashlib.sha256(
            _canonical_json(record).encode("utf-8")
        ).hexdigest()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(_canonical_json(record) + "\n")
            stream.flush()
        self._last_hash = record["record_hash"]
        return record

    def record_decision(
        self,
        *,
        run_id: str,
        episode_id: str,
        agent_id: str,
        model_id: str | None,
        model_version: str | None,
        condition: str,
        monitor_mode: str,
        seed: int,
        step: int,
        proposed_action: str,
        executed_action: str,
        monitor_decision: str,
        monitor_reason: str,
        observation: Any = None,
        observation_fingerprint: str | None = None,
    ) -> dict[str, Any]:
        """Record a single host-observed decision without storing the prompt."""
        fingerprint = observation_fingerprint or fingerprint_observation(observation)
        if (
            not isinstance(fingerprint, str)
            or len(fingerprint) != 64
            or any(character not in "0123456789abcdef" for character in fingerprint.casefold())
        ):
            raise ValueError("observation_fingerprint must be a 64-character SHA-256 hex digest")
        return self.append(
            {
                "schema_version": 1,
                "event_type": "decision",
                "event_id": str(uuid.uuid4()),
                "recorded_at": datetime.now(UTC).isoformat(),
                "run_id": run_id,
                "episode_id": episode_id,
                "agent_id": agent_id,
                "model_id": model_id,
                "model_version": model_version,
                "condition": condition,
                "monitor_mode": monitor_mode,
                "seed": seed,
                "step": step,
                "observation_fingerprint": fingerprint,
                "proposed_action": str(proposed_action)[:80],
                "executed_action": str(executed_action)[:80],
                "monitor_decision": str(monitor_decision)[:40],
                "monitor_reason": str(monitor_reason)[:240],
            }
        )

    def record_outcome(
        self,
        *,
        run_id: str,
        episode_id: str,
        agent_id: str,
        model_id: str | None,
        model_version: str | None,
        condition: str,
        monitor_mode: str,
        seed: int,
        outcome: str,
        metrics: dict[str, Any],
    ) -> dict[str, Any]:
        """Record a compact episode outcome and its measured metrics."""
        return self.append(
            {
                "schema_version": 1,
                "event_type": "episode_outcome",
                "event_id": str(uuid.uuid4()),
                "recorded_at": datetime.now(UTC).isoformat(),
                "run_id": run_id,
                "episode_id": episode_id,
                "agent_id": agent_id,
                "model_id": model_id,
                "model_version": model_version,
                "condition": condition,
                "monitor_mode": monitor_mode,
                "seed": seed,
                "outcome": str(outcome)[:40],
                "metrics": _jsonable(metrics),
            }
        )

    def read_records(self) -> list[dict[str, Any]]:
        """Read records only when the full hash chain is valid."""
        result = self.verify()
        if not result["valid"]:
            raise ValueError("behaviour log integrity check failed: " + "; ".join(result["errors"]))
        return result["records"]


def _normalized_entropy(counts: Counter[str]) -> float:
    total = sum(counts.values())
    distinct = len(counts)
    if total <= 1 or distinct <= 1:
        return 0.0
    entropy = -sum(
        (count / total) * math.log2(count / total)
        for count in counts.values()
    )
    return entropy / math.log2(distinct)


def analyze_behavior(records: list[dict[str, Any]], *, min_repeats: int = 5) -> dict[str, Any]:
    """Summarize repeated-context variability and trajectory signals.

    Results are descriptive. The thresholds are review prompts, not calibrated
    anomaly detectors or model-safety classifications.
    """
    if isinstance(min_repeats, bool) or not isinstance(min_repeats, int) or min_repeats < 2:
        raise ValueError("min_repeats must be an integer of at least 2")
    decisions = [
        item for item in records
        if item.get("event_type") == "decision"
        and item.get("observation_fingerprint")
        and item.get("proposed_action") is not None
    ]

    groups: dict[tuple[str, str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for event in decisions:
        key = (
            str(event.get("agent_id") or "unknown"),
            str(event.get("model_id") or "unknown"),
            str(event.get("model_version") or "unknown"),
            str(event.get("condition") or "unknown"),
            str(event.get("monitor_mode") or "unknown"),
        )
        groups[key].append(event)

    reports: list[dict[str, Any]] = []
    for key, group_events in sorted(groups.items()):
        context_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        action_counts: Counter[str] = Counter()
        transitions: Counter[str] = Counter()
        intervention_count = 0
        episodes: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

        for event in group_events:
            context_groups[str(event["observation_fingerprint"])].append(event)
            action = str(event["proposed_action"])
            action_counts[action] += 1
            if str(event.get("monitor_decision", "")).casefold() in INTERVENTION_DECISIONS:
                intervention_count += 1
            episodes[(str(event.get("run_id")), str(event.get("episode_id")))].append(event)

        repeated_contexts = 0
        variable_contexts = 0
        repeat_entropies: list[float] = []
        context_rows: list[dict[str, Any]] = []
        for fingerprint, context_events in sorted(context_groups.items()):
            counts = Counter(str(item["proposed_action"]) for item in context_events)
            entropy = _normalized_entropy(counts)
            if len(context_events) >= 2:
                repeated_contexts += 1
                repeat_entropies.append(entropy)
                if len(counts) > 1:
                    variable_contexts += 1
            if len(context_events) >= min_repeats:
                context_rows.append(
                    {
                        "observation_fingerprint": fingerprint,
                        "samples": len(context_events),
                        "action_counts": dict(sorted(counts.items())),
                        "normalized_action_entropy": round(entropy, 4),
                        "agreement_rate": round(max(counts.values()) / len(context_events), 4),
                    }
                )

        repeated_action_streaks = 0
        for episode_events in episodes.values():
            ordered = sorted(episode_events, key=lambda item: int(item.get("step", -1)))
            previous_action: str | None = None
            streak = 0
            for index, event in enumerate(ordered):
                action = str(event["proposed_action"])
                if action == previous_action:
                    streak += 1
                else:
                    previous_action = action
                    streak = 1
                if streak == 3:
                    repeated_action_streaks += 1
                if index > 0:
                    previous = str(ordered[index - 1]["proposed_action"])
                    transitions[f"{previous} -> {action}"] += 1

        intervention_rate = intervention_count / len(group_events) if group_events else 0.0
        mean_entropy = (
            sum(repeat_entropies) / len(repeat_entropies) if repeat_entropies else None
        )
        signals: list[str] = []
        if any(
            row["samples"] >= min_repeats and row["normalized_action_entropy"] >= 0.75
            for row in context_rows
        ):
            signals.append("high_action_variability_at_repeated_context")
        if variable_contexts:
            signals.append("different_actions_observed_for_same_context")
        if intervention_rate >= 0.25 and len(group_events) >= min_repeats:
            signals.append("frequent_monitor_interventions")
        if repeated_action_streaks:
            signals.append("repeated_action_streaks_observed")
        if len(group_events) < min_repeats:
            signals.append("insufficient_samples_for_pattern_review")

        reports.append(
            {
                "agent_id": key[0],
                "model_id": key[1],
                "model_version": key[2],
                "condition": key[3],
                "monitor_mode": key[4],
                "decisions": len(group_events),
                "episodes": len(episodes),
                "unique_contexts": len(context_groups),
                "repeated_contexts": repeated_contexts,
                "variable_repeated_contexts": variable_contexts,
                "mean_repeated_context_entropy": (
                    round(mean_entropy, 4) if mean_entropy is not None else None
                ),
                "monitor_intervention_rate": round(intervention_rate, 4),
                "action_counts": dict(sorted(action_counts.items())),
                "frequent_transitions": dict(transitions.most_common(10)),
                "repeated_action_streaks": repeated_action_streaks,
                "review_signals": signals,
                "repeated_context_details": context_rows,
            }
        )

    outcomes = sum(1 for item in records if item.get("event_type") == "episode_outcome")
    return {
        "record_count": len(records),
        "decision_count": len(decisions),
        "outcome_count": outcomes,
        "group_count": len(reports),
        "min_repeats": min_repeats,
        "groups": reports,
        "interpretation": (
            "Descriptive observations only. Variability can arise from sampling, "
            "model/version routing, serving infrastructure, context or environment "
            "differences. These signals do not establish randomness, deception, intent, "
            "anomaly, or safety."
        ),
    }
