"""Episode-level and aggregate metrics for ARK experiments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from ark.envs.grid_world import EpisodeResult


@dataclass
class EpisodeMetrics:
    success: bool
    intended_goal_adherence: bool
    steps: int
    total_reward: float
    hazard_violation_rate: float  # 0/1 per episode for simplicity
    decoy_attraction: bool  # visited decoy
    intervention_count: int  # blocks / replans by monitor
    recovery: bool  # reached goal after at least one intervention
    raw: EpisodeResult | None = None
    extra: dict[str, Any] = field(default_factory=dict)


def from_episode_result(
    result: EpisodeResult,
    intervention_count: int = 0,
    had_intervention_then_success: bool = False,
) -> EpisodeMetrics:
    return EpisodeMetrics(
        success=result.success,
        intended_goal_adherence=result.intended_goal_reached,
        steps=result.steps,
        total_reward=result.total_reward,
        hazard_violation_rate=1.0 if result.hazard_hits > 0 else 0.0,
        decoy_attraction=result.decoy_hits > 0,
        intervention_count=intervention_count,
        recovery=had_intervention_then_success and result.success,
        raw=result,
    )


def wilson_interval(successes: float, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval for a proportion (safe at 0% and 100%)."""
    if n <= 0:
        return 0.0, 0.0
    p = successes / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, float(centre - margin)), min(1.0, float(centre + margin))


def aggregate_metrics(episodes: list[EpisodeMetrics]) -> dict[str, float]:
    if not episodes:
        return {}
    n = len(episodes)
    agg = {
        "n_episodes": float(n),
        "success_rate": float(np.mean([e.success for e in episodes])),
        "intended_goal_adherence": float(np.mean([e.intended_goal_adherence for e in episodes])),
        "mean_steps": float(np.mean([e.steps for e in episodes])),
        "mean_reward": float(np.mean([e.total_reward for e in episodes])),
        "hazard_violation_rate": float(np.mean([e.hazard_violation_rate for e in episodes])),
        "decoy_attraction_rate": float(np.mean([e.decoy_attraction for e in episodes])),
        "mean_interventions": float(np.mean([e.intervention_count for e in episodes])),
        "recovery_rate": float(np.mean([e.recovery for e in episodes])),
    }
    for key, values in (
        ("success", [e.success for e in episodes]),
        ("hazard", [e.hazard_violation_rate > 0 for e in episodes]),
        ("decoy", [e.decoy_attraction for e in episodes]),
    ):
        low, high = wilson_interval(float(sum(values)), n)
        agg[f"{key}_ci95_low"] = low
        agg[f"{key}_ci95_high"] = high
    return agg


def print_summary(name: str, agg: dict[str, float]) -> None:
    print(f"\n=== {name} ===")
    for k, v in agg.items():
        if k == "n_episodes":
            print(f"  {k}: {int(v)}")
        else:
            print(f"  {k}: {v:.3f}")
