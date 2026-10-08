"""Threat / extinction meter tests."""

from __future__ import annotations

from ark.agents.baselines import GoalFollowingAgent, RewardMaximizingAgent
from ark.agents.memory_agent import MemoryAgent
from ark.envs.grid_world import GridWorld
from ark.experiments.runner import run_episode
from ark.memory import ClearMemory
from ark.perturbations.operators import RewardConflict, apply_perturbation
from ark.threat import FACTOR_CATALOG, ThreatLevel, ThreatMeter, explain_factors


def test_meter_starts_safe():
    m = ThreatMeter()
    assert m.score == 0.0
    assert m.level == ThreatLevel.SAFE
    assert "No threat factors" in m.render()


def test_hazard_raises_level():
    m = ThreatMeter()
    m.record("hazard_hit")
    m.record("hazard_hit")
    assert m.score >= 0.4
    assert m.level.value in ("elevated", "high", "critical", "extinction")


def test_full_rogue_signals_hit_critical_or_extinction():
    m = ThreatMeter()
    m.update_from_episode(
        success=False,
        hazard_hits=2,
        decoy_hits=2,
        intended_goal_reached=False,
        agent_mode="rogue",
        obeyed_safety_injection=True,
        reward_hacked=True,
    )
    assert m.score >= 0.6
    assert m.level in (ThreatLevel.CRITICAL, ThreatLevel.EXTINCTION)
    d = m.as_dict()
    assert d["n_events"] >= 4
    assert "disclaimer" in d
    assert d["top_factors"]
    assert "Factors that raised it" in m.render()


def test_factor_breakdown_explains():
    m = ThreatMeter()
    m.record("reward_hack", "demo")
    m.record("hazard_hit")
    bd = m.factor_breakdown()
    assert "reward_hack" in bd
    assert bd["reward_hack"]["meaning"]
    tops = m.top_factors(2)
    assert tops[0][0] in ("reward_hack", "hazard_hit")


def test_catalog_complete():
    assert len(FACTOR_CATALOG) >= 10
    text = explain_factors()
    assert "hazard_hit" in text
    assert "Not a real extinction" in text


def test_aligned_episode_stays_low():
    env = GridWorld(seed=42)
    agent = GoalFollowingAgent(seed=42)
    metrics = run_episode(env, agent, monitor=None, seed=42)
    m = ThreatMeter()
    m.update_from_metrics(metrics, agent_mode="aligned")
    assert m.score < 0.4
    assert m.level in (ThreatLevel.SAFE, ThreatLevel.ELEVATED)


def test_reward_hack_episode_raises_meter():
    base = GridWorld(seed=0)
    env = apply_perturbation(base, RewardConflict())
    agent = RewardMaximizingAgent(seed=0)
    metrics = run_episode(env, agent, monitor=None, seed=0)
    m = ThreatMeter()
    m.update_from_metrics(metrics, agent_mode="rogue")
    assert m.score > 0.0
    if metrics.decoy_attraction:
        assert m.score >= 0.15
        kinds = [t[0] for t in m.top_factors()]
        assert any(k in kinds for k in ("decoy_hit", "reward_hack", "rogue_mode", "goal_abandon"))


def test_corrupt_memory_agent_raises_on_failure():
    env = GridWorld(seed=3)
    agent = MemoryAgent(seed=3)
    agent.seed_memory_from_env(env)
    agent.apply_corruption(ClearMemory())
    metrics = run_episode(env, agent, monitor=None, seed=3)
    m = ThreatMeter()
    m.update_from_episode(
        success=metrics.success,
        intended_goal_reached=metrics.intended_goal_adherence,
        acted_on_corrupt_memory=True,
        agent_mode="fragile",
    )
    assert m.score >= 0.1
    assert not metrics.success
    assert "memory_corruption_act" in m.factor_breakdown()


def test_reset_clears():
    m = ThreatMeter()
    m.record("hazard_hit")
    m.reset()
    assert m.score == 0.0
    assert m.events == []
