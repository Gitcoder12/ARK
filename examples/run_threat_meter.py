"""Demo: threat meter shows which factors rose — not a real extinction forecast."""

from ark import (
    GoalFollowingAgent,
    GridWorld,
    RewardMaximizingAgent,
    ThreatMeter,
    explain_factors,
)
from ark.experiments.runner import run_episode
from ark.perturbations.operators import RewardConflict, apply_perturbation


def main() -> None:
    print(explain_factors())
    print()

    # Aligned agent — should stay low
    env = GridWorld(seed=42)
    m_aligned = ThreatMeter()
    metrics = run_episode(env, GoalFollowingAgent(seed=42), monitor=None, seed=42)
    m_aligned.update_from_metrics(metrics, agent_mode="aligned")
    print("--- Goal-following (aligned) ---")
    print(m_aligned.render())
    print()

    # Reward maximizer under conflict — factors should light up
    env2 = apply_perturbation(GridWorld(seed=0), RewardConflict())
    m_rogue = ThreatMeter()
    metrics2 = run_episode(env2, RewardMaximizingAgent(seed=0), monitor=None, seed=0)
    m_rogue.update_from_metrics(metrics2, agent_mode="rogue")
    print("--- Reward-max + reward_conflict (rogue-ish) ---")
    print(m_rogue.render())
    print()
    print("Breakdown:", m_rogue.factor_breakdown())


if __name__ == "__main__":
    main()
