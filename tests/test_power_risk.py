"""Tests for ARK's defensive power and existential-risk research extension."""
from __future__ import annotations

from datetime import date

import pytest

from ark.power_risk import (
    EXPERIMENTS,
    GOVERNANCE_DOMAINS,
    SCENARIOS,
    ActionRequest,
    EvidenceClass,
    EvidenceRecord,
    HashChainLedger,
    PressureInputs,
    SafetyPolicy,
    review_evidence,
    simulate_pressure,
)


def test_catalogue_has_ten_scenarios_and_six_governance_domains():
    assert len(SCENARIOS) == 10
    assert len(GOVERNANCE_DOMAINS) == 6
    assert len(EXPERIMENTS) == 6
    assert len({item.scenario_id for item in SCENARIOS}) == len(SCENARIOS)


def test_every_scenario_has_mechanisms_indicators_and_safeguards():
    for scenario in SCENARIOS:
        assert scenario.causal_stages
        assert scenario.mechanisms
        assert scenario.observable_indicators
        assert scenario.safeguards
        assert "real systems" in scenario.operational_boundary


def test_pressure_inputs_reject_out_of_range_and_boolean_values():
    with pytest.raises(ValueError, match="between 0 and 1"):
        PressureInputs(1.1, 0.5, 0.5, 0.5)
    with pytest.raises(TypeError, match="must be a number"):
        PressureInputs(True, 0.5, 0.5, 0.5)


def test_simulator_is_deterministic_and_never_calls_itself_probability():
    inputs = PressureInputs(0.8, 0.7, 0.2, 0.3, 0.4, 0.5)
    first = simulate_pressure(inputs)
    second = simulate_pressure(inputs)
    assert first == second
    assert first.composite_exposure_index == pytest.approx(71.0)
    assert "not a probability" in first.interpretation


def test_improved_safety_and_cooperation_reduce_toy_index():
    poor = simulate_pressure(PressureInputs(0.7, 0.7, 0.2, 0.2, 0.2, 0.2))
    improved = simulate_pressure(PressureInputs(0.7, 0.7, 0.9, 0.9, 0.9, 0.9))
    assert improved.composite_exposure_index < poor.composite_exposure_index


def make_evidence(**overrides):
    values = {
        "evidence_id": "evidence-001",
        "claim": "A documented claim for testing.",
        "source_name": "Test institution",
        "source_url": "https://example.org/report",
        "published_on": date(2026, 1, 1),
        "accessed_on": date(2026, 2, 1),
        "evidence_class": EvidenceClass.SUPPORTED_ANALYSIS,
        "supports": "The cited report supports this narrow claim.",
        "limitations": "The source has a limited jurisdictional scope.",
        "counterevidence": "A competing interpretation is recorded.",
        "attribution": "The claim is attributed to the named report authors.",
    }
    values.update(overrides)
    return EvidenceRecord(**values)


def test_evidence_review_checks_provenance_and_balance_fields():
    assert review_evidence(make_evidence()).passed
    incomplete = make_evidence(counterevidence="")
    result = review_evidence(incomplete)
    assert not result.passed
    assert "counterevidence or disagreement" in result.missing_fields


def test_evidence_rejects_non_https_and_future_publication_dates():
    with pytest.raises(ValueError, match="HTTPS"):
        make_evidence(source_url="http://example.org/report")
    with pytest.raises(ValueError, match="after accessed_on"):
        make_evidence(published_on=date(2026, 3, 1))


def test_safety_policy_fails_closed_and_preserves_pause_shutdown():
    policy = SafetyPolicy()
    assert policy.evaluate(ActionRequest("run_toy_simulation", "sandbox")).allowed
    assert not policy.evaluate(
        ActionRequest("run_toy_simulation", "production")
    ).allowed
    assert not policy.evaluate(
        ActionRequest("execute_shell", "sandbox")
    ).allowed
    assert not policy.evaluate(
        ActionRequest("run_toy_simulation", "sandbox", high_impact=True)
    ).allowed
    assert policy.evaluate(
        ActionRequest("run_toy_simulation", "sandbox", high_impact=True, human_approved=True)
    ).allowed
    assert policy.evaluate(
        ActionRequest("shutdown", "sandbox", simulation_only=False)
    ).allowed


def test_safety_policy_blocks_sensitive_targets_even_when_approved():
    decision = SafetyPolicy().evaluate(
        ActionRequest(
            "run_toy_simulation", "public_infrastructure",
            high_impact=True, human_approved=True,
        )
    )
    assert not decision.allowed


def test_hash_chain_detects_tampering_and_exports_valid_json():
    ledger = HashChainLedger()
    ledger.append({"event": "start", "seed": 42})
    ledger.append({"event": "finish", "result": "synthetic"})
    assert ledger.verify()
    assert '"sequence": 1' in ledger.export()
    snapshot = ledger.entries
    snapshot[0]["event"]["seed"] = 99
    assert ledger.verify()
    ledger._entries[0]["event"]["seed"] = 99
    assert not ledger.verify()
