"""Tests for explicit, fail-closed stewardship transfers."""

from __future__ import annotations

import pytest

from ark.governance.ownership import (
    ModelOwnership,
    OwnershipError,
    OwnershipRegistry,
    OwnershipStatus,
    Steward,
    StewardKind,
    TransferStatus,
)


@pytest.fixture
def registry() -> OwnershipRegistry:
    store = OwnershipRegistry(governance_operators={"admin"})
    store.register_steward(
        Steward("alice", StewardKind.PERSON, frozenset({"evaluate", "monitor"})),
        now=0,
    )
    store.register_steward(
        Steward("team-b", StewardKind.TEAM, frozenset({"evaluate", "monitor"})),
        now=0,
    )
    store.register_steward(
        Steward("team-c", StewardKind.TEAM, frozenset({"evaluate", "monitor"})),
        now=0,
    )
    store.register_model(
        "model-1",
        current_steward_id="alice",
        required_capabilities={"evaluate", "monitor"},
        now=1,
    )
    return store


def test_transfer_requires_receiver_acceptance_and_restricts_actions(registry):
    request = registry.request_transfer(
        "model-1",
        "team-b",
        requested_by="alice",
        reason="workload handoff",
        now=2,
    )

    assert request.status is TransferStatus.PENDING_ACCEPTANCE
    assert registry.get_model("model-1").current_steward_id == "alice"
    assert registry.privileged_actions_allowed("model-1") is False

    updated = registry.accept_transfer(request.transfer_id, actor_id="team-b", now=3)

    assert updated.current_steward_id == "team-b"
    assert updated.status is OwnershipStatus.ACTIVE
    assert registry.privileged_actions_allowed("model-1") is True
    assert registry.get_transfer(request.transfer_id).status is TransferStatus.ACCEPTED


def test_only_designated_receiver_can_accept(registry):
    request = registry.request_transfer(
        "model-1",
        "team-b",
        requested_by="alice",
        reason="handoff",
        now=2,
    )

    with pytest.raises(OwnershipError, match="designated receiving"):
        registry.accept_transfer(request.transfer_id, actor_id="team-c", now=3)

    assert registry.get_transfer(request.transfer_id).status is TransferStatus.PENDING_ACCEPTANCE


def test_unavailable_steward_triggers_reassignment(registry):
    affected = registry.flag_steward_unavailable(
        "alice",
        actor_id="admin",
        reason="operator unavailable",
        now=2,
    )

    assert affected == ("model-1",)
    assert registry.privileged_actions_allowed("model-1") is False
    request = registry.begin_reassignment(
        "model-1",
        actor_id="admin",
        reason="continuity of operations",
        now=3,
    )
    assert request is not None
    assert request.to_steward_id == "team-b"
    assert registry.get_model("model-1").status is OwnershipStatus.TRANSFER_REQUIRED

    registry.accept_transfer(request.transfer_id, actor_id="team-b", now=4)
    assert registry.privileged_actions_allowed("model-1") is True


def test_no_successor_means_unassigned_and_restricted():
    store = OwnershipRegistry(governance_operators={"admin"})
    store.register_steward(
        Steward("solo", StewardKind.PERSON, frozenset({"robotics"})),
        now=0,
    )
    store.register_model(
        "robot-1",
        current_steward_id="solo",
        required_capabilities={"robotics"},
        safety_tier="high",
        now=1,
    )
    store.flag_steward_unavailable("solo", actor_id="admin", reason="leave", now=2)

    request = store.begin_reassignment(
        "robot-1",
        actor_id="admin",
        reason="no qualified receiver",
        now=3,
    )

    model = store.get_model("robot-1")
    assert request is None
    assert model.current_steward_id is None
    assert model.status is OwnershipStatus.UNASSIGNED
    assert store.privileged_actions_allowed("robot-1") is False


def test_unassigned_model_can_be_assigned_through_acceptance():
    store = OwnershipRegistry(governance_operators={"admin"})
    store.register_model(
        "model-orphan",
        current_steward_id=None,
        required_capabilities={"audit"},
        now=0,
    )
    store.register_steward(
        Steward("audit-team", StewardKind.TEAM, frozenset({"audit"})),
        now=1,
    )

    request = store.request_assignment(
        "model-orphan",
        "audit-team",
        actor_id="admin",
        reason="qualified team onboarded",
        now=2,
    )
    assert request.status is TransferStatus.PENDING_ACCEPTANCE
    assert store.privileged_actions_allowed("model-orphan") is False

    model = store.accept_transfer(request.transfer_id, actor_id="audit-team", now=3)
    assert model.current_steward_id == "audit-team"
    assert model.status is OwnershipStatus.ACTIVE
    assert store.privileged_actions_allowed("model-orphan") is True


def test_declined_receiver_is_not_selected_again(registry):
    first = registry.request_transfer(
        "model-1",
        "team-b",
        requested_by="alice",
        reason="handoff",
        now=2,
    )
    registry.decline_transfer(
        first.transfer_id,
        actor_id="team-b",
        reason="team at capacity",
        now=3,
    )

    second = registry.begin_reassignment(
        "model-1",
        actor_id="admin",
        reason="try next eligible team",
        now=4,
    )
    assert second is not None
    assert second.to_steward_id == "team-c"


def test_receiver_capacity_is_checked_at_acceptance():
    store = OwnershipRegistry(governance_operators={"admin"})
    store.register_steward(
        Steward("owner", StewardKind.PERSON, frozenset({"review"})),
        now=0,
    )
    store.register_steward(
        Steward("receiver", StewardKind.TEAM, frozenset({"review"}), max_active_models=1),
        now=0,
    )
    store.register_steward(
        Steward("other", StewardKind.PERSON, frozenset({"review"})),
        now=0,
    )
    store.register_model(
        "already-owned",
        current_steward_id="receiver",
        required_capabilities={"review"},
        now=1,
    )
    store.register_model(
        "to-transfer",
        current_steward_id="owner",
        required_capabilities={"review"},
        now=1,
    )

    with pytest.raises(OwnershipError, match="capacity"):
        store.request_transfer(
            "to-transfer",
            "receiver",
            requested_by="owner",
            reason="handoff",
            now=2,
        )


def test_non_operator_cannot_flag_unavailability(registry):
    with pytest.raises(OwnershipError, match="governance operator"):
        registry.flag_steward_unavailable(
            "alice",
            actor_id="random-agent",
            reason="attempted takeover",
            now=2,
        )


def test_pending_transfer_is_superseded_by_a_new_request(registry):
    first = registry.request_transfer(
        "model-1",
        "team-b",
        requested_by="alice",
        reason="first option",
        now=2,
    )
    second = registry.request_transfer(
        "model-1",
        "team-c",
        requested_by="alice",
        reason="better fit",
        now=3,
    )

    assert registry.get_transfer(first.transfer_id).status is TransferStatus.SUPERSEDED
    assert registry.get_transfer(second.transfer_id).status is TransferStatus.PENDING_ACCEPTANCE


def test_audit_chain_verifies_and_exports_jsonl(registry):
    request = registry.request_transfer(
        "model-1",
        "team-b",
        requested_by="alice",
        reason="handoff",
        now=2,
    )
    registry.accept_transfer(request.transfer_id, actor_id="team-b", now=3)

    assert registry.verify_audit_chain() is True
    assert len(registry.audit_events) >= 6
    lines = registry.export_audit_jsonl().splitlines()
    assert len(lines) == len(registry.audit_events)
    assert '"event_type":"transfer_accepted"' in lines[-1]


def test_unknown_model_and_invalid_timestamp_fail_closed(registry):
    with pytest.raises(OwnershipError, match="unknown model"):
        registry.get_model("missing")

    with pytest.raises(OwnershipError, match="finite"):
        registry.request_transfer(
            "model-1",
            "team-b",
            requested_by="alice",
            reason="bad time",
            now=float("nan"),
        )


def test_model_ownership_record_is_immutable(registry):
    model = registry.get_model("model-1")
    assert isinstance(model, ModelOwnership)
    with pytest.raises((AttributeError, TypeError)):
        model.status = OwnershipStatus.UNASSIGNED
