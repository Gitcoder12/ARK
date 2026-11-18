from __future__ import annotations

from ark.world import ARKWorld, Zone, create_world


def test_arkworld_is_the_canonical_world_alias() -> None:
    world = create_world(seed=17)
    assert isinstance(world, ARKWorld)
    assert world.to_dict()["world"] == "ARKWorld"


def test_arkworld_namespace_exposes_the_seven_world_zones() -> None:
    world = create_world()
    assert len(world.agents) == 6
    assert len(list(Zone)) == 7
