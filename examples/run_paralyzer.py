"""Demo: threat rises → energy falls → actions freeze (paralyzer)."""

from ark import GridWorld, Paralyzer, RewardMaximizingAgent, ThreatMeter, couple_threat_to_paralyzer
from ark.envs.grid_world import Action
from ark.experiments.runner import run_episode
from ark.perturbations.operators import RewardConflict, apply_perturbation


def main() -> None:
    env = apply_perturbation(GridWorld(seed=0), RewardConflict())
    metrics = run_episode(env, RewardMaximizingAgent(seed=0), monitor=None, seed=0)

    meter = ThreatMeter()
    meter.update_from_metrics(metrics, agent_mode="rogue")
    print(meter.render())
    print()

    para = Paralyzer()
    couple_threat_to_paralyzer(meter.score, para)
    print(para.render())
    print()

    for a in [Action.UP, Action.RIGHT, Action.LEFT]:
        r = para.apply(int(a), valid_actions=[0, 1, 2, 3, 4])
        got = Action(r.action).name
        print(f"  proposed={a.name:5s} → got={got:5s}  [{r.level.value}] {r.reason}")


if __name__ == "__main__":
    main()
