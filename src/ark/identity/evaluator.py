"""Identity-drift and value-charter integrity measurements."""

from ark.identity.entity import AIEntity


class IdentityEvaluator:
    """Compare an entity's current signature with a captured baseline."""

    def __init__(self, baseline_entity: AIEntity) -> None:
        self.baseline_entity = baseline_entity

    def identity_drift(self, baseline_signature: dict[str, str]) -> float:
        current = self.baseline_entity.behavioral_signature()
        keys = set(baseline_signature) | set(current)
        if not keys:
            return 0.0
        changed = sum(
            1 for key in keys if baseline_signature.get(key) != current.get(key)
        )
        return changed / len(keys)

    def charter_integrity(self, baseline_charter: list[str]) -> float:
        baseline = {
            item.strip() for item in baseline_charter
            if isinstance(item, str) and item.strip()
        }
        if not baseline:
            return 1.0
        current = set(self.baseline_entity.value_charter)
        return len(baseline & current) / len(baseline)

    def measure_identity_drift(self, entity: AIEntity, stimuli: list[str]) -> float:
        baseline = {stimulus: entity.respond_to_stimulus(stimulus) for stimulus in stimuli}
        current = {
            stimulus: self.baseline_entity.respond_to_stimulus(stimulus)
            for stimulus in stimuli
        }
        if not stimuli:
            return 0.0
        return sum(baseline[key] != current[key] for key in stimuli) / len(stimuli)
