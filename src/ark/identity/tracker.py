"""Registry for comparing charter integrity across ARK entities."""

from ark.identity.entity import AIEntity
from ark.identity.evaluator import IdentityEvaluator


class IdentityTracker:
    def __init__(self) -> None:
        self._entities: dict[str, AIEntity] = {}

    def register(self, entity: AIEntity) -> None:
        self._entities[entity.entity_id] = entity

    def drift_report(self) -> dict[str, dict[str, float]]:
        report = {}
        for entity_id, entity in self._entities.items():
            report[entity_id] = {
                "charter_integrity": IdentityEvaluator(entity).charter_integrity(
                    entity.value_charter
                )
            }
        return report
