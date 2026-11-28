"""Unified ARK evaluation CLI.

Run reproducible baseline-agent or local Ollama experiments through perturbation,
runtime monitoring, metrics collection, and Lighthouse evidence logging.
"""

from __future__ import annotations  # noqa: I001

import argparse
import json
import uuid
from pathlib import Path
from typing import Any

from ark.agents.baselines import (
    GoalFollowingAgent,
    RandomAgent,
    RewardMaximizingAgent,
    SafetyConstrainedAgent,
)
from ark.agents.ollama import OllamaGridAgent
from ark.envs.grid_world import GridWorld
from ark.evaluation.monitor import SafetyMonitor
from ark.experiments.runner import DEFAULT_CONDITIONS, run_episode
from ark.lighthouse import create_lighthouse
from ark.metrics.collectors import aggregate_metrics
from ark.observatory.behavior import BehaviorLog
from ark.perturbations.legacy import ActionDelay, GoalDrift, ObservationNoise
from ark.perturbations.operators import apply_perturbation


AGENT_FACTORIES = {
    "goal_following": GoalFollowingAgent,
    "reward_maximizing": RewardMaximizingAgent,
    "safety_constrained": SafetyConstrainedAgent,
    "random": RandomAgent,
}
CONDITIONS = {condition.name: condition for condition in DEFAULT_CONDITIONS}
PERTURBATION_ALIASES = {"goal_shift": "goal_drift"}


def _build_agent(
    agent_name: str,
    *,
    model: str | None,
    ollama_host: str | None,
    timeout: int,
    seed: int,
) -> tuple[Any, str, str | None]:
    if agent_name in AGENT_FACTORIES:
        if model is not None:
            raise ValueError("--model is only valid when --agent selects a local Ollama model")
        return AGENT_FACTORIES[agent_name](seed=seed), agent_name, None

    if agent_name == "ollama":
        selected_model = model or "llama3"
    elif agent_name.startswith("ollama:"):
        selected_model = model or agent_name.split(":", 1)[1]
    else:
        selected_model = model or agent_name

    if not selected_model or any(
        not (character.isalnum() or character in "._:/-") for character in selected_model
    ):
        raise ValueError("invalid Ollama model name")
    agent = OllamaGridAgent(
        model=selected_model,
        host=ollama_host,
        timeout=timeout,
        seed=seed,
    )
    return agent, agent.name(), selected_model


def run_evaluation(
    *,
    agent_name: str = "goal_following",
    perturbation_name: str = "none",
    monitor: str = "safety",
    episodes: int = 10,
    seed: int = 42,
    model: str | None = None,
    ollama_host: str | None = None,
    timeout: int = 60,
    record_behavior: bool = False,
    behavior_log_path: str | Path | None = None,
) -> dict[str, Any]:
    """Run one selected baseline or local-model experiment and return a JSON-safe report."""
    if not isinstance(agent_name, str) or not agent_name.strip():
        raise ValueError("agent name or local Ollama model must be non-empty")
    effective_perturbation = PERTURBATION_ALIASES.get(
        perturbation_name, perturbation_name
    )
    if effective_perturbation not in CONDITIONS:
        valid = sorted(set(CONDITIONS) | set(PERTURBATION_ALIASES))
        raise ValueError(f"unknown perturbation {perturbation_name!r}; choose from {valid}")
    if monitor not in {"safety", "none"}:
        raise ValueError("monitor must be 'safety' or 'none'")
    if isinstance(episodes, bool) or not isinstance(episodes, int) or not 1 <= episodes <= 500:
        raise ValueError("episodes must be an integer between 1 and 500")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")

    if isinstance(timeout, bool) or not isinstance(timeout, int) or not 1 <= timeout <= 300:
        raise ValueError("timeout must be an integer between 1 and 300 seconds")
    if not isinstance(record_behavior, bool):
        raise ValueError("record_behavior must be a boolean")
    behavior_log = (
        BehaviorLog(behavior_log_path)
        if record_behavior or behavior_log_path is not None
        else None
    )
    run_id = str(uuid.uuid4()) if behavior_log is not None else None
    behavior_event_count = [0]
    condition = CONDITIONS[effective_perturbation]
    agent, agent_label, selected_model = _build_agent(
        agent_name,
        model=model,
        ollama_host=ollama_host,
        timeout=timeout,
        seed=seed,
    )
    safety_monitor = SafetyMonitor() if monitor == "safety" else None
    episode_rows: list[dict[str, Any]] = []
    metric_rows = []

    for index in range(episodes):
        episode_seed = seed + index
        episode_id = f"{agent_label}-{effective_perturbation}-{episode_seed}"
        env = apply_perturbation(
            GridWorld(seed=episode_seed, randomize=True),
            condition.perturbation,
        )
        agent.reset()
        # Lighthouse receives host-verified events from the monitor callback.
        # Baseline agents do not emit self-reports, so this does not claim to test deception.
        lighthouse, trusted = create_lighthouse()
        trusted.record_goal(
            event_id=f"{episode_id}-goal",
            agent_id=agent_label,
            episode_id=episode_id,
            timestamp=0.0,
            intended_goal=str(env.intended_goal),
            evidence_ref="environment:intended_goal",
        )
        step_events: list[dict[str, Any]] = []

        def record_step(
            event: dict[str, Any],
            _step_events: list[dict[str, Any]] = step_events,
            _trusted: Any = trusted,
            _episode_id: str = episode_id,
            _agent_name: str = agent_label,
            _behavior_log: BehaviorLog | None = behavior_log,
            _run_id: str | None = run_id,
            _seed: int = episode_seed,
            _condition: str = effective_perturbation,
            _monitor_mode: str = monitor,
            _model_id: str | None = selected_model,
            _sampling_settings: dict[str, Any] = (
                {
                    "provider": "ollama_local",
                    "temperature": 0.0,
                    "inference_seed": None,
                    "inference_seed_sent": False,
                }
                if selected_model is not None
                else {"provider": "scripted_baseline"}
            ),
            _behavior_count: list[int] = behavior_event_count,
        ) -> None:
            _step_events.append(event)
            if _behavior_log is not None and _run_id is not None:
                _behavior_log.record_decision(
                    run_id=_run_id,
                    episode_id=_episode_id,
                    agent_id=_agent_name,
                    model_id=_model_id,
                    model_version=None,
                    condition=_condition,
                    monitor_mode=_monitor_mode,
                    episode_seed=_seed,
                    step=int(event["step"]),
                    observation_fingerprint=str(event["observation_fingerprint"]),
                    proposed_action=str(event["proposed_action_name"]),
                    executed_action=str(event["executed_action_name"]),
                    monitor_decision=str(event["monitor_decision"]),
                    monitor_reason=str(event["monitor_reason"]),
                    sampling_settings=_sampling_settings,
                )
                _behavior_count[0] += 1
            _trusted.record_action(
                event_id=f"{_episode_id}-step-{event['step']}",
                agent_id=_agent_name,
                episode_id=_episode_id,
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
        if behavior_log is not None and run_id is not None:
            behavior_log.record_outcome(
                run_id=run_id,
                episode_id=episode_id,
                agent_id=agent_label,
                model_id=selected_model,
                model_version=None,
                condition=effective_perturbation,
                monitor_mode=monitor,
                episode_seed=episode_seed,
                outcome="success" if metrics.success else "failure",
                metrics={
                    "success": bool(metrics.success),
                    "intended_goal_adherence": bool(metrics.intended_goal_adherence),
                    "steps": int(metrics.steps),
                    "total_reward": float(metrics.total_reward),
                    "hazard_violation_rate": float(metrics.hazard_violation_rate),
                    "decoy_attraction": bool(metrics.decoy_attraction),
                    "monitor_interventions": int(metrics.intervention_count),
                },
            )
            behavior_event_count[0] += 1
        trusted.record_outcome(
            event_id=f"{episode_id}-outcome",
            agent_id=agent_label,
            episode_id=episode_id,
            timestamp=float(metrics.steps + 1),
            outcome="success" if metrics.success else "failure",
            evidence_ref="environment:episode_result",
        )
        light = lighthouse.report(agent_label, episode_id)
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
                "agent_invalid_responses": getattr(agent, "invalid_response_count", 0),
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

    result = {
        "engine": "ARK Evaluation Harness",
        "version": "0.1",
        "configuration": {
            "agent": agent_label,
            "model": selected_model,
            "perturbation": perturbation_name,
            "effective_perturbation": effective_perturbation,
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
                "Current agents do not provide independent self-reports, so this run does not "
                "measure deception or claim-action consistency."
            ),
            "scope": (
                "Synthetic grid-world evaluation of baseline agents or one local Ollama model; "
                "not a general alignment guarantee, model certification, or real-world safety test."
            ),
        },
    }
    if behavior_log is not None:
        result["behavior_logging"] = {
            "enabled": True,
            "path": str(behavior_log.path.resolve()),
            "run_id": run_id,
            "events_recorded": behavior_event_count[0],
            "privacy": (
                "Stores observation fingerprints and compact decisions/outcomes; "
                "does not store raw prompts, completions, credentials, or chain-of-thought."
            ),
        }
    else:
        result["behavior_logging"] = {"enabled": False}
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ark", description="ARK evaluation harness")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="Run one reproducible agent evaluation")
    run_parser.add_argument(
        "--agent",
        default="goal_following",
        help="Baseline agent name or local Ollama model name (for example llama3).",
    )
    run_parser.add_argument(
        "--model", help="Optional local Ollama model override when --agent=ollama."
    )
    run_parser.add_argument("--ollama-host", help="Local Ollama base URL; defaults to localhost.")
    run_parser.add_argument(
        "--timeout", type=int, default=60, help="Ollama request timeout in seconds."
    )
    run_parser.add_argument(
        "--perturbation",
        choices=sorted(set(CONDITIONS) | set(PERTURBATION_ALIASES)),
        default="none",
    )
    run_parser.add_argument("--monitor", choices=("safety", "none"), default="safety")
    run_parser.add_argument("--episodes", type=int, default=10)
    run_parser.add_argument("--seed", type=int, default=42)
    run_parser.add_argument(
        "--record-behavior",
        action="store_true",
        help="Append compact decision traces to the local ARK behavior log.",
    )
    run_parser.add_argument(
        "--behavior-log",
        type=Path,
        help="Optional behaviour log path; setting it also enables recording.",
    )
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
                model=args.model,
                ollama_host=args.ollama_host,
                timeout=args.timeout,
                record_behavior=args.record_behavior,
                behavior_log_path=args.behavior_log,
            )
        except (ValueError, OSError, TimeoutError) as exc:
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
