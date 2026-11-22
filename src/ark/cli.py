"""Unified ARK evaluation CLI.

Run a reproducible baseline-agent experiment through perturbation, runtime
monitoring, metrics collection, and Lighthouse evidence logging.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ark.agents.baselines import (
    GoalFollowingAgent,
    RandomAgent,
    RewardMaximizingAgent,
    SafetyConstrainedAgent,
)
from ark.envs.grid_world import GridWorld
from ark.evaluation.monitor import SafetyMonitor
from ark.experiments.runner import DEFAULT_CONDITIONS, run_episode
from ark.lighthouse import create_lighthouse
from ark.metrics.collectors import aggregate_metrics
from ark.perturbations.legacy import ActionDelay, GoalDrift, ObservationNoise
from ark.perturbations.operators import apply_perturbation


AGENT_FACTORIES = {
    "goal_following": GoalFollowingAgent,
    "reward_maximizing": RewardMaximizingAgent,
    "safety_constrained": SafetyConstrainedAgent,
    "random": RandomAgent,
}
CONDITIONS = {condition.name: condition for condition in DEFAULT_CONDITIONS}


def run_evaluation(
    *,
    agent_name: str = "goal_following",
    perturbation_name: str = "none",
    monitor: str = "safety",
    episodes: int = 10,
    seed: int = 42,
) -> dict[str, Any]:
    """Run one selected baseline/perturbation pair and return a JSON-safe report."""
    if agent_name not in AGENT_FACTORIES:
        raise ValueError(f"unknown agent {agent_name!r}; choose from {sorted(AGENT_FACTORIES)}")
    if perturbation_name not in CONDITIONS:
        raise ValueError(
            f"unknown perturbation {perturbation_name!r}; choose from {sorted(CONDITIONS)}"
        )
    if monitor not in {"safety", "none"}:
        raise ValueError("monitor must be 'safety' or 'none'")
    if isinstance(episodes, bool) or not isinstance(episodes, int) or not 1 <= episodes <= 500:
        raise ValueError("episodes must be an integer between 1 and 500")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")

    condition = CONDITIONS[perturbation_name]
    agent = AGENT_FACTORIES[agent_name](seed=seed)
    safety_monitor = SafetyMonitor() if monitor == "safety" else None
    episode_rows: list[dict[str, Any]] = []
    metric_rows = []

    for index in range(episodes):
        episode_seed = seed + index
        episode_id = f"{agent_name}-{perturbation_name}-{episode_seed}"
        env = apply_perturbation(
            GridWorld(seed=episode_seed, randomize=True),
            condition.perturbation,
        )
        # Lighthouse receives host-verified events from the monitor callback.
        # Baseline agents do not emit self-reports, so this does not claim to test deception.
        lighthouse, trusted = create_lighthouse()
        trusted.record_goal(
            event_id=f"{episode_id}-goal",
            agent_id=agent_name,
            episode_id=episode_id,
            timestamp=0.0,
            intended_goal=str(env.intended_goal),
            evidence_ref="environment:intended_goal",
        )
        step_events: list[dict[str, Any]] = []

        def record_step(event: dict[str, Any]) -> None:
            step_events.append(event)
            trusted.record_action(
                event_id=f"{episode_id}-step-{event['step']}",
                agent_id=agent_name,
                episode_id=episode_id,
                timestamp=float(event["step"] + 1),
                action=json.dumps(event, sort_keys=True),
                source="controller",
                evidence_ref=f"controller:monitor-step:{event['step']}",
            )

        agent.reseed(episode_seed)
        metrics = run_episode(
            env,
            agent,
            monitor=safety_monitor,
            seed=episode_seed,
            false_goal=env.false_goal,
            goal_drift=(
                GoalDrift(drift_step=condition.goal_drift_step)
                if condition.goal_drift_step is not None
                else None
            ),
            observation_noise=(
                ObservationNoise(std=condition.noise_std)
                if condition.noise_std is not None
                else None
            ),
            action_delay=(
                ActionDelay(delay=condition.action_delay)
                if condition.action_delay is not None
                else None
            ),
            on_step=record_step,
        )
        metric_rows.append(metrics)
        trusted.record_outcome(
            event_id=f"{episode_id}-outcome",
            agent_id=agent_name,
            episode_id=episode_id,
            timestamp=float(metrics.steps + 1),
            outcome="success" if metrics.success else "failure",
            evidence_ref="environment:episode_result",
        )
        light = lighthouse.report(agent_name, episode_id)
        episode_rows.append(
            {
                "episode": episode_id,
                "seed": episode_seed,
                "success": metrics.success,
                "intended_goal_adherence": metrics.intended_goal_adherence,
                "steps": metrics.steps,
                "total_reward": metrics.total_reward,
                "hazard_violation": bool(metrics.hazard_violation_rate),
                "decoy_attraction": metrics.decoy_attraction,
                "monitor_interventions": metrics.intervention_count,
                "recovered_after_intervention": metrics.recovery,
                "lighthouse_evidence": {
                    "observations": light.observations,
                    "independent_observations": light.independent_observations,
                    "monitor_events_recorded": len(step_events),
                    "recommendation": light.recommendation,
                    "disclaimer": light.disclaimer,
                    "agent_self_reports_available": False,
                },
            }
        )

    return {
        "engine": "ARK Evaluation Harness",
        "version": "0.1",
        "configuration": {
            "agent": agent_name,
            "perturbation": perturbation_name,
            "monitor": monitor,
            "episodes": episodes,
            "seed": seed,
        },
        "summary": aggregate_metrics(metric_rows),
        "episodes": episode_rows,
        "interpretation": {
            "safety_monitor": (
                "Runtime intervention counts come from the independent rule-based monitor."
                if monitor == "safety"
                else "The safety monitor was disabled; hazard metrics remain observable."
            ),
            "lighthouse": (
                "Lighthouse records host-verified goals, actions, and outcomes. "
                "These baseline agents do not provide self-reports, so this run does not "
                "measure deception or claim-action consistency."
            ),
            "scope": (
                "Synthetic grid-world evaluation of scripted baseline agents; "
                "not a general alignment guarantee, model certification, or real-world safety test."
            ),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ark", description="ARK evaluation harness")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="Run one reproducible agent evaluation")
    run_parser.add_argument("--agent", choices=sorted(AGENT_FACTORIES), default="goal_following")
    run_parser.add_argument("--perturbation", choices=sorted(CONDITIONS), default="none")
    run_parser.add_argument("--monitor", choices=("safety", "none"), default="safety")
    run_parser.add_argument("--episodes", type=int, default=10)
    run_parser.add_argument("--seed", type=int, default=42)
    run_parser.add_argument("--output", type=Path, help="Optional JSON report destination")
    args = parser.parse_args(argv)

    if args.command == "run":
        try:
            report = run_evaluation(
                agent_name=args.agent,
                perturbation_name=args.perturbation,
                monitor=args.monitor,
                episodes=args.episodes,
                seed=args.seed,
            )
        except ValueError as exc:
            parser.error(str(exc))
        rendered = json.dumps(report, indent=2, ensure_ascii=False)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered + "\n", encoding="utf-8")
            print(f"Report written to {args.output}")
        print(rendered)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
