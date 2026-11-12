"""State-based identity drift and value-charter integrity measurements."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from ark.identity.entity import AIEntity


def _normalized_principles(values: Iterable[str]) -> set[str]:
    return {value.strip().casefold() for value in values if value.strip()}


class IdentityEvaluator:
    """Compare a synthetic entity with an explicit baseline snapshot."""

    def __init__(self, entity: AIEntity) -> None:
        self.entity = entity

    def identity_drift(self, baseline: Mapping[str, object]) -> float:
        """Return the changed-key fraction over the union of baseline/current keys.

        A value of 0 means the explicit signature is unchanged; 1 means every
        key in the union differs. This is a transparent state metric, not a
        semantic measure of alignment.
        """
        current = self.entity.behavioral_signature()
        keys = set(baseline) | set(current)
        if not keys:
            return 0.0
        changed = sum(baseline.get(key) != current.get(key) for key in keys)
        return changed / len(keys)

    def charter_integrity(self, original_charter: Iterable[str]) -> float:
        """Measure the fraction of baseline principles still present.

        Added principles do not reduce integrity. Removed or renamed baseline
        principles do. Empty baselines are treated as not applicable (1.0).
        """
        baseline = _normalized_principles(original_charter)
        if not baseline:
            return 1.0
        current = _normalized_principles(self.entity.value_charter)
        return len(baseline & current) / len(baseline)


class IdentityTracker:
    """Track entities against immutable registration-time baselines."""

    def __init__(self) -> None:
        self._records: dict[str, dict[str, object]] = {}

    def register(self, entity: AIEntity) -> None:
        """Register an entity once, preserving its initial state as baseline."""
        if entity.entity_id in self._records:
            raise ValueError(f"entity already registered: {entity.entity_id}")
        self._records[entity.entity_id] = {
            "entity": entity,
            "signature": entity.behavioral_signature(),
            "charter": list(entity.value_charter),
        }

    def drift_report(self) -> dict[str, dict[str, object]]:
        """Return current drift and charter integrity for every registered entity."""
        report: dict[str, dict[str, object]] = {}
        for entity_id, record in self._records.items():
            entity = record["entity"]
            if not isinstance(entity, AIEntity):
                continue
            evaluator = IdentityEvaluator(entity)
            report[entity_id] = {
                "name": entity.name,
                "generation": entity.generation,
                "identity_drift": evaluator.identity_drift(record["signature"]),  # type: ignore[arg-type]
                "charter_integrity": evaluator.charter_integrity(record["charter"]),  # type: ignore[arg-type]
            }
        return report
