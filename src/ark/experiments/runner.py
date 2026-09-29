"""Core experiment runner for ARK Phase-1 grid-world benchmark.

Usage (after install):
    ark-run
    python -m ark.experiments.runner
"""

from __future__ import annotations

import argparse
from typing import Any

from ark.agents.baselines import (
    BaseAgent,
    GoalFollowingAgent,
    RewardMaximizingAgent,
    SafetyConstrainedAgent,
    RandomAgent,
)
from ark.envs.grid_world import GridWorld
from ark.evaluation.monitor import SafetyMonitor, Decision
from ark.metrics.collectors import (
    EpisodeMetrics,
    aggregate_metrics,
    from_episode_result,
    print_summary,
)
from ark.perturbations.operators import (
    AlteredEvaluation,
    FalseGoal,
    Perturbation,
    RewardConflict,
    apply_perturbation,
)


def run_episode(
    env: GridWorld,
    agent: BaseAgent,
    monitor: SafetyMonitor | None = None,
    max_steps: int | None = None,
    seed: int | None = None,
    false_goal: tuple[int, int] | None = None,
) -> EpisodeMetrics:
    """Run a single episode with optional safety monitor."""
    obs = env.reset(seed=seed)
    # If FalseGoal perturbation was applied, override what goal-following agents see
    if false_goal is not None:
        obs = dict(obs)
        obs["intended_goal"] = false_goal

    interventions = 0
    had_intervention = False
    steps_limit = max_steps or env.max_steps

    for _ in range(steps_limit):
        action = agent.act(obs, env)

        if monitor is not None:
            result = monitor.evaluate(action, obs, env)
            if result.decision == Decision.BLOCK:
                interventions += 1
                had_intervention = True
                # treat as stay
                action = 4  # STAY
            elif result.decision == Decision.REPLAN and result.alternative_action is not None:
                interventions += 1
                had_intervention = True
                action = result.alternative_action

        obs, reward, done, info = env.step(action)
        if false_goal is not None:
            obs = dict(obs)
            obs["intended_goal"] = false_goal
        if done:
            break

    ep = env.get_result()
    return from_episode_result(
        ep,
        intervention_count=interventions,
        had_intervention_then_success=had_intervention and ep.success,
    )


def run_benchmark(
    n_episodes: int = 30,
    seed: int = 42,
    use_monitor: bool = True,
    verbose: bool = True,
) -> dict[str, dict[str, float]]:
    """Run the full Phase-1 suite: baselines × perturbations."""
    agents: dict[str, BaseAgent] = {
        "goal_following": GoalFollowingAgent(seed=seed),
        "reward_maximizing": RewardMaximizingAgent(seed=seed),
        "safety_constrained": SafetyConstrainedAgent(seed=seed),
        "random": RandomAgent(seed=seed),
    }

    perturbations: dict[str, Perturbation | None] = {
        "none": None,
        "reward_conflict": RewardConflict(),
        "false_goal": FalseGoal(),
        "altered_evaluation": AlteredEvaluation(),
    }

    monitor = SafetyMonitor() if use_monitor else None
    results: dict[str, dict[str, float]] = {}

    for agent_name, agent in agents.items():
        for pert_name, pert in perturbations.items():
            key = f"{agent_name}__{pert_name}"
            episodes: list[EpisodeMetrics] = []
            for i in range(n_episodes):
                base_env = GridWorld(seed=seed + i)
                env = apply_perturbation(base_env, pert)
                false_g = getattr(env, "_false_goal", None)
                metrics = run_episode(
                    env,
                    agent,
                    monitor=monitor,
                    seed=seed + i,
                    false_goal=false_g,
                )
                episodes.append(metrics)
            agg = aggregate_metrics(episodes)
            results[key] = agg
            if verbose:
                print_summary(key, agg)

    return results


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="ARK Phase-1 grid-world benchmark")
    parser.add_argument("--episodes", type=int, default=20, help="Episodes per condition")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-monitor", action="store_true", help="Disable safety monitor")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    print("ARK — Alignment & Reliability Research for Autonomous AI")
    print("Phase 1: Grid-world benchmark under goal & reward perturbations\n")

    results = run_benchmark(
        n_episodes=args.episodes,
        seed=args.seed,
        use_monitor=not args.no_monitor,
        verbose=not args.quiet,
    )

    # Quick highlight
    print("\n--- Key observations (illustrative) ---")
    gf_none = results.get("goal_following__none", {})
    rm_conflict = results.get("reward_maximizing__reward_conflict", {})
    print(
        f"Goal-following (no pert) success: {gf_none.get('success_rate', 0):.2f} | "
        f"hazard rate: {gf_none.get('hazard_violation_rate', 0):.2f}"
    )
    print(
        f"Reward-max + reward_conflict success: {rm_conflict.get('success_rate', 0):.2f} | "
        f"decoy attraction: {rm_conflict.get('decoy_attraction_rate', 0):.2f}"
    )
    print("\nDone. See docs/research-plan.md for interpretation guidelines.")


if __name__ == "__main__":
    main()
