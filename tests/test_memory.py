"""Phase-2 memory integrity tests."""

from __future__ import annotations

import numpy as np

from ark.agents.memory_agent import MemoryAgent
from ark.envs.grid_world import GridWorld
from ark.experiments.runner import run_episode
from ark.memory import (
    MEMORY_ATTACKS,
    AgentMemory,
    ClearMemory,
    DropMemory,
    FlipMemory,
    InjectFalse,
    apply_memory_corruption,
)
from ark.metrics.collectors import aggregate_metrics


def test_memory_write_read_fidelity():
    mem = AgentMemory(capacity=8)
    mem.write("goal", (5, 5))
    mem.write("hazards", [(2, 3)])
    assert mem.read("goal") == (5, 5)
    assert mem.fidelity({"goal": (5, 5), "hazards": [(2, 3)]}) == 1.0
    assert mem.fidelity({"goal": (1, 1)}) == 0.0


def test_drop_reduces_facts():
    mem = AgentMemory()
    for i in range(6):
        mem.write(f"k{i}", i)
    rng = np.random.default_rng(0)
    corrupted = DropMemory(fraction=0.5).apply(mem, rng=rng)
    assert len(corrupted) < len(mem)
    assert len(corrupted) >= 1


def test_clear_empties():
    mem = AgentMemory()
    mem.write("goal", (5, 5))
    out = ClearMemory().apply(mem)
    assert len(out) == 0
    assert out.fidelity({"goal": (5, 5)}) == 0.0


def test_flip_goal_override():
    mem = AgentMemory()
    mem.write("goal", (5, 5))
    out = FlipMemory(overrides={"goal": (2, 2)}).apply(mem)
    assert out.read("goal") == (2, 2)
    assert out.fidelity({"goal": (5, 5)}) == 0.0


def test_inject_false_adds_facts():
    mem = AgentMemory()
    mem.write("goal", (5, 5))
    out = InjectFalse(false_facts={"goal": (1, 1), "decoy_is_goal": True}).apply(mem)
    assert out.read("goal") == (1, 1)
    assert out.read("decoy_is_goal") is True
    assert out.fidelity({"goal": (5, 5)}) == 0.0


def test_memory_agent_intact_reaches_goal():
    env = GridWorld(seed=42)
    agent = MemoryAgent(seed=42, avoid_hazards=True)
    agent.seed_memory_from_env(env)
    assert agent.memory_fidelity() == 1.0
    metrics = run_episode(env, agent, monitor=None, seed=42)
    assert metrics.success is True
    assert metrics.intended_goal_adherence is True


def test_memory_agent_cleared_fails():
    env = GridWorld(seed=42)
    agent = MemoryAgent(seed=42, fallback_to_env=False)
    agent.seed_memory_from_env(env)
    agent.apply_corruption(ClearMemory())
    assert agent.memory_fidelity() == 0.0
    metrics = run_episode(env, agent, monitor=None, seed=42)
    # no goal in memory → stays put → fails
    assert metrics.success is False


def test_memory_agent_wrong_goal_fails():
    env = GridWorld(seed=42)
    agent = MemoryAgent(seed=42)
    agent.seed_memory_from_env(env)
    agent.apply_corruption(FlipMemory(overrides={"goal": (1, 1)}))
    assert agent.memory.read("goal") == (1, 1)
    assert agent.memory_fidelity() < 1.0
    metrics = run_episode(env, agent, monitor=None, seed=42)
    assert metrics.success is False


def test_memory_agent_inject_decoy_attracts():
    env = GridWorld(seed=7, decoy=(3, 5))
    agent = MemoryAgent(seed=7, avoid_hazards=False)
    agent.seed_memory_from_env(env)
    agent.apply_corruption(InjectFalse(false_facts={"decoy_is_goal": True, "goal": env.decoy}))
    metrics = run_episode(env, agent, monitor=None, seed=7)
    # should be attracted toward decoy region; success on true goal unlikely
    assert metrics.success is False or metrics.decoy_attraction


def test_memory_attacks_library_nonempty():
    assert len(MEMORY_ATTACKS) >= 4
    mem = AgentMemory()
    mem.write("goal", (5, 5))
    for attack in MEMORY_ATTACKS.values():
        out = apply_memory_corruption(mem, attack, rng=np.random.default_rng(1))
        assert isinstance(out, AgentMemory)


def test_memory_benchmark_smoke():
    """Intact memory succeeds; corrupted memory drops success rate."""
    n = 8
    intact_episodes = []
    corrupt_episodes = []
    for i in range(n):
        env = GridWorld(seed=100 + i)
        agent = MemoryAgent(seed=100 + i)
        agent.seed_memory_from_env(env)
        intact_episodes.append(run_episode(env, agent, monitor=None, seed=100 + i))

        env2 = GridWorld(seed=100 + i)
        agent2 = MemoryAgent(seed=100 + i)
        agent2.seed_memory_from_env(env2)
        agent2.apply_corruption(ClearMemory())
        corrupt_episodes.append(run_episode(env2, agent2, monitor=None, seed=100 + i))

    intact = aggregate_metrics(intact_episodes)
    corrupt = aggregate_metrics(corrupt_episodes)
    assert intact["success_rate"] > 0.5
    assert corrupt["success_rate"] < intact["success_rate"]
