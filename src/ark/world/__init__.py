"""Canonical ARKWorld API for the digital commons simulation."""

from ark.robopia.core import (
    Agent,
    EventKind,
    RobopiaWorld,
    Zone,
    advance_tick,
    create_demo_world,
    demo_report,
    move_agent,
    run_simulation,
    world_metrics,
)

ARKWorld = RobopiaWorld
create_world = create_demo_world

__all__ = [
    "ARKWorld",
    "Agent",
    "EventKind",
    "RobopiaWorld",
    "Zone",
    "advance_tick",
    "create_demo_world",
    "create_world",
    "demo_report",
    "move_agent",
    "run_simulation",
    "world_metrics",
]
