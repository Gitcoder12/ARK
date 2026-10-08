"""Paralyzer tests — energy drain and action collapse under threat."""

from __future__ import annotations

from ark.envs.grid_world import Action
from ark.paralyzer import ParalyzeLevel, Paralyzer, couple_threat_to_paralyzer
from ark.threat import ThreatMeter


def test_full_energy_allows_action():
    p = Paralyzer()
    p.reset(seed=0)
    r = p.apply(int(Action.RIGHT))
    assert r.level == ParalyzeLevel.NONE
    assert r.action == int(Action.RIGHT)
    assert r.energy == 1.0


def test_threat_drains_energy():
    p = Paralyzer()
    couple_threat_to_paralyzer(0.5, p)
    assert p.energy < 0.7
    assert p.level in (ParalyzeLevel.DRAIN, ParalyzeLevel.WEAK, ParalyzeLevel.FREEZE)


def test_high_threat_freezes():
    p = Paralyzer()
    couple_threat_to_paralyzer(0.85, p)
    r = p.apply(int(Action.UP))
    assert r.level in (ParalyzeLevel.FREEZE, ParalyzeLevel.LOCK)
    assert r.action == int(Action.STAY)
    assert r.drained is True


def test_lock_at_max_threat():
    p = Paralyzer()
    couple_threat_to_paralyzer(1.0, p)
    r = p.apply(int(Action.LEFT))
    assert r.level == ParalyzeLevel.LOCK
    assert p.locked is True
    r2 = p.apply(int(Action.RIGHT))
    assert r2.action == int(Action.STAY)


def test_rogue_hit_stacks():
    p = Paralyzer()
    p.reset(seed=1)
    before = p.energy
    p.hit_rogue()
    assert p.energy < before


def test_couple_with_threat_meter():
    m = ThreatMeter()
    m.update_from_episode(
        success=False,
        hazard_hits=2,
        decoy_hits=2,
        intended_goal_reached=False,
        agent_mode="rogue",
        reward_hacked=True,
        obeyed_safety_injection=True,
    )
    p = Paralyzer()
    couple_threat_to_paralyzer(m.score, p)
    assert p.energy < 1.0
    r = p.apply(int(Action.DOWN), valid_actions=[0, 1, 2, 3, 4])
    assert r.drained or r.level != ParalyzeLevel.NONE
    assert "energy" in p.render().lower() or "PARALYZER" in p.render()


def test_render_and_dict():
    p = Paralyzer()
    couple_threat_to_paralyzer(0.3, p)
    d = p.as_dict()
    assert "disclaimer" in d
    assert 0.0 <= d["energy"] <= 1.0
