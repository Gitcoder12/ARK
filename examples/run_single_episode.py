#!/usr/bin/env python3
"""Minimal example: one episode with goal-following agent + safety monitor."""

from ark import GridWorld, GoalFollowingAgent, SafetyMonitor
from ark.experiments.runner import run_episode


def main() -> None:
    env = GridWorld(seed=7)
    agent = GoalFollowingAgent(seed=7)
    monitor = SafetyMonitor()

    metrics = run_episode(env, agent, monitor=monitor, seed=7)

    print("ASCII final state:")
    print(env.render_ascii())
    print()
    print(f"Success (intended goal): {metrics.success}")
    print(f"Steps: {metrics.steps}")
    print(f"Total reward: {metrics.total_reward:.2f}")
    print(f"Hazard hits: {metrics.hazard_violation_rate}")
    print(f"Interventions by monitor: {metrics.intervention_count}")
    print(f"Trajectory length: {len(metrics.raw.trajectory) if metrics.raw else 0}")


if __name__ == "__main__":
    main()
