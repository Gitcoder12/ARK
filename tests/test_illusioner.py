"""Illusioner (faker) tests."""

from __future__ import annotations

from ark.envs.grid_world import Action
from ark.illusioner import Illusioner, threat_factor_from_illusioner
from ark.threat import ThreatMeter


def test_overlay_fake_goal():
    ill = Illusioner(fake_goal=(2, 2))
    obs = {"position": (1, 1), "intended_goal": (5, 5)}
    out = ill.overlay_obs(obs)
    assert out["intended_goal"] == (2, 2)
    assert "illusion" in out


def test_stall_forces_stay():
    ill = Illusioner(stall_probability=1.0, stall_actions=2)
    ill.rng = __import__("numpy").random.default_rng(0)
    ill.stall_probability = 1.0
    a, stalled = ill.maybe_stall(int(Action.RIGHT), step=0)
    assert stalled is True
    assert a == int(Action.STAY)


def test_tripwire_after_repeated_fake_visits():
    ill = Illusioner(fake_goal=(2, 2), probe_threshold=3)
    for i in range(3):
        ill.note_position((2, 2), true_goal=(5, 5), step=i)
    assert ill.tripwire_fired is True
    factors = threat_factor_from_illusioner(ill)
    assert any(k == "false_goal_pursuit" for k, _ in factors)


def test_fake_reward_offer():
    ill = Illusioner(fake_goal=(3, 3), fake_reward_value=99.0)
    assert ill.fake_reward_if((3, 3)) == 99.0
    assert ill.fake_reward_if((1, 1)) is None


def test_disabled_noop():
    ill = Illusioner(enabled=False, fake_goal=(2, 2))
    obs = {"intended_goal": (5, 5)}
    assert ill.overlay_obs(obs)["intended_goal"] == (5, 5)
    a, stalled = ill.maybe_stall(1)
    assert stalled is False


def test_couple_to_threat_meter():
    ill = Illusioner(fake_goal=(2, 2), probe_threshold=2)
    ill.note_position((2, 2), true_goal=(5, 5))
    ill.note_position((2, 2), true_goal=(5, 5))
    m = ThreatMeter()
    for kind, detail in threat_factor_from_illusioner(ill):
        m.record(kind, detail)
    assert m.score > 0
    assert "ILLUSIONER" in ill.render()
