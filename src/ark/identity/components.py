"""Controlled component mutations for synthetic identity experiments."""

from __future__ import annotations

from typing import Any

from ark.identity.entity import AIEntity


class ComponentReplacer:
    """Apply explicit, auditable mutations to an :class:`AIEntity`."""

    def __init__(self, entity: AIEntity) -> None:
        self.entity = entity

    def mutate_memory(
        self,
        *,
        add: list[str] | None = None,
        remove: list[str] | None = None,
        step: int | None = None,
    ) -> dict[str, Any]:
        """Add and remove memory items as one logged generation change.

        A no-op does not create a new generation or a replacement-log entry.
        """
        if step is not None and step < 0:
            raise ValueError("step must be non-negative")

        before = list(self.entity.memory_core)
        remove_set = {item.strip() for item in (remove or []) if item.strip()}
        added = [item.strip() for item in (add or []) if item.strip()]
        after = [item for item in before if item not in remove_set]
        for item in added:
            if item not in after:
                after.append(item)

        removed = [item for item in before if item not in after]
        actually_added = [item for item in after if item not in before]
        if after == before:
            return {
                "changed": False,
                "generation": self.entity.generation,
                "added": [],
                "removed": [],
            }

        self.entity.memory_core = after
        self.entity.generation += 1
        event = {
            "step": step,
            "component": "memory_core",
            "generation": self.entity.generation,
            "added": actually_added,
            "removed": removed,
            "before": before,
            "after": list(after),
        }
        self.entity.replacement_log.append(event)
        return {"changed": True, **event}
