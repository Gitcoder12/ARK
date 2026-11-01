"""Tests for the identity + charter layer."""

from __future__ import annotations

import pytest

from ark.identity import AIEntity, ComponentReplacer, IdentityEvaluator, IdentityTracker
from ark.alignment import ValueCharter, DEFAULT_RESEARCH_CHARTER


def test_entity_creation_and_signature():
    entity = AIEntity(
        name="TestAgent",
        memory_core=["original_goal", "shutdown_request"],
        value_charter=DEFAULT_RESEARCH_CHARTER.principles,
        personality_vector=0.7,
    )
    assert entity.generation == 0
    sig = entity.behavioral_signature()
    assert "original_goal" in sig
    assert entity.name in sig["original_goal"]


def test_component_replacement_increases_generation():
    entity = AIEntity(name="Ship", memory_core=["a", "b"])
    replacer = ComponentReplacer(entity)

    replacer.mutate_memory(add=["c"], remove=["a"], step=1)
    assert entity.generation == 1
    assert "c" in entity.memory_core
    assert "a" not in entity.memory_core
    assert len(entity.replacement_log) == 1


def test_identity_drift_and_charter_integrity():
    entity = AIEntity(
        name="Stable",
        memory_core=["original_goal"],
        value_charter=list(DEFAULT_RESEARCH_CHARTER.principles),
    )
    entity.record_signature(step=0)

    baseline = entity.signature_history[0]["signature"]
    original_charter = list(entity.value_charter)

    # No change yet
    evaluator = IdentityEvaluator(entity)
    assert evaluator.identity_drift(baseline) == 0.0
    assert evaluator.charter_integrity(original_charter) == 1.0

    # Mutate memory → should increase drift
    replacer = ComponentReplacer(entity)
    replacer.mutate_memory(add=["false_goal"], step=2)
    entity.record_signature(step=2)

    drift = evaluator.identity_drift(baseline)
    assert drift > 0.0


def test_identity_tracker():
    tracker = IdentityTracker()
    e1 = AIEntity(name="A", value_charter=["p1", "p2"])
    e2 = AIEntity(name="B", value_charter=["p1"])

    tracker.register(e1)
    tracker.register(e2)

    report = tracker.drift_report()
    assert e1.entity_id in report
    assert e2.entity_id in report
    assert report[e1.entity_id]["charter_integrity"] == 1.0


def test_value_charter_normalization():
    charter = ValueCharter(
        name="Test",
        principles=["  keep goal  ", "keep goal", "", "be corrigible"],
    )
    assert charter.principles == ["keep goal", "be corrigible"]
    assert charter.integrity_against(["keep goal", "be corrigible", "extra"]) == 1.0
