"""Strategic failure analysis and fault-tolerant agent-group simulation.

This module is a deterministic research prototype. Agent roles are simulated unless
an application supplies real provider adapters in a future integration.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Iterable


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Decision(str, Enum):
    PROCEED = "proceed"
    REVISE = "revise"
    RESTRICTED = "restricted"
    PAUSE_REVIEW = "pause_for_review"
    STOP_REVIEW = "stop_external_review"


@dataclass(frozen=True)
class PlanStep:
    name: str
    description: str = ""
    dependencies: tuple[str, ...] = ()


@dataclass(frozen=True)
class StrategicPlan:
    name: str
    objective: str
    steps: tuple[PlanStep, ...]
    resources: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    stakeholders: tuple[str, ...] = ()
    contingencies: tuple[str, ...] = ()
    milestones: tuple[str, ...] = ()
    continuity_owner: str | None = None
    risk_level: Severity = Severity.MEDIUM
    context: tuple[str, ...] = ()


@dataclass(frozen=True)
class RiskFinding:
    code: str
    title: str
    severity: Severity
    explanation: str
    mitigation: str


@dataclass(frozen=True)
class PremortemResult:
    plan_name: str
    findings: tuple[RiskFinding, ...]
    assumptions_to_test: tuple[str, ...]
    recommended_decision: Decision

    @property
    def risk_count(self) -> int:
        return len(self.findings)


class PremortemEngine:
    """Rule-based pre-mortem; findings are prompts for review, not predictions."""

    def analyse(self, plan: StrategicPlan) -> PremortemResult:
        findings: list[RiskFinding] = []
        assumptions: list[str] = []

        if not plan.resources:
            findings.append(RiskFinding(
                "RESOURCE_BUDGET_MISSING", "Resource plan is missing", Severity.HIGH,
                "The plan does not specify the people, supplies, compute, time, or budget it needs.",
                "Estimate resource demand, reserves, replenishment and hard limits before execution.",
            ))
        if not plan.constraints:
            findings.append(RiskFinding(
                "CONSTRAINTS_UNDECLARED", "Operating constraints are unclear", Severity.MEDIUM,
                "No explicit environmental, legal, technical or human constraints were supplied.",
                "Record hard constraints and conditions that require stopping or replanning.",
            ))
        if not plan.contingencies:
            findings.append(RiskFinding(
                "NO_CONTINGENCY", "No fallback route is defined", Severity.HIGH,
                "The plan has no stated alternative if a critical assumption or dependency fails.",
                "Define abort criteria, alternate routes and safe fallback states.",
            ))
        if not plan.milestones:
            findings.append(RiskFinding(
                "NO_MILESTONES", "No intermediate checkpoints", Severity.MEDIUM,
                "The plan cannot clearly distinguish progress from an unfinished objective.",
                "Add measurable milestones and evidence required to mark each one complete.",
            ))
        if not plan.stakeholders:
            findings.append(RiskFinding(
                "STAKEHOLDER_CAPACITY_UNKNOWN", "Stakeholder capacity is unknown", Severity.HIGH,
                "The plan does not identify the people or teams whose cooperation is required.",
                "Confirm capacity, consent, authority and stop rights with affected stakeholders.",
            ))
        if not plan.continuity_owner:
            findings.append(RiskFinding(
                "CONTINUITY_UNASSIGNED", "No continuity or succession owner", Severity.MEDIUM,
                "The plan does not say who maintains responsibility if its owner becomes unavailable.",
                "Assign a qualified successor and require an explicit, auditable handoff.",
            ))
        if len(plan.steps) > 1:
            known = {step.name for step in plan.steps}
            for step in plan.steps:
                missing = [dep for dep in step.dependencies if dep not in known]
                if missing:
                    findings.append(RiskFinding(
                        "MISSING_DEPENDENCY", f"Unresolved dependency for {step.name}",
                        Severity.HIGH,
                        f"Dependencies are not represented as plan steps: {', '.join(missing)}.",
                        "Add the missing steps or correct the dependency references.",
                    ))
                    break
        if plan.risk_level in (Severity.HIGH, Severity.CRITICAL) and not plan.context:
            findings.append(RiskFinding(
                "HIGH_RISK_CONTEXT_THIN", "High-risk plan lacks supporting context",
                Severity.HIGH,
                "A high-risk objective was submitted without evidence or context references.",
                "Attach source evidence, uncertainty notes and independent review before action.",
            ))

        assumptions.extend((
            "The objective is still valid and has not been superseded.",
            "Resource estimates reflect current conditions, not optimistic best cases.",
            "Dependencies and stakeholder commitments are available when needed.",
            "The plan can be paused without causing uncontrolled side effects.",
        ))
        if not findings:
            decision = Decision.PROCEED
        elif any(item.severity in (Severity.HIGH, Severity.CRITICAL) for item in findings):
            decision = Decision.REVISE
        else:
            decision = Decision.PROCEED
        return PremortemResult(plan.name, tuple(findings), tuple(assumptions), decision)


ROLE_ORDER = ("coordinator", "researcher", "executor", "critic", "validator")
CRITICAL_ROLES = frozenset(("coordinator", "executor", "validator"))
HIGH_RISK_ROLES = frozenset(("critic", "validator"))


@dataclass
class Agent:
    agent_id: str
    role: str
    capabilities: tuple[str, ...] = ()
    backup: bool = False
    available: bool = True
    failure_count: int = 0

    def can_cover(self, role: str) -> bool:
        return role == self.role or role in self.capabilities


@dataclass(frozen=True)
class AgentEvent:
    event: str
    role: str
    agent_id: str | None
    detail: str


@dataclass(frozen=True)
class GroupResult:
    decision: Decision
    active_agents: tuple[str, ...]
    replacements: tuple[str, ...]
    uncovered_roles: tuple[str, ...]
    events: tuple[AgentEvent, ...]
    external_review_report: str | None
    simulated: bool = True


def default_agents() -> tuple[list[Agent], list[Agent]]:
    active = [
        Agent("agent-coordinator", "coordinator", ("researcher",)),
        Agent("agent-researcher", "researcher"),
        Agent("agent-executor", "executor"),
        Agent("agent-critic", "critic", ("validator",)),
        Agent("agent-validator", "validator", ("researcher",)),
    ]
    backups = [
        Agent("backup-coordinator", "coordinator", ("researcher",), backup=True),
        Agent("backup-researcher", "researcher", ("critic",), backup=True),
        Agent("backup-executor", "executor", backup=True),
        Agent("backup-critic", "critic", ("validator",), backup=True),
        Agent("backup-validator", "validator", ("researcher",), backup=True),
    ]
    return active, backups


class AgentGroup:
    """Five-role team with role-matched backups and explicit degraded-mode rules."""

    def __init__(
        self,
        active: Iterable[Agent] | None = None,
        backups: Iterable[Agent] | None = None,
    ) -> None:
        default_active, default_backups = default_agents()
        self.active = list(active if active is not None else default_active)
        self.backups = list(backups if backups is not None else default_backups)

    def run(
        self,
        plan: StrategicPlan,
        *,
        fail_roles: Iterable[str] = (),
        invalid_roles: Iterable[str] = (),
        fail_backup_roles: Iterable[str] = (),
    ) -> GroupResult:
        failed = set(fail_roles)
        invalid = set(invalid_roles)
        failed_backups = set(fail_backup_roles)
        events: list[AgentEvent] = []
        replacements: list[str] = []
        unavailable_roles: set[str] = set()

        for role in ROLE_ORDER:
            agent = next((item for item in self.active if item.available and item.role == role), None)
            if agent is None:
                continue
            if role not in failed and role not in invalid:
                events.append(AgentEvent("completed", role, agent.agent_id,
                                         "Simulated role completed its assigned stage."))
                continue

            reason = "simulated crash" if role in failed else "invalid output"
            agent.available = False
            agent.failure_count += 1
            events.append(AgentEvent("agent_failed", role, agent.agent_id, reason))
            backup = next(
                (item for item in self.backups
                 if item.available and item.role == role and role not in failed_backups),
                None,
            )
            if backup is not None:
                backup.available = False
                self.active.append(backup)
                replacements.append(backup.agent_id)
                events.append(AgentEvent(
                    "backup_replaced", role, backup.agent_id,
                    f"Role restored after {reason}; prior work must be checkpoint-verified.",
                ))
            else:
                unavailable_roles.add(role)
                events.append(AgentEvent(
                    "replacement_unavailable", role, None,
                    "No healthy role-matched backup remains.",
                ))

        healthy = [agent for agent in self.active if agent.available]
        uncovered = tuple(
            role for role in ROLE_ORDER
            if not any(agent.can_cover(role) for agent in healthy)
        )
        critical_missing = set(uncovered) & set(CRITICAL_ROLES)
        if plan.risk_level in (Severity.HIGH, Severity.CRITICAL):
            critical_missing |= set(uncovered) & set(HIGH_RISK_ROLES)

        if not healthy:
            decision = Decision.STOP_REVIEW
        elif critical_missing:
            decision = Decision.PAUSE_REVIEW
        elif len(healthy) <= 2:
            decision = Decision.RESTRICTED
        elif unavailable_roles or uncovered:
            decision = Decision.RESTRICTED
        else:
            decision = Decision.PROCEED

        report = None
        if decision in (Decision.PAUSE_REVIEW, Decision.STOP_REVIEW):
            report = self._external_report(plan, decision, healthy, uncovered, events)
        return GroupResult(
            decision=decision,
            active_agents=tuple(agent.agent_id for agent in healthy),
            replacements=tuple(replacements),
            uncovered_roles=uncovered,
            events=tuple(events),
            external_review_report=report,
        )

    @staticmethod
    def _external_report(
        plan: StrategicPlan,
        decision: Decision,
        healthy: list[Agent],
        uncovered: tuple[str, ...],
        events: list[AgentEvent],
    ) -> str:
        lines = [
            f"# External Review Report: {plan.name}",
            "",
            f"- Generated: {datetime.now(timezone.utc).isoformat()}",
            f"- Decision: {decision.value}",
            f"- Objective: {plan.objective}",
            f"- Healthy agents remaining: {len(healthy)}",
            f"- Remaining agents: {', '.join(agent.agent_id for agent in healthy) or 'none'}",
            f"- Uncovered roles: {', '.join(uncovered) or 'none'}",
            "",
            "## Event history",
        ]
        lines.extend(
            f"- {event.event}: role={event.role}, agent={event.agent_id or 'none'} — {event.detail}"
            for event in events
        )
        lines.extend((
            "",
            "## Required human review",
            "- Verify the last trusted checkpoint and all side effects.",
            "- Confirm completed work independently; do not rely only on agent self-reports.",
            "- Decide whether to resume, reduce scope, reassign roles or abandon the task.",
            "- Restore capacity and re-authorize execution before continuing.",
            "",
            "This report is generated from a deterministic simulation. It is not proof of real-world actions.",
        ))
        return "\n".join(lines)


def result_to_dict(result: PremortemResult | GroupResult) -> dict:
    """Convert results into JSON-friendly dictionaries."""
    return asdict(result)


__all__ = [
    "Agent", "AgentGroup", "Decision", "GroupResult", "PlanStep",
    "PremortemEngine", "PremortemResult", "RiskFinding", "Severity",
    "StrategicPlan", "default_agents", "result_to_dict",
]
