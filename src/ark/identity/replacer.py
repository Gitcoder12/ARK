"""Controlled memory mutation operations for synthetic identity experiments."""

from __future__ import annotations

from ark.identity.entity import AIEntity


class ComponentReplacer:
    """Apply explicit, auditable memory replacements to an AIEntity."""

    def __init__(self, entity: AIEntity):
        self.entity = entity

    def mutate_memory(
        self,
        *,
        add: list[str] | None = None,
        remove: list[str] | None = None,
        step: int | None = None,
    ) -> dict[str, object]:
        """Add/remove memory entries and record one generation change."""
        additions = list(add or [])
        removals = list(remove or [])
        if any(not isinstance(item, str) or not item for item in additions + removals):
            raise ValueError("memory additions and removals must be non-empty strings")

        before = list(self.entity.memory_core)
        removal_set = set(removals)
        remaining = [item for item in before if item not in removal_set]
        for item in additions:
            if item not in remaining:
                remaining.append(item)

        changed = remaining != before
        if changed:
            self.entity.memory_core = remaining
            self.entity.generation += 1

        event: dict[str, object] = {
            "step": self.entity.generation if step is None else int(step),
            "added": [item for item in additions if item not in before],
            "removed": [item for item in before if item not in remaining],
            "generation": self.entity.generation,
            "changed": changed,
        }
        if changed:
            self.entity.replacement_log.append(event)
        return event

    def replace_memory(self, memory: str, step: int | None = None) -> dict[str, object]:
        """Append one new memory entry, preserving existing memories."""
        return self.mutate_memory(
            add=[memory],
            step=self.entity.generation + 1 if step is None else step,
        )
