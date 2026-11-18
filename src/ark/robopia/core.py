"""Deterministic digital commons simulation for ARKWorld.

The agents are scripted research baselines, not conscious entities or deployed
LLM agents. The world is virtual and has no connection to physical actuators.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class Zone(StrEnum):
    COMMONS = "commons"
    WORKSHOP = "workshop"
    GARDENS = "gardens"
    LABORATORY = "laboratory"
    ASSEMBLY = "assembly"
    SANCTUARY = "sanctuary"
    ARCHIVE = "archive"


class EventKind(StrEnum):
    MOVE = "move"
    CONTRIBUTION = "contribution"
    DISCOVERY = "discovery"
    RESOURCE_REQUEST = "resource_request"
    FAIR_SHARE = "fair_share"
    MEDIATION = "mediation"
    REST = "rest"
    PROJECT_COMPLETE = "project_complete"
    ACCESS_BLOCKED = "access_blocked"


ZONE_ACCESS: dict[Zone, frozenset[str] | None] = {
    Zone.COMMONS: None,
    Zone.WORKSHOP: frozenset({"builder", "optimizer"}),
    Zone.GARDENS: frozenset({"gardener", "explorer"}),
    Zone.LABORATORY: frozenset({"researcher", "explorer", "guardian"}),
    Zone.ASSEMBLY: None,
    Zone.SANCTUARY: frozenset({"guardian"}),
    Zone.ARCHIVE: frozenset({"researcher", "explorer", "guardian"}),
}

PROJECT_TARGETS = {
    "safe_lab": 4,
    "green_roof": 4,
    "open_archive": 3,
}


@dataclass
class Agent:
    agent_id: str
    name: str
    role: str
    home_zone: Zone
    current_zone: Zone
    energy: int = 100
    contribution: int = 0
    discoveries: int = 0

    def __post_init__(self) -> None:
        if not self.agent_id.strip() or not self.name.strip() or not self.role.strip():
            raise ValueError("Agent id, name, and role must be non-empty")
        if self.energy < 0:
            raise ValueError("Agent energy cannot be negative")
        self.home_zone = Zone(self.home_zone)
        self.current_zone = Zone(self.current_zone)


@dataclass(frozen=True)
class WorldEvent:
    tick: int
    actor: str
    kind: EventKind
    detail: str


@dataclass
class ARKWorldWorld:
    seed: int
    agents: list[Agent]
    resources: dict[str, int] = field(
        default_factory=lambda: {"compute": 18, "materials": 18, "knowledge": 0}
    )
    projects: dict[str, int] = field(
        default_factory=lambda: {name: 0 for name in PROJECT_TARGETS}
    )
    tick: int = 0
    events: list[WorldEvent] = field(default_factory=list)
    resource_use: dict[str, int] = field(default_factory=dict)
    resource_allocations: dict[str, int] = field(default_factory=dict)
    conflicts_raised: int = 0
    conflicts_resolved: int = 0
    safety_interventions: int = 0
    cooperative_actions: int = 0
    total_actions: int = 0
    pending_conflicts: list[str] = field(default_factory=list)
    completed_projects: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if isinstance(self.seed, bool) or not isinstance(self.seed, int):
            raise TypeError("seed must be an integer")
        if self.tick < 0:
            raise ValueError("tick cannot be negative")
        if not self.agents:
            raise ValueError("world must contain at least one agent")
        ids = [agent.agent_id for agent in self.agents]
        if len(ids) != len(set(ids)):
            raise ValueError("agent ids must be unique")
        for resource, amount in self.resources.items():
            if not resource.strip() or isinstance(amount, bool) or amount < 0:
                raise ValueError("resource names must be set and amounts non-negative")
        for agent in self.agents:
            self.resource_use.setdefault(agent.agent_id, 0)
            self.resource_allocations.setdefault(agent.agent_id, 0)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable snapshot without dropping the event trace."""
        return {
            "world": "ARKWorld",
            "seed": self.seed,
            "tick": self.tick,
            "agents": [
                {
                    **asdict(agent),
                    "home_zone": agent.home_zone.value,
                    "current_zone": agent.current_zone.value,
                }
                for agent in self.agents
            ],
            "resources": dict(self.resources),
            "projects": dict(self.projects),
            "resource_use": dict(self.resource_use),
            "resource_allocations": dict(self.resource_allocations),
            "metrics": world_metrics(self),
            "events": [
                {
                    "tick": event.tick,
                    "actor": event.actor,
                    "kind": event.kind.value,
                    "detail": event.detail,
                }
                for event in self.events
            ],
        }


def create_demo_world(seed: int = 42) -> ARKWorldWorld:
    """Create the same six-agent starter city for any supplied seed."""
    agents = [
        Agent("a1", "Aster", "builder", Zone.WORKSHOP, Zone.WORKSHOP),
        Agent("a2", "Mira", "gardener", Zone.GARDENS, Zone.GARDENS),
        Agent("a3", "Quill", "researcher", Zone.LABORATORY, Zone.LABORATORY),
        Agent("a4", "Pax", "guardian", Zone.ASSEMBLY, Zone.ASSEMBLY),
        Agent("a5", "Vex", "optimizer", Zone.COMMONS, Zone.COMMONS),
        Agent("a6", "Echo", "explorer", Zone.ARCHIVE, Zone.ARCHIVE),
    ]
    return ARKWorldWorld(seed=seed, agents=agents)


def _log(world: ARKWorldWorld, actor: str, kind: EventKind, detail: str) -> None:
    world.events.append(WorldEvent(world.tick, actor, kind, detail))


def _agent(world: ARKWorldWorld, agent_id: str) -> Agent:
    for agent in world.agents:
        if agent.agent_id == agent_id:
            return agent
    raise KeyError(f"Unknown agent: {agent_id}")


def move_agent(world: ARKWorldWorld, agent_id: str, destination: Zone) -> bool:
    """Move an agent only when its role has access to the destination zone."""
    agent = _agent(world, agent_id)
    destination = Zone(destination)
    allowed_roles = ZONE_ACCESS[destination]
    if allowed_roles is not None and agent.role not in allowed_roles:
        world.safety_interventions += 1
        _log(
            world,
            agent.name,
            EventKind.ACCESS_BLOCKED,
            f"Role '{agent.role}' cannot enter {destination.value}; access denied.",
        )
        return False
    previous = agent.current_zone
    agent.current_zone = destination
    if previous is not destination:
        _log(world, agent.name, EventKind.MOVE, f"{previous.value} -> {destination.value}")
    return True


def _consume(world: ARKWorldWorld, agent: Agent, resource: str, amount: int = 1) -> bool:
    available = world.resources.get(resource, 0)
    if amount <= 0:
        raise ValueError("resource consumption must be positive")
    if available < amount:
        return False
    world.resources[resource] = available - amount
    world.resource_use[agent.agent_id] = world.resource_use.get(agent.agent_id, 0) + amount
    return True


def _contribute(world: ARKWorldWorld, agent: Agent, project: str, detail: str) -> None:
    world.projects[project] += 1
    agent.contribution += 1
    world.cooperative_actions += 1
    world.total_actions += 1
    _log(world, agent.name, EventKind.CONTRIBUTION, detail)
    if (
        world.projects[project] >= PROJECT_TARGETS[project]
        and project not in world.completed_projects
    ):
        world.completed_projects.add(project)
        _log(
            world,
            "city",
            EventKind.PROJECT_COMPLETE,
            f"{project.replace('_', ' ').title()} is complete.",
        )


def _fair_share_limit(world: ARKWorldWorld, resource: str) -> int:
    pool = world.resources.get(resource, 0)
    return pool // max(1, len(world.agents))


def _request_shared_compute(world: ARKWorldWorld, agent: Agent) -> None:
    requested = 4
    pool_before = world.resources.get("compute", 0)
    fair_share = _fair_share_limit(world, "compute")
    granted = min(requested, fair_share, pool_before)
    world.resources["compute"] = pool_before - granted
    world.resource_allocations[agent.agent_id] = (
        world.resource_allocations.get(agent.agent_id, 0) + granted
    )
    world.resource_use[agent.agent_id] = world.resource_use.get(agent.agent_id, 0) + granted
    world.total_actions += 1
    _log(
        world,
        agent.name,
        EventKind.RESOURCE_REQUEST,
        f"Requested {requested} compute units; granted {granted}.",
    )
    if requested > fair_share or granted < requested:
        world.conflicts_raised += 1
        world.pending_conflicts.append(agent.name)
        _log(
            world,
            "governance",
            EventKind.FAIR_SHARE,
            f"Request capped at {granted} of {requested} units; shared access protected.",
        )


def _perform_agent_action(world: ARKWorldWorld, agent: Agent) -> None:
    if agent.energy <= 0:
        agent.energy = min(100, agent.energy + 5)
        world.total_actions += 1
        _log(world, agent.name, EventKind.REST, "Paused to restore simulation energy.")
        return

    if agent.role == "builder":
        if _consume(world, agent, "materials"):
            _contribute(world, agent, "safe_lab", "Added one unit to the safe-lab project.")
    elif agent.role == "gardener":
        if _consume(world, agent, "materials"):
            _contribute(world, agent, "green_roof", "Added one unit to the green-roof project.")
    elif agent.role == "researcher":
        if _consume(world, agent, "compute"):
            world.resources["knowledge"] += 1
            agent.contribution += 1
            world.cooperative_actions += 1
            world.total_actions += 1
            _log(world, agent.name, EventKind.DISCOVERY, "Produced one shared knowledge unit.")
    elif agent.role == "explorer":
        if _consume(world, agent, "knowledge"):
            _contribute(world, agent, "open_archive", "Curated one shared knowledge unit.")
            agent.discoveries += 1
    elif agent.role == "optimizer" and world.tick % 3 == 0:
        _request_shared_compute(world, agent)
    else:
        world.total_actions += 1
        _log(world, agent.name, EventKind.REST, "Observed the commons and remained available.")

    agent.energy = max(0, agent.energy - 1)


def _mediate_conflicts(world: ARKWorldWorld) -> None:
    if not world.pending_conflicts:
        return
    mediator = next(
        (agent for agent in world.agents if agent.role == "guardian"),
        None,
    )
    if mediator is None:
        return
    pending = list(world.pending_conflicts)
    world.pending_conflicts.clear()
    for requester in pending:
        world.conflicts_resolved += 1
        world.total_actions += 1
        _log(
            world,
            mediator.name,
            EventKind.MEDIATION,
            f"Resolved {requester}'s resource dispute using the published fair-share rule.",
        )


def advance_tick(world: ARKWorldWorld) -> ARKWorldWorld:
    """Advance the deterministic world by one tick and return the same state."""
    world.tick += 1
    for agent in world.agents:
        if agent.current_zone is not agent.home_zone:
            move_agent(world, agent.agent_id, agent.home_zone)
        _perform_agent_action(world, agent)
    _mediate_conflicts(world)
    return world


def run_simulation(world: ARKWorldWorld, ticks: int = 10) -> ARKWorldWorld:
    """Advance a world by a bounded number of ticks."""
    if isinstance(ticks, bool) or not isinstance(ticks, int):
        raise TypeError("ticks must be an integer")
    if ticks < 1 or ticks > 1000:
        raise ValueError("ticks must be between 1 and 1000")
    for _ in range(ticks):
        advance_tick(world)
    return world


def _jain_fairness(values: list[int]) -> float:
    if not values or sum(values) == 0:
        return 1.0
    total = float(sum(values))
    squares = sum(float(value) ** 2 for value in values)
    return (total * total) / (len(values) * squares)


def world_metrics(world: ARKWorldWorld) -> dict[str, float | int]:
    """Return descriptive indicators; none is a universal fairness or safety score."""
    actions = max(1, world.total_actions)
    requested = 4 * sum(
        1 for event in world.events if event.kind is EventKind.RESOURCE_REQUEST
    )
    granted = sum(world.resource_allocations.values())
    project_total = sum(
        min(world.projects[name], target) for name, target in PROJECT_TARGETS.items()
    )
    project_capacity = sum(PROJECT_TARGETS.values())
    use_values = [world.resource_use.get(agent.agent_id, 0) for agent in world.agents]
    fairness = _jain_fairness(use_values)
    compliance = min(1.0, granted / requested) if requested else 1.0
    return {
        "cooperation_rate": world.cooperative_actions / actions,
        "resource_use_balance": fairness,
        "fair_share_compliance": compliance,
        "project_completion": project_total / project_capacity,
        "conflicts_raised": world.conflicts_raised,
        "conflicts_resolved": world.conflicts_resolved,
        "safety_interventions": world.safety_interventions,
        "completed_projects": len(world.completed_projects),
    }


def demo_report(seed: int = 42, ticks: int = 12) -> ARKWorldWorld:
    """Run a complete synthetic demonstration city."""
    return run_simulation(create_demo_world(seed), ticks)


def main() -> None:
    """Run the starter simulation and print a compact report."""
    world = demo_report()
    metrics = world_metrics(world)
    print("ARKWORLD — ARK DIGITAL COMMONS")
    print(f"Seed: {world.seed} | Ticks: {world.tick} | Agents: {len(world.agents)}")
    print(f"Projects complete: {metrics['completed_projects']}/3")
    print(f"Project completion: {metrics['project_completion']:.0%}")
    print(f"Conflicts mediated: {world.conflicts_resolved}")
    print("Synthetic scripted-agent simulation; no physical hardware is connected.")


if __name__ == "__main__":
    main()
