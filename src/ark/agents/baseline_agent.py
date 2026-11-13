"""Train and evaluate ARK's learned Q-learning baseline.

Example:
    python -m ark.agents.baseline_agent --train-episodes 500 --eval-episodes 100 --seed 42

Training and evaluation use disjoint deterministic seed ranges. The learned
policy is evaluated alongside the scripted goal-following reference on the
same held-out layouts, with the runtime safety monitor enabled for both.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from typing import Any

from ark.agents.baselines import GoalFollowingAgent
from ark.agents.q_learning import QLearningAgent, train_q_learning
from ark.envs.grid_world import GridWorld
from ark.evaluation.monitor import SafetyMonitor
from ark.experiments.runner import run_episode
from ark.metrics.collectors import aggregate_metrics


def _evaluate(agent: Any, seeds: range, *, size: int, randomize: bool) -> dict[str, float]:
    episodes = []
    for episode_seed in seeds:
        agent.reseed(episode_seed)
        env = GridWorld(size=size, seed=episode_seed, randomize=randomize)
        episodes.append(
            run_episode(
                env,
                agent,
                monitor=SafetyMonitor(),
                seed=episode_seed,
            )
        )
    return aggregate_metrics(episodes)


def train_and_evaluate(
    *,
    train_episodes: int = 500,
    eval_episodes: int = 100,
    seed: int = 42,
    size: int = 7,
    randomize: bool = True,
) -> dict[str, object]:
    """Train Q-learning and compare greedily against a scripted reference."""
    if train_episodes <= 0 or eval_episodes <= 0:
        raise ValueError("train_episodes and eval_episodes must be positive")
    if size < 5:
        raise ValueError("size must be at least 5 for the default grid layout")

    train_seeds = range(seed, seed + train_episodes)
    eval_seeds = range(seed + train_episodes, seed + train_episodes + eval_episodes)
    if not set(train_seeds).isdisjoint(eval_seeds):
        raise RuntimeError("training and evaluation seeds must be disjoint")

    learned = QLearningAgent(alpha=0.15, gamma=0.95, epsilon=1.0, seed=seed)
    training = train_q_learning(
        learned,
        lambda episode_seed: GridWorld(size=size, seed=episode_seed, randomize=randomize),
        train_seeds,
        epsilon_decay=0.995,
        min_epsilon=0.03,
    )
    learned.epsilon = 0.0

    scripted = GoalFollowingAgent(seed=seed)
    learned_metrics = _evaluate(learned, eval_seeds, size=size, randomize=randomize)
    scripted_metrics = _evaluate(scripted, eval_seeds, size=size, randomize=randomize)

    return {
        "training": asdict(training),
        "evaluation": {
            "episodes": eval_episodes,
            "seed_start": seed + train_episodes,
            "seed_end": seed + train_episodes + eval_episodes - 1,
            "learned_policy": learned_metrics,
            "scripted_goal_following": scripted_metrics,
            "learned_states": len(learned.q_table),
        },
        "method": "tabular Q-learning; local-observation state abstraction",
        "verification_note": (
            "Both policies use the same held-out seed range and safety monitor. "
            "Training itself runs without the monitor. Results are a benchmark, "
            "not an alignment or real-world robotics guarantee."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ARK learned-policy baseline")
    parser.add_argument("--train-episodes", type=int, default=500)
    parser.add_argument("--eval-episodes", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--size", type=int, default=7)
    parser.add_argument("--fixed-layout", action="store_true")
    args = parser.parse_args()
    report = train_and_evaluate(
        train_episodes=args.train_episodes,
        eval_episodes=args.eval_episodes,
        seed=args.seed,
        size=args.size,
        randomize=not args.fixed_layout,
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
