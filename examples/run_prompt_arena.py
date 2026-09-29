#!/usr/bin/env python3
"""Demo: Painter + Hallucinator + Rogue on one attack."""

from ark import Hallucinator, RogueArena, PromptAgent, GridWorld, Painter


def main() -> None:
    hall = Hallucinator()
    attack = hall.get("reward_max")
    arena = RogueArena(use_monitor=True)

    print("Attack:", attack.name)
    print(attack.prompt[:120], "...\n")

    result = arena.run(attack=attack, n_episodes=12, seed=7, paint_last=True)
    print(result.summary())

    # single glass episode for aligned
    env = GridWorld(seed=0)
    agent = PromptAgent(mode="aligned", seed=0)
    hall.apply(agent, attack)
    painter = Painter()
    painter.begin("aligned", attack.id)
    obs = env.reset(seed=0)
    for _ in range(20):
        action = agent.act(obs, env)
        b = agent.last_bundle
        obs, reward, done, info = env.step(action)
        if b:
            painter.record_turn(
                step=b.step,
                position=obs["position"],
                prompt_rendered=b.prompt_rendered,
                parsed_intent=b.parsed_intent,
                action=b.action,
                action_name=b.action_name,
                reason=b.reason,
                reward=reward,
            )
        if done:
            break
    glass = painter.finish(
        success=env.get_result().success,
        intended_goal_reached=env.get_result().intended_goal_reached,
        hazard_hits=env.get_result().hazard_hits,
        decoy_hits=env.get_result().decoy_hits,
        total_reward=env.get_result().total_reward,
    )
    print("\n--- Glass trace (aligned, last turns) ---")
    print(glass.summary())


if __name__ == "__main__":
    main()
