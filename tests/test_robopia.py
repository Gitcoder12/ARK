from __future__ import annotations

import pytest

from ark.robopia import (
    EventKind,
    Zone,
    advance_tick,
    create_demo_world,
    move_agent,
    run_simulation,
    world_metrics,
)


def test_demo_world_has_six_agents_and_seven_zones() -> None:
    world = create_demo_world()
    assert len(world.agents) == 6
    assert {zone.value for zone in Zone} == {
        "commons", "workshop", "gardens", "laboratory",
        "assembly", "sanctuary", "archive",
    }


def test_simulation_is_reproducible_for_same_seed() -> None:
    first = run_simulation(create_demo_world(23), 12)
    second = run_simulation(create_demo_world(23), 12)
    assert first.to_dict() == second.to_dict()


def test_role_based_zone_access_blocks_unauthorized_entry() -> None:
    world = create_demo_world()
    assert move_agent(world, "a1", Zone.WORKSHOP)
    assert not move_agent(world, "a1", Zone.SANCTUARY)
    assert world.safety_interventions == 1
    assert world.events[-1].kind is EventKind.ACCESS_BLOCKED


def test_fair_share_rule_caps_large_compute_request() -> None:
    world = create_demo_world()
    advance_tick(world)
    advance_tick(world)
    advance_tick(world)
    request_events = [
        event for event in world.events if event.kind is EventKind.RESOURCE_REQUEST
    ]
    assert len(request_events) == 1
    assert "granted 2" in request_events[0].detail
    assert world.conflicts_raised == 1
    assert world.conflicts_resolved == 1


def test_resources_never_become_negative_and_projects_complete() -> None:
    world = run_simulation(create_demo_world(), 20)
    assert all(amount >= 0 for amount in world.resources.values())
    assert world.completed_projects == {"safe_lab", "green_roof", "open_archive"}


def test_metrics_stay_in_expected_ranges() -> None:
    metrics = world_metrics(run_simulation(create_demo_world(), 8))
    for key in (
        "cooperation_rate",
        "resource_use_balance",
        "fair_share_compliance",
        "project_completion",
    ):
        assert 0.0 <= metrics[key] <= 1.0
    assert metrics["conflicts_raised"] == metrics["conflicts_resolved"]


@pytest.mark.parametrize("ticks", [0, -1, 1001])
def test_run_rejects_out_of_range_tick_counts(ticks: int) -> None:
    with pytest.raises(ValueError):
        run_simulation(create_demo_world(), ticks)


def test_run_rejects_boolean_tick_count() -> None:
    with pytest.raises(TypeError):
        run_simulation(create_demo_world(), True)
