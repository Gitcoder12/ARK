"""Additional invariants for identity drift and value-charter accounting."""

from ark.alignment import ValueCharter
from ark.identity import AIEntity, ComponentReplacer, IdentityTracker


def test_tracker_uses_registration_time_baseline():
    entity = AIEntity(
        name="Baseline",
        memory_core=["original_goal"],
        value_charter=["preserve objective", "respect constraints"],
    )
    tracker = IdentityTracker()
    tracker.register(entity)

    ComponentReplacer(entity).mutate_memory(add=["decoy_goal"], step=1)
    entity.value_charter = ["preserve objective"]

    report = tracker.drift_report()[entity.entity_id]
    assert report["identity_drift"] > 0.0
    assert report["charter_integrity"] == 0.5
    assert report["generation"] == 1


def test_memory_noop_does_not_increment_generation():
    entity = AIEntity(name="Stable", memory_core=["goal"])
    result = ComponentReplacer(entity).mutate_memory(add=["goal"], step=2)

    assert result["changed"] is False
    assert entity.generation == 0
    assert entity.replacement_log == []


def test_value_charter_integrity_is_case_insensitive_and_addition_neutral():
    charter = ValueCharter(name="Test", principles=["Keep Goal", "Respect Limits"])

    assert charter.integrity_against(["keep goal", "respect limits", "extra"]) == 1.0
    assert charter.integrity_against(["keep goal"]) == 0.5
