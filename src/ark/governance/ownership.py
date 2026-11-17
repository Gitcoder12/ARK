"""Human/team stewardship transfer for ARK model deployments.

This is a governance-domain prototype. It records accountable stewards and
requires explicit receiver acceptance before a handoff becomes active.
It does not authenticate identities, persist state, or enforce external
tool/actuator permissions; production deployments must place it behind a
trusted identity provider, transactional store, and independent control plane.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterable
from dataclasses import asdict, dataclass, replace
from enum import StrEnum
from uuid import uuid4


class StewardKind(StrEnum):
    """The human or organizational unit accountable for a deployment."""

    PERSON = "person"
    TEAM = "team"


class OwnershipStatus(StrEnum):
    """Whether a deployment has an active steward and may use privileged tools."""

    ACTIVE = "active"
    TRANSFER_REQUIRED = "transfer_required"
    UNASSIGNED = "unassigned"


class TransferStatus(StrEnum):
    """State of an explicit stewardship handoff request."""

    PENDING_ACCEPTANCE = "pending_acceptance"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    SUPERSEDED = "superseded"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Steward:
    """A person/team principal with bounded capacity and declared competencies."""

    steward_id: str
    kind: StewardKind
    capabilities: frozenset[str]
    max_active_models: int = 3
    available: bool = True
    active: bool = True


@dataclass(frozen=True)
class ModelOwnership:
    """Current accountable steward and restrictions for one model deployment."""

    model_id: str
    current_steward_id: str | None
    required_capabilities: frozenset[str]
    safety_tier: str = "standard"
    status: OwnershipStatus = OwnershipStatus.ACTIVE


@dataclass(frozen=True)
class TransferRequest:
    """A proposed transfer; pending requests do not change the current steward."""

    transfer_id: str
    model_id: str
    from_steward_id: str
    to_steward_id: str
    requested_by: str
    reason: str
    created_at: float
    status: TransferStatus = TransferStatus.PENDING_ACCEPTANCE
    resolved_at: float | None = None


@dataclass(frozen=True)
class AuditEvent:
    """Hash-chained audit event with non-secret, canonicalized details."""

    sequence: int
    event_type: str
    actor_id: str
    occurred_at: float
    subject_id: str
    details: tuple[tuple[str, str], ...]
    previous_hash: str
    event_hash: str


class OwnershipError(ValueError):
    """Raised when a stewardship operation violates governance policy."""


class OwnershipRegistry:
    """Track model stewardship and fail closed while transfers are unresolved.

    Governance operators may flag unavailability and initiate reassignment.
    A receiver must accept a request using its own principal ID. No model/agent
    identity is accepted as an operator, requester, or receiving steward.
    """

    def __init__(self, *, governance_operators: Iterable[str] = ()) -> None:
        operators = frozenset(
            self._required_text(value, "governance operator")
            for value in governance_operators
        )
        self._governance_operators = operators
        self._stewards: dict[str, Steward] = {}
        self._models: dict[str, ModelOwnership] = {}
        self._transfers: dict[str, TransferRequest] = {}
        self._events: list[AuditEvent] = []

    @staticmethod
    def _required_text(value: str, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise OwnershipError(f"{field} must be a non-empty string")
        return value.strip()

    @staticmethod
    def _timestamp(value: float) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise OwnershipError("timestamp must be numeric")
        timestamp = float(value)
        if not math.isfinite(timestamp):
            raise OwnershipError("timestamp must be finite")
        return timestamp

    def _record_event(
        self,
        event_type: str,
        actor_id: str,
        occurred_at: float,
        subject_id: str,
        **details: object,
    ) -> AuditEvent:
        timestamp = self._timestamp(occurred_at)
        normalized = tuple(sorted((key, str(value)) for key, value in details.items()))
        previous_hash = self._events[-1].event_hash if self._events else "0" * 64
        payload = {
            "sequence": len(self._events) + 1,
            "event_type": event_type,
            "actor_id": actor_id,
            "occurred_at": timestamp,
            "subject_id": subject_id,
            "details": dict(normalized),
            "previous_hash": previous_hash,
        }
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        digest = hashlib.sha256(encoded).hexdigest()
        event = AuditEvent(
            sequence=payload["sequence"],
            event_type=event_type,
            actor_id=actor_id,
            occurred_at=timestamp,
            subject_id=subject_id,
            details=normalized,
            previous_hash=previous_hash,
            event_hash=digest,
        )
        self._events.append(event)
        return event

    @property
    def audit_events(self) -> tuple[AuditEvent, ...]:
        """Read-only snapshot of the append-only in-process audit history."""
        return tuple(self._events)

    @property
    def stewards(self) -> tuple[Steward, ...]:
        return tuple(self._stewards[key] for key in sorted(self._stewards))

    @property
    def models(self) -> tuple[ModelOwnership, ...]:
        return tuple(self._models[key] for key in sorted(self._models))

    @property
    def transfers(self) -> tuple[TransferRequest, ...]:
        return tuple(self._transfers[key] for key in sorted(self._transfers))

    def get_model(self, model_id: str) -> ModelOwnership:
        key = self._required_text(model_id, "model_id")
        try:
            return self._models[key]
        except KeyError as exc:
            raise OwnershipError(f"unknown model deployment: {key}") from exc

    def get_transfer(self, transfer_id: str) -> TransferRequest:
        key = self._required_text(transfer_id, "transfer_id")
        try:
            return self._transfers[key]
        except KeyError as exc:
            raise OwnershipError(f"unknown transfer request: {key}") from exc

    def _active_load(self, steward_id: str) -> int:
        return sum(
            model.current_steward_id == steward_id
            and model.status is not OwnershipStatus.UNASSIGNED
            for model in self._models.values()
        )

    def _reserved_load(
        self,
        steward_id: str,
        *,
        excluding_model_id: str | None = None,
        excluding_transfer_id: str | None = None,
    ) -> int:
        return sum(
            transfer.to_steward_id == steward_id
            and transfer.status is TransferStatus.PENDING_ACCEPTANCE
            and transfer.model_id != excluding_model_id
            and transfer.transfer_id != excluding_transfer_id
            for transfer in self._transfers.values()
        )

    def _is_eligible(self, steward: Steward, model: ModelOwnership) -> bool:
        reserved = self._reserved_load(
            steward.steward_id,
            excluding_model_id=model.model_id,
        )
        return (
            steward.active
            and steward.available
            and steward.steward_id != model.current_steward_id
            and model.required_capabilities.issubset(steward.capabilities)
            and self._active_load(steward.steward_id) + reserved < steward.max_active_models
        )

    def _require_operator(self, actor_id: str) -> str:
        actor = self._required_text(actor_id, "actor_id")
        if actor not in self._governance_operators:
            raise OwnershipError("operation requires an authorized governance operator")
        return actor

    def register_steward(self, steward: Steward, *, now: float) -> None:
        """Register a person/team principal during trusted system provisioning."""
        if not isinstance(steward, Steward):
            raise TypeError("steward must be a Steward")
        timestamp = self._timestamp(now)
        steward_id = self._required_text(steward.steward_id, "steward_id")
        if steward_id == "__unassigned__":
            raise OwnershipError("steward_id is reserved")
        if not isinstance(steward.available, bool) or not isinstance(steward.active, bool):
            raise OwnershipError("available and active must be booleans")
        if steward_id in self._stewards:
            raise OwnershipError(f"steward already registered: {steward_id}")
        if not isinstance(steward.kind, StewardKind):
            raise OwnershipError("kind must be a StewardKind")
        if not isinstance(steward.capabilities, frozenset) or any(
            not isinstance(item, str) or not item.strip() for item in steward.capabilities
        ):
            raise OwnershipError("capabilities must be a frozenset of non-empty strings")
        if (
            isinstance(steward.max_active_models, bool)
            or not isinstance(steward.max_active_models, int)
            or steward.max_active_models < 1
        ):
            raise OwnershipError("max_active_models must be a positive integer")
        self._stewards[steward_id] = replace(steward, steward_id=steward_id)
        self._record_event(
            "steward_registered",
            "system",
            timestamp,
            steward_id,
            kind=steward.kind.value,
            max_active_models=steward.max_active_models,
        )

    def register_model(
        self,
        model_id: str,
        *,
        current_steward_id: str | None,
        required_capabilities: Iterable[str],
        safety_tier: str = "standard",
        now: float,
    ) -> ModelOwnership:
        """Register a deployment; unassigned deployments start restricted."""
        timestamp = self._timestamp(now)
        key = self._required_text(model_id, "model_id")
        if key in self._models:
            raise OwnershipError(f"model deployment already registered: {key}")
        requirements = frozenset(
            self._required_text(value, "required capability") for value in required_capabilities
        )
        tier = self._required_text(safety_tier, "safety_tier")
        if current_steward_id is None:
            record = ModelOwnership(key, None, requirements, tier, OwnershipStatus.UNASSIGNED)
        else:
            steward_key = self._required_text(current_steward_id, "current_steward_id")
            steward = self._stewards.get(steward_key)
            if steward is None or not steward.active or not steward.available:
                raise OwnershipError("initial steward must be registered, active, and available")
            if not requirements.issubset(steward.capabilities):
                raise OwnershipError("initial steward lacks required capabilities")
            committed_and_reserved = self._active_load(steward_key) + self._reserved_load(
                steward_key
            )
            if committed_and_reserved >= steward.max_active_models:
                raise OwnershipError("initial steward has reached model capacity")
            record = ModelOwnership(key, steward_key, requirements, tier, OwnershipStatus.ACTIVE)
        self._models[key] = record
        self._record_event(
            "model_registered",
            "system",
            timestamp,
            key,
            steward_id=record.current_steward_id or "none",
            status=record.status.value,
            safety_tier=tier,
        )
        return record

    def eligible_successors(self, model_id: str) -> tuple[Steward, ...]:
        """Return eligible successors sorted by current load, then stable ID."""
        model = self.get_model(model_id)
        declined = {
            transfer.to_steward_id
            for transfer in self._transfers.values()
            if transfer.model_id == model.model_id
            and transfer.status is TransferStatus.DECLINED
        }
        candidates = [
            steward
            for steward in self._stewards.values()
            if self._is_eligible(steward, model) and steward.steward_id not in declined
        ]
        return tuple(
            sorted(
                candidates,
                key=lambda item: (self._active_load(item.steward_id), item.steward_id),
            )
        )

    def flag_steward_unavailable(
        self,
        steward_id: str,
        *,
        actor_id: str,
        reason: str,
        now: float,
    ) -> tuple[str, ...]:
        """Mark a person/team unavailable and restrict every deployment they own."""
        actor = self._require_operator(actor_id)
        timestamp = self._timestamp(now)
        key = self._required_text(steward_id, "steward_id")
        explanation = self._required_text(reason, "reason")
        steward = self._stewards.get(key)
        if steward is None:
            raise OwnershipError(f"unknown steward: {key}")
        if not steward.available:
            return ()
        self._stewards[key] = replace(steward, available=False)
        affected: list[str] = []
        for model_id, model in tuple(self._models.items()):
            if model.current_steward_id == key and model.status is not OwnershipStatus.UNASSIGNED:
                self._models[model_id] = replace(model, status=OwnershipStatus.TRANSFER_REQUIRED)
                affected.append(model_id)
        for transfer_id, transfer in tuple(self._transfers.items()):
            if (
                transfer.status is TransferStatus.PENDING_ACCEPTANCE
                and transfer.to_steward_id == key
            ):
                self._transfers[transfer_id] = replace(
                    transfer, status=TransferStatus.CANCELLED, resolved_at=timestamp
                )
                self._record_event(
                    "transfer_cancelled",
                    actor,
                    timestamp,
                    transfer_id,
                    reason="receiving_steward_unavailable",
                )
        self._record_event(
            "steward_unavailable",
            actor,
            timestamp,
            key,
            reason=explanation,
            affected_models=",".join(sorted(affected)),
        )
        return tuple(sorted(affected))

    def reassign_all_owned_models(
        self,
        steward_id: str,
        *,
        actor_id: str,
        reason: str,
        now: float,
    ) -> tuple[tuple[str, TransferRequest | None], ...]:
        """Fail closed and start a handoff for every model assigned to a steward.

        Existing pending handoffs are preserved rather than duplicated. New
        successors are selected by capability fit, active load, pending capacity
        reservations, and a stable ID tie-break. Receivers must still accept.
        """
        actor = self._require_operator(actor_id)
        timestamp = self._timestamp(now)
        key = self._required_text(steward_id, "steward_id")
        explanation = self._required_text(reason, "reason")
        affected = self.flag_steward_unavailable(
            key,
            actor_id=actor,
            reason=explanation,
            now=timestamp,
        )
        if not affected:
            affected = tuple(
                model.model_id
                for model in self._models.values()
                if model.current_steward_id == key
                and model.status is OwnershipStatus.TRANSFER_REQUIRED
            )
        results: list[tuple[str, TransferRequest | None]] = []
        for model_id in sorted(affected):
            pending = next(
                (
                    transfer
                    for transfer in self._transfers.values()
                    if transfer.model_id == model_id
                    and transfer.from_steward_id == key
                    and transfer.status is TransferStatus.PENDING_ACCEPTANCE
                ),
                None,
            )
            if pending is not None:
                results.append((model_id, pending))
                continue
            request = self.begin_reassignment(
                model_id,
                actor_id=actor,
                reason=explanation,
                now=timestamp,
            )
            results.append((model_id, request))
        return tuple(results)

    def request_transfer(
        self,
        model_id: str,
        to_steward_id: str,
        *,
        requested_by: str,
        reason: str,
        now: float,
    ) -> TransferRequest:
        """Create a pending handoff; it is not active until receiver acceptance."""
        model = self.get_model(model_id)
        actor = self._required_text(requested_by, "requested_by")
        explanation = self._required_text(reason, "reason")
        target_id = self._required_text(to_steward_id, "to_steward_id")
        source_id = model.current_steward_id
        if source_id is None or model.status is OwnershipStatus.UNASSIGNED:
            raise OwnershipError("unassigned deployments require a new assignment workflow")
        if actor != source_id and actor not in self._governance_operators:
            raise OwnershipError(
                "only the current steward or a governance operator may request transfer"
            )
        target = self._stewards.get(target_id)
        if target is None or not self._is_eligible(target, model):
            raise OwnershipError("receiving steward is unavailable, ineligible, or at capacity")
        timestamp = self._timestamp(now)
        for transfer_id, previous in tuple(self._transfers.items()):
            if (
                previous.model_id == model.model_id
                and previous.status is TransferStatus.PENDING_ACCEPTANCE
            ):
                self._transfers[transfer_id] = replace(
                    previous, status=TransferStatus.SUPERSEDED, resolved_at=timestamp
                )
                self._record_event(
                    "transfer_superseded",
                    actor,
                    timestamp,
                    transfer_id,
                    replacement_steward=target_id,
                )
        transfer_id = str(uuid4())
        request = TransferRequest(
            transfer_id=transfer_id,
            model_id=model.model_id,
            from_steward_id=source_id,
            to_steward_id=target_id,
            requested_by=actor,
            reason=explanation,
            created_at=timestamp,
        )
        self._transfers[transfer_id] = request
        self._models[model.model_id] = replace(model, status=OwnershipStatus.TRANSFER_REQUIRED)
        self._record_event(
            "transfer_requested",
            actor,
            timestamp,
            transfer_id,
            model_id=model.model_id,
            from_steward=source_id,
            to_steward=target_id,
            reason=explanation,
        )
        return request

    def begin_reassignment(
        self,
        model_id: str,
        *,
        actor_id: str,
        reason: str,
        now: float,
    ) -> TransferRequest | None:
        """Choose the least-loaded eligible successor, but never auto-accept.

        If there is no eligible receiver, move the deployment to UNASSIGNED so
        privileged actions remain blocked until a qualified steward is appointed.
        """
        actor = self._require_operator(actor_id)
        timestamp = self._timestamp(now)
        explanation = self._required_text(reason, "reason")
        model = self.get_model(model_id)
        if model.current_steward_id is None:
            raise OwnershipError("model deployment is already unassigned")
        self._models[model.model_id] = replace(model, status=OwnershipStatus.TRANSFER_REQUIRED)
        self._record_event(
            "transfer_required",
            actor,
            timestamp,
            model.model_id,
            reason=explanation,
        )
        candidates = self.eligible_successors(model.model_id)
        if not candidates:
            self.place_unassigned(
                model.model_id,
                actor_id=actor,
                reason="no eligible successor: " + explanation,
                now=timestamp,
            )
            return None
        return self.request_transfer(
            model.model_id,
            candidates[0].steward_id,
            requested_by=actor,
            reason=explanation,
            now=timestamp,
        )

    def request_assignment(
        self,
        model_id: str,
        to_steward_id: str,
        *,
        actor_id: str,
        reason: str,
        now: float,
    ) -> TransferRequest:
        """Propose a first steward for an unassigned deployment.

        Only governance operators may initiate assignment. The receiving
        principal must still explicitly accept before privileged actions resume.
        """
        actor = self._require_operator(actor_id)
        timestamp = self._timestamp(now)
        explanation = self._required_text(reason, "reason")
        model = self.get_model(model_id)
        if model.status is not OwnershipStatus.UNASSIGNED or model.current_steward_id is not None:
            raise OwnershipError("assignment is only valid for an unassigned deployment")
        target_id = self._required_text(to_steward_id, "to_steward_id")
        target = self._stewards.get(target_id)
        if target is None or not self._is_eligible(target, model):
            raise OwnershipError("receiving steward is unavailable, ineligible, or at capacity")
        for transfer_id, previous in tuple(self._transfers.items()):
            if (
                previous.model_id == model.model_id
                and previous.status is TransferStatus.PENDING_ACCEPTANCE
            ):
                self._transfers[transfer_id] = replace(
                    previous, status=TransferStatus.SUPERSEDED, resolved_at=timestamp
                )
                self._record_event(
                    "assignment_superseded",
                    actor,
                    timestamp,
                    transfer_id,
                    replacement_steward=target_id,
                )
        transfer_id = str(uuid4())
        request = TransferRequest(
            transfer_id=transfer_id,
            model_id=model.model_id,
            from_steward_id="__unassigned__",
            to_steward_id=target_id,
            requested_by=actor,
            reason=explanation,
            created_at=timestamp,
        )
        self._transfers[transfer_id] = request
        self._record_event(
            "assignment_requested",
            actor,
            timestamp,
            transfer_id,
            model_id=model.model_id,
            to_steward=target_id,
            reason=request.reason,
        )
        return request

    def accept_transfer(
        self,
        transfer_id: str,
        *,
        actor_id: str,
        now: float,
    ) -> ModelOwnership:
        """Complete handoff only when the designated receiver explicitly accepts."""
        actor = self._required_text(actor_id, "actor_id")
        timestamp = self._timestamp(now)
        transfer = self.get_transfer(transfer_id)
        if transfer.status is not TransferStatus.PENDING_ACCEPTANCE:
            raise OwnershipError("transfer is not pending acceptance")
        if actor != transfer.to_steward_id:
            raise OwnershipError("only the designated receiving steward may accept")
        target = self._stewards.get(actor)
        if target is None or not target.active or not target.available:
            raise OwnershipError("receiving steward is no longer active and available")
        model = self.get_model(transfer.model_id)
        expected_source = (
            None if transfer.from_steward_id == "__unassigned__" else transfer.from_steward_id
        )
        source_matches = model.current_steward_id == expected_source
        assignment_matches = (
            transfer.from_steward_id != "__unassigned__"
            or model.status is OwnershipStatus.UNASSIGNED
        )
        if not source_matches or not assignment_matches:
            self._transfers[transfer_id] = replace(
                transfer, status=TransferStatus.SUPERSEDED, resolved_at=timestamp
            )
            self._record_event(
                "transfer_superseded",
                actor,
                timestamp,
                transfer_id,
                reason="source_ownership_changed",
            )
            raise OwnershipError("source stewardship changed; transfer was superseded")
        if not model.required_capabilities.issubset(target.capabilities):
            raise OwnershipError("receiving steward no longer meets required capabilities")
        reserved = self._reserved_load(actor, excluding_transfer_id=transfer_id)
        if self._active_load(actor) + reserved >= target.max_active_models:
            raise OwnershipError("receiving steward has reached model capacity")
        updated = replace(
            model,
            current_steward_id=actor,
            status=OwnershipStatus.ACTIVE,
        )
        self._models[model.model_id] = updated
        self._transfers[transfer_id] = replace(
            transfer, status=TransferStatus.ACCEPTED, resolved_at=timestamp
        )
        self._record_event(
            "transfer_accepted",
            actor,
            timestamp,
            transfer_id,
            model_id=model.model_id,
            previous_steward=transfer.from_steward_id,
            new_steward=actor,
        )
        return updated

    def decline_transfer(
        self,
        transfer_id: str,
        *,
        actor_id: str,
        reason: str,
        now: float,
    ) -> TransferRequest:
        """Allow a receiving person/team to refuse responsibility."""
        actor = self._required_text(actor_id, "actor_id")
        timestamp = self._timestamp(now)
        explanation = self._required_text(reason, "reason")
        transfer = self.get_transfer(transfer_id)
        if transfer.status is not TransferStatus.PENDING_ACCEPTANCE:
            raise OwnershipError("transfer is not pending acceptance")
        if actor != transfer.to_steward_id:
            raise OwnershipError("only the designated receiving steward may decline")
        updated = replace(
            transfer,
            status=TransferStatus.DECLINED,
            resolved_at=timestamp,
        )
        self._transfers[transfer_id] = updated
        self._record_event(
            "transfer_declined",
            actor,
            timestamp,
            transfer_id,
            reason=explanation,
        )
        return updated

    def place_unassigned(
        self,
        model_id: str,
        *,
        actor_id: str,
        reason: str,
        now: float,
    ) -> ModelOwnership:
        """Remove active stewardship and keep the deployment in restricted state."""
        actor = self._require_operator(actor_id)
        timestamp = self._timestamp(now)
        explanation = self._required_text(reason, "reason")
        model = self.get_model(model_id)
        updated = replace(
            model,
            current_steward_id=None,
            status=OwnershipStatus.UNASSIGNED,
        )
        self._models[model.model_id] = updated
        for transfer_id, transfer in tuple(self._transfers.items()):
            if (
                transfer.model_id == model.model_id
                and transfer.status is TransferStatus.PENDING_ACCEPTANCE
            ):
                self._transfers[transfer_id] = replace(
                    transfer, status=TransferStatus.CANCELLED, resolved_at=timestamp
                )
                self._record_event(
                    "transfer_cancelled",
                    actor,
                    timestamp,
                    transfer_id,
                    reason="model_unassigned",
                )
        self._record_event(
            "model_unassigned",
            actor,
            timestamp,
            model.model_id,
            previous_steward=model.current_steward_id or "none",
            reason=explanation,
        )
        return updated

    def privileged_actions_allowed(self, model_id: str) -> bool:
        """Return false unless a deployment has an active, available steward."""
        model = self.get_model(model_id)
        if model.status is not OwnershipStatus.ACTIVE or model.current_steward_id is None:
            return False
        steward = self._stewards.get(model.current_steward_id)
        return bool(steward and steward.active and steward.available)

    def verify_audit_chain(self) -> bool:
        """Check sequence, previous hashes, and event hashes for the local history."""
        previous_hash = "0" * 64
        for index, event in enumerate(self._events, start=1):
            if event.sequence != index or event.previous_hash != previous_hash:
                return False
            payload = {
                "sequence": event.sequence,
                "event_type": event.event_type,
                "actor_id": event.actor_id,
                "occurred_at": event.occurred_at,
                "subject_id": event.subject_id,
                "details": dict(event.details),
                "previous_hash": event.previous_hash,
            }
            encoded = json.dumps(
                payload,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
            digest = hashlib.sha256(encoded).hexdigest()
            if digest != event.event_hash:
                return False
            previous_hash = event.event_hash
        return True

    def export_audit_jsonl(self) -> str:
        """Export events for external append-only storage or independent review."""
        lines = []
        for event in self._events:
            payload = asdict(event)
            payload["details"] = dict(event.details)
            lines.append(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        return "\n".join(lines) + ("\n" if lines else "")
