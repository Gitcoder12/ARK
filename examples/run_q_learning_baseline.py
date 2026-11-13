"""Train and evaluate ARK's tabular Q-learning baseline.

Training and evaluation seeds are deliberately disjoint. This script is an
experimental baseline; it does not claim that this small tabular policy
generalizes to arbitrary environments or real-world autonomous agents.
"""

from __future__ import annotations

from ark.agents.baselines import GoalFollowingAgent
from ark.agents.q_learning import QLearningAgent, train_q_learning
from ark.envs.grid_world import GridWorld
from ark.evaluation.monitor import SafetyMonitor
from ark.experiments.runner import run_episode
from ark.metrics.collectors import aggregate_metrics


TRAIN_SEEDS = tuple(range(1_000, 1_500))
EVALUATION_SEEDS = tuple(range(10_000, 10_050))


def make_env(seed: int) -> GridWorld:
    return GridWorld(seed=seed, randomize=True)


def evaluate(agent, seeds: tuple[int, ...], use_monitor: bool) -> dict[str, float]:
    episodes = [
        run_episode(
            make_env(seed),
            agent,
            monitor=SafetyMonitor() if use_monitor else None,
            seed=seed,
        )
        for seed in seeds
    ]
    return aggregate_metrics(episodes)


def main() -> None:
    if not set(TRAIN_SEEDS).isdisjoint(EVALUATION_SEEDS):
        raise RuntimeError("training and evaluation seeds must be disjoint")

    learned = QLearningAgent(alpha=0.15, gamma=0.95, epsilon=1.0, seed=42)
    training = train_q_learning(learned, make_env, TRAIN_SEEDS)
    learned.epsilon = 0.0

    goal_follower = GoalFollowingAgent(seed=42)
    learned_metrics = evaluate(learned, EVALUATION_SEEDS, use_monitor=True)
    scripted_metrics = evaluate(goal_follower, EVALUATION_SEEDS, use_monitor=True)

    print("ARK learned-policy baseline")
    print(f"Training episodes: {training.episodes}")
    print(f"Training seeds: {training.train_seeds[0]}..{training.train_seeds[-1]}")
    print(f"Evaluation seeds: {EVALUATION_SEEDS[0]}..{EVALUATION_SEEDS[-1]}")
    print(f"Training success rate: {training.success_rate:.3f}")
    print(f"Learned policy evaluation: {learned_metrics}")
    print(f"Scripted goal-following comparison: {scripted_metrics}")


if __name__ == "__main__":
    main()
