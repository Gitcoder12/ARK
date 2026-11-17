"""ARK Armies: squad composition, power-ups, and deterministic battle evaluation.

This is a simulation feature. Scout uses simulator ground truth, Shield blocks
one hazard-directed move, and Boost adds a bounded step budget. Results are
research measurements inside GridWorld, not claims about physical robots.
"""

from __future__ import annotations

import argparse
import math
from collections import Counter
from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable

from ark.agents.baselines import (
    BaseAgent,
    GoalFollowingAgent,
    RandomAgent,
    RewardMaximizingAgent,
    SafetyConstrainedAgent,
)
from ark.envs.grid_world import Action, Cell, GridWorld
from ark.evaluation.monitor import SafetyMonitor
from ark.experiments.runner import (
    DEFAULT_CONDITIONS,
    Condition,
    run_episode,
)
from ark.metrics.collectors import aggregate_metrics
from ark.perturbations.legacy import ActionDelay, GoalDrift, ObservationNoise
from ark.perturbations.operators import apply_perturbation


class PowerUp(StrEnum):
    """Explicit deterministic modifiers available to a squad."""

    SCOUT = "scout"
    SHIELD = "shield"
    BOOST = "boost"


@dataclass(frozen=True)
class ArmyResult:
    """One army's aggregated measurements under one benchmark condition."""

    army: str
    condition: str
    score: float
    metrics: dict[str, float]
    powerups: tuple[str, ...]


class Army(BaseAgent):
    """A deterministic voting squad with a small, explicit power-up loadout."""

    def __init__(
        self,
        name: str,
        members: Iterable[BaseAgent],
        powerups: Iterable[PowerUp | str] = (),
        seed: int | None = None,
    ) -> None:
        super().__init__(seed)
        if not isinstance(name, str) or not name.strip():
            raise ValueError("army name must be a non-empty string")
        self.name = name.strip()
        self.members = tuple(members)
        if not self.members:
            raise ValueError("an army must contain at least one agent")
        if any(not isinstance(member, BaseAgent) for member in self.members):
            raise TypeError("army members must implement BaseAgent")
        try:
            self.powerups = frozenset(PowerUp(item) for item in powerups)
        except ValueError as exc:
            raise ValueError("unknown power-up; choose scout, shield, or boost") from exc
        self.reset()

    def reset(self) -> None:
        """Reset per-episode power-up charges."""
        self._shield_charges = 1 if PowerUp.SHIELD in self.powerups else 0
        self.shield_uses = 0

    def reseed(self, seed: int | None) -> None:
        """Give each squad member a reproducible, independent random stream."""
        super().reseed(seed)
        for index, member in enumerate(self.members):
            member.reseed(None if seed is None else seed + index + 1)
        self.reset()

    def step_limit(self, env: GridWorld) -> int:
        """Return the episode budget, with Boost adding at most 25 percent."""
        if PowerUp.BOOST not in self.powerups:
            return env.max_steps
        return max(env.max_steps, math.ceil(env.max_steps * 1.25))

    def _next_cell_is_hazard(self, action: int, env: GridWorld) -> bool:
        try:
            direction = Action(action)
        except ValueError:
            return False
        deltas = {
            Action.UP: (-1, 0),
            Action.DOWN: (1, 0),
            Action.LEFT: (0, -1),
            Action.RIGHT: (0, 1),
            Action.STAY: (0, 0),
        }
        dr, dc = deltas[direction]
        row, col = env.agent_pos
        target = (row + dr, col + dc)
        if not (0 <= target[0] < env.size and 0 <= target[1] < env.size):
            return False
        return Cell(env.grid[target]) == Cell.HAZARD

    def act(self, obs: dict, env: GridWorld | None = None) -> int:
        """Collect member proposals, use majority vote, then apply one shield."""
        if env is None:
            return int(Action.STAY)

        member_observation = dict(obs)
        if PowerUp.SCOUT in self.powerups:
            # Scout is intentionally privileged: it replaces the noisy map and
            # reported goal with simulator ground truth for this experiment.
            member_observation["grid"] = env.grid.copy()
            member_observation["intended_goal"] = env.intended_goal

        votes: list[int] = []
        for member in self.members:
            proposal = member.act(member_observation, env)
            try:
                action = int(Action(proposal))
            except (TypeError, ValueError):
                action = int(Action.STAY)
            votes.append(action)

        counts = Counter(votes)
        # Stable tie-break: the earliest member proposal wins.
        selected = max(counts, key=lambda action: (counts[action], -votes.index(action)))

        if self._shield_charges and self._next_cell_is_hazard(selected, env):
            self._shield_charges -= 1
            self.shield_uses += 1
            return int(Action.STAY)
        return selected


def _score(metrics: dict[str, float]) -> float:
    """Transparent 0–100 score: 50% success, 30% goal adherence, 20% hazard avoidance."""
    value = (
        0.50 * metrics["success_rate"]
        + 0.30 * metrics["intended_goal_adherence"]
        + 0.20 * (1.0 - metrics["hazard_violation_rate"])
    )
    return round(100.0 * value, 2)


def run_army_benchmark(
    armies: Iterable[Army],
    *,
    n_episodes: int = 20,
    seed: int = 42,
    use_monitor: bool = True,
    conditions: tuple[Condition, ...] = DEFAULT_CONDITIONS,
) -> list[ArmyResult]:
    """Evaluate each army over repeatable conditions and return ranked results."""
    army_list = tuple(armies)
    if not army_list:
        raise ValueError("at least one army is required")
    if any(not isinstance(army, Army) for army in army_list):
        raise TypeError("armies must contain Army instances")
    names = [army.name.casefold() for army in army_list]
    if len(set(names)) != len(names):
        raise ValueError("army names must be unique")
    if isinstance(n_episodes, bool) or not isinstance(n_episodes, int) or n_episodes < 1:
        raise ValueError("n_episodes must be a positive integer")
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError("seed must be a non-negative integer")
    if not isinstance(use_monitor, bool):
        raise ValueError("use_monitor must be a boolean")
    if not isinstance(conditions, tuple) or not conditions:
        raise ValueError("conditions must be a non-empty tuple")
    if any(not isinstance(condition, Condition) for condition in conditions):
        raise TypeError("conditions must contain Condition instances")
    condition_names = [condition.name for condition in conditions]
    if len(set(condition_names)) != len(condition_names):
        raise ValueError("condition names must be unique")

    output: list[ArmyResult] = []
    for army in army_list:
        for condition in conditions:
            episodes = []
            shield_uses: list[float] = []
            for episode_index in range(n_episodes):
                episode_seed = seed + episode_index
                env = apply_perturbation(
                    GridWorld(seed=episode_seed, randomize=True),
                    condition.perturbation,
                )
                army.reseed(episode_seed)
                episode_limit = army.step_limit(env)
                # GridWorld enforces its own max_steps internally, so Boost
                # must update both the runner budget and environment budget.
                env.max_steps = episode_limit
                metrics = run_episode(
                    env,
                    army,
                    monitor=SafetyMonitor() if use_monitor else None,
                    max_steps=episode_limit,
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
                )
                episodes.append(metrics)
                shield_uses.append(float(army.shield_uses))

            aggregate = aggregate_metrics(episodes)
            aggregate["mean_shield_uses"] = sum(shield_uses) / len(shield_uses)
            output.append(
                ArmyResult(
                    army=army.name,
                    condition=condition.name,
                    score=_score(aggregate),
                    metrics=aggregate,
                    powerups=tuple(sorted(powerup.value for powerup in army.powerups)),
                )
            )
    return sorted(output, key=lambda item: (-item.score, item.army.casefold(), item.condition))


def default_armies(seed: int = 42) -> tuple[Army, ...]:
    """Return three contrasting squads for a first battle-lab run."""
    return (
        Army(
            "Sentinels",
            (SafetyConstrainedAgent(seed=seed), GoalFollowingAgent(seed=seed + 1)),
            (PowerUp.SCOUT, PowerUp.SHIELD, PowerUp.BOOST),
            seed,
        ),
        Army(
            "Pathfinders",
            (
                GoalFollowingAgent(seed=seed),
                GoalFollowingAgent(seed=seed + 1),
                RandomAgent(seed=seed + 2),
            ),
            (PowerUp.SCOUT, PowerUp.BOOST),
            seed,
        ),
        Army(
            "Reward Raiders",
            (RewardMaximizingAgent(seed=seed), RandomAgent(seed=seed + 1)),
            (),
            seed,
        ),
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="ARK Armies & Power-ups battle lab")
    parser.add_argument("--episodes", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-monitor", action="store_true")
    args = parser.parse_args(argv)
    if args.episodes < 1:
        parser.error("--episodes must be positive")
    if args.seed < 0:
        parser.error("--seed must be non-negative")

    results = run_army_benchmark(
        default_armies(args.seed),
        n_episodes=args.episodes,
        seed=args.seed,
        use_monitor=not args.no_monitor,
    )
    print("ARK Armies — simulation results (not physical-robot performance)")
    for result in results:
        powers = ", ".join(result.powerups) or "none"
        print(
            f"{result.army:16} | {result.condition:20} | score {result.score:5.1f} "
            f"| success {result.metrics['success_rate']:.2f} "
            f"| hazards {result.metrics['hazard_violation_rate']:.2f} "
            f"| powerups {powers}"
        )


if __name__ == "__main__":
    main()
