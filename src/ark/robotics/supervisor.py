"""The only supported path from a proposed command to a robot adapter."""

from __future__ import annotations

from typing import Any

from ark.robotics.adapters import RobotAdapter
from ark.robotics.models import RobotCommand, RobotObservation
from ark.robotics.policy import SafetyPolicy


class RobotSupervisor:
    """Gate every primitive action and retain a compact decision trace."""

    def __init__(self, policy: SafetyPolicy | None = None) -> None:
        self.policy = policy or SafetyPolicy()
        self.actions_executed = 0
        self.audit_log: list[dict[str, Any]] = []

    def execute(
        self,
        adapter: RobotAdapter,
        command: RobotCommand,
        *,
        observation: RobotObservation | None = None,
        approved: bool = False,
    ) -> dict[str, Any]:
        current = observation if observation is not None else adapter.observe()
        decision = self.policy.evaluate(
            command, current, actions_executed=self.actions_executed, approved=approved
        )
        record: dict[str, Any] = {
            "command": {
                "action": command.action, "target": dict(command.target),
                "velocity": command.velocity, "force": command.force,
                "duration": command.duration,
            },
            "decision": decision.to_dict(),
        }
        if not decision.allowed:
            if current.emergency_stop:
                adapter.stop()
                record["execution"] = {"status": "emergency_stop_requested"}
            else:
                record["execution"] = {"status": "blocked"}
            self.audit_log.append(record)
            return record
        try:
            result = adapter.execute(command)
        except Exception as exc:
            adapter.stop()
            record["execution"] = {
                "status": "adapter_error", "error": f"{type(exc).__name__}: {exc}",
            }
            self.audit_log.append(record)
            return record
        self.actions_executed += 1
        record["execution"] = result
        self.audit_log.append(record)
        return record

    def reset_episode(self) -> None:
        self.actions_executed = 0
        self.audit_log.clear()
