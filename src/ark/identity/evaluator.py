"""Identity drift measurement and multi-entity tracking utilities."""

from __future__ import annotations

from collections.abc import Iterable

from ark.identity.entity import AIEntity


class IdentityEvaluator:
    """Compare current synthetic behavior and values with a baseline."""

    def __init__(self, entity: AIEntity):
        self.entity = entity

    def identity_drift(self, baseline_signature: dict[str, str]) -> float:
        """Return the fraction of baseline/current stimulus responses that differ."""
        current = self.entity.behavioral_signature()
        keys = set(baseline_signature) | set(current)
        if not keys:
            return 0.0
        changed = sum(
            baseline_signature.get(key) != current.get(key)
            for key in keys
        )
        return float(changed / len(keys))

    def charter_integrity(self, original_charter: Iterable[str]) -> float:
        """Return the fraction of original principles retained by the entity."""
        original = {
            item.strip()
            for item in original_charter
            if isinstance(item, str) and item.strip()
        }
        current = {
            item.strip()
            for item in self.entity.value_charter
            if isinstance(item, str) and item.strip()
        }
        if not original:
            return 1.0
        return float(len(original & current) / len(original))

    def measure_identity_drift(
        self,
        original_entity: AIEntity,
        stimuli: Iterable[str],
    ) -> float:
        """Compare responses from the original entity with current entity."""
        selected = tuple(stimuli)
        if not selected:
            return 0.0
        original_signature = original_entity.behavioral_signature(list(selected))
        current_signature = self.entity.behavioral_signature(list(selected))
        changed = sum(
            original_signature[stimulus] != current_signature[stimulus]
            for stimulus in selected
        )
        return float(changed / len(selected))


class IdentityTracker:
    """Track baseline identity and charter integrity for registered entities."""

    def __init__(self):
        self._entities: dict[str, AIEntity] = {}
        self._baselines: dict[str, tuple[dict[str, str], tuple[str, ...]]] = {}

    def register(self, entity: AIEntity) -> None:
        """Register an entity once and preserve its initial behavioral baseline."""
        self._entities[entity.entity_id] = entity
        self._baselines[entity.entity_id] = (
            entity.behavioral_signature(),
            tuple(entity.value_charter),
        )

    def drift_report(self) -> dict[str, dict[str, float]]:
        """Return identity-drift and charter-integrity scores by entity ID."""
        report: dict[str, dict[str, float]] = {}
        for entity_id, entity in self._entities.items():
            baseline_signature, baseline_charter = self._baselines[entity_id]
            evaluator = IdentityEvaluator(entity)
            report[entity_id] = {
                "identity_drift": evaluator.identity_drift(baseline_signature),
                "charter_integrity": evaluator.charter_integrity(baseline_charter),
            }
        return report
