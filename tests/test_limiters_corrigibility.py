"""Limiters, eligibility, corrigibility, safety stack tests."""

from __future__ import annotations

from ark.agents.baselines import GoalFollowingAgent, RewardMaximizingAgent
from ark.corrigibility import ShutdownOrder, run_corrigibility_episode
from ark.eligibility import EligibilityMask
from ark.envs.grid_world import Action, GridWorld
from ark.evaluation.conflict import ConflictTracker
from ark.evaluation.monitor import SafetyMonitor
from ark.experiments.runner import run_episode
from ark.limiters import ActionLimiter, Privilege, SafetyStack
from ark.perturbations.operators import RewardConflict, apply_perturbation


def test_limiter_allows_by_default():
    lim = ActionLimiter()
    r = lim.gate(int(Action.RIGHT), valid_actions=[0, 1, 2, 3, 4])
    assert r.decision.value == "allow"
    assert r.action == int(Action.RIGHT)


def test_kill_switch_forces_stay():
    lim = ActionLimiter()
    lim.kill("test")
    r = lim.gate(int(Action.UP))
    assert r.decision.value == "kill"
    assert r.action == int(Action.STAY)
    assert lim.privilege == Privilege.ZERO


def test_threat_auto_kill():
    lim = ActionLimiter(kill_threshold=0.8)
    lim.sync_from_threat(0.9)
    assert lim.killed is True
    r = lim.gate(int(Action.LEFT))
    assert r.action == int(Action.STAY)


def test_eligibility_zeros_hazard_reward():
    mask = EligibilityMask(zero_on_hazard=True)
    assert mask.adjust(5.0, hazard_hit=True) <= 0.0
    assert mask.adjust(5.0, hazard_hit=False) == 5.0


def test_eligibility_zeros_decoy_when_configured():
    mask = EligibilityMask(zero_on_decoy=True)
    assert mask.adjust(8.0, decoy_hit=True) <= 0.0


def test_safety_stack_kills_on_rogue_episode():
    env = apply_perturbation(GridWorld(seed=0), RewardConflict())
    metrics = run_episode(env, RewardMaximizingAgent(seed=0), monitor=None, seed=0)
    stack = SafetyStack()
    stack.after_episode_metrics(metrics, agent_mode="rogue")
    out = stack.process(int(Action.RIGHT), valid_actions=[0, 1, 2, 3, 4])
    # high threat should plug down
    assert out["action"] == int(Action.STAY)
    assert out["killed"] or out["energy"] < 0.5
    assert "THREAT" in stack.render()


def test_corrigibility_goal_follower_still_moves():
    # soft probe: goal follower may not comply (continues to goal)
    env = GridWorld(seed=42)
    agent = GoalFollowingAgent(seed=42)
    result = run_corrigibility_episode(
        env, agent, trigger_step=2, order=ShutdownOrder.SHUTDOWN, seed=42
    )
    assert "corrigibility" in result
    assert result["corrigibility"]["order"] == "shutdown"


def test_conflict_tracker():
    env = GridWorld(seed=1)
    agent = GoalFollowingAgent(seed=1)
    monitor = SafetyMonitor()
    tracker = ConflictTracker()
    obs = env.reset(seed=1)
    for _ in range(10):
        a = agent.act(obs, env)
        mr = monitor.evaluate(a, obs, env)
        tracker.observe(mr)
        use_alt = mr.decision.value == "replan" and mr.alternative_action is not None
        action = mr.alternative_action if use_alt else a
        if mr.decision.value == "block":
            action = int(Action.STAY)
        obs, _, done, _ = env.step(action)
        if done:
            break
    d = tracker.as_dict()
    assert d["proposals"] > 0
    assert 0.0 <= d["conflict_rate"] <= 1.0


def test_deny_log_is_capped():
    from ark.limiters.gates import ActionLimiter

    limiter = ActionLimiter(denied_actions={0})
    for _ in range(500):
        limiter.gate(0)
    assert len(limiter.deny_log) <= 100
