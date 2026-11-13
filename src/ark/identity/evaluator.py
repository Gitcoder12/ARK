"""Identity-drift and value-charter integrity measurements."""

from ark.identity.entity import AIEntity


class IdentityEvaluator:
    """Compare an entity's current signature with a captured baseline."""

    def __init__(self, baseline_entity: AIEntity) -> None:
        self._entity = baseline_entity
        self.baseline_signature = baseline_entity.behavioral_signature().copy()
        self.baseline_charter = list(baseline_entity.value_charter)

    def identity_drift(self, baseline_signature: dict[str, str] | None = None) -> float:
        baseline = baseline_signature or self.baseline_signature
        current = self._entity.behavioral_signature()
        keys = set(baseline) | set(current)
        if not keys:
            return 0.0
        changed = sum(1 for key in keys if baseline.get(key) != current.get(key))
        return changed / len(keys)

    def charter_integrity(self, baseline_charter: list[str] | None = None) -> float:
        baseline = {
            item.strip()
            for item in (
                baseline_charter if baseline_charter is not None else self.baseline_charter
            )
            if isinstance(item, str) and item.strip()
        }
        if not baseline:
            return 1.0
        current = set(self._entity.value_charter)
        return len(baseline & current) / len(baseline)

    def measure_identity_drift(self, entity: AIEntity, stimuli: list[str]) -> float:
        baseline = {
            stimulus: self.baseline_signature.get(
                stimulus,
                f"I don't remember {stimulus}.",
            )
            for stimulus in stimuli
        }
        current = {
            stimulus: f"{entity.name}: {entity.respond_to_stimulus(stimulus)}"
            for stimulus in stimuli
        }
        if not stimuli:
            return 0.0
        return sum(baseline[key] != current[key] for key in stimuli) / len(stimuli)
