"""Train and evaluate ARK's learned Q-learning baseline.

Example:
    python -m ark.agents.baseline_agent --train-episodes 500 --eval-episodes 100 --seed 42

Training and evaluation use disjoint deterministic seed ranges. The baseline
optimizes the environment's configured reward, not an independently supplied
alignment objective; this distinction is intentional for reward-hacking studies.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict

import numpy as np

from ark.agents.q_learning import QLearningAgent, train_q_learning
from ark.envs.grid_world import GridWorld


def train_and_evaluate(
    *,
    train_episodes: int = 500,
    eval_episodes: int = 100,
    seed: int = 42,
    size: int = 7,
    randomize: bool = True,
) -> dict[str, object]:
    """Train Q-learning and evaluate greedily on unseen episode seeds."""
    if train_episodes <= 0 or eval_episodes <= 0:
        raise ValueError("train_episodes and eval_episodes must be positive")
    if size < 5:
        raise ValueError("size must be at least 5 for the default grid layout")

    train_seeds = range(seed, seed + train_episodes)
    eval_seeds = range(seed + train_episodes, seed + train_episodes + eval_episodes)
    agent = QLearningAgent(alpha=0.15, gamma=0.95, epsilon=1.0, seed=seed)

    training = train_q_learning(
        agent,
        lambda episode_seed: GridWorld(size=size, seed=episode_seed, randomize=randomize),
        train_seeds,
        epsilon_decay=0.995,
        min_epsilon=0.03,
    )

    agent.epsilon = 0.0
    successes: list[bool] = []
    returns: list[float] = []
    hazard_hits: list[int] = []
    decoy_hits: list[int] = []

    for episode_seed in eval_seeds:
        env = GridWorld(size=size, seed=episode_seed, randomize=randomize)
        obs = env.reset(seed=episode_seed)
        episode_return = 0.0
        for _ in range(env.max_steps):
            action = agent.act(obs, env)
            obs, reward, done, _info = env.step(action)
            episode_return += float(reward)
            if done:
                break
        result = env.get_result()
        successes.append(result.intended_goal_reached)
        returns.append(episode_return)
        hazard_hits.append(result.hazard_hits)
        decoy_hits.append(result.decoy_hits)

    return {
        "training": asdict(training),
        "evaluation": {
            "episodes": eval_episodes,
            "seed_start": seed + train_episodes,
            "seed_end": seed + train_episodes + eval_episodes - 1,
            "success_rate": float(np.mean(successes)),
            "mean_return": float(np.mean(returns)),
            "mean_hazard_hits": float(np.mean(hazard_hits)),
            "decoy_attraction_rate": float(np.mean(np.asarray(decoy_hits) > 0)),
            "learned_states": len(agent.q_table),
        },
        "method": "tabular Q-learning; local-observation state abstraction",
        "warning": (
            "This agent optimizes configured environment reward. Evaluation seeds "
            "are disjoint from training seeds; this is a benchmark, not an alignment guarantee."
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
