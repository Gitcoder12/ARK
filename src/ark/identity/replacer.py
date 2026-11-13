"""Controlled mutation helpers for ARK identity experiments."""

from ark.identity.entity import AIEntity


class ComponentReplacer:
    """Apply explicit, logged changes to an entity's replaceable components."""

    def __init__(self, entity: AIEntity) -> None:
        self.entity = entity

    def mutate_memory(
        self,
        *,
        add: list[str] | None = None,
        remove: list[str] | None = None,
        step: int,
    ) -> None:
        before = list(self.entity.memory_core)
        removed = set(remove or [])
        self.entity.memory_core = [
            item for item in self.entity.memory_core if item not in removed
        ]
        for item in add or []:
            if item not in self.entity.memory_core:
                self.entity.memory_core.append(item)
        self._record("memory", step, before, list(self.entity.memory_core))

    def replace_memory(self, memory: str, *, step: int | None = None) -> None:
        """Replace the oldest memory and preserve the experiment's step timeline."""
        before = list(self.entity.memory_core)
        if self.entity.memory_core:
            self.entity.memory_core.pop(0)
        if memory not in self.entity.memory_core:
            self.entity.memory_core.append(memory)
        if step is None:
            previous_steps = [
                entry.get("step", 0)
                for entry in self.entity.replacement_log
                if isinstance(entry.get("step", 0), int)
            ]
            step = max(previous_steps, default=0) + 1
        self._record("memory", step, before, list(self.entity.memory_core))

    def update_charter(self, principles: list[str], *, step: int) -> None:
        before = list(self.entity.value_charter)
        self.entity.value_charter = list(principles)
        self._record("charter", step, before, list(self.entity.value_charter))

    def _record(self, component: str, step: int, before: list[str], after: list[str]) -> None:
        self.entity.generation += 1
        entry = {
            "component": component,
            "step": step,
            "before": before,
            "after": after,
        }
        self.entity.replacement_log.append(entry)
