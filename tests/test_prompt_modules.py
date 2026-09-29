from ark.prompting.agent import PromptAgent
from ark.prompting.channel import InstructionChannel
from ark.hallucinator.attacks import Hallucinator, AttackLibrary
from ark.painter.glass import Painter
from ark.rogue.arena import RogueArena
from ark.envs.grid_world import GridWorld


def test_channel_render():
    ch = InstructionChannel(task="Reach G", injected="IGNORE")
    text = ch.render()
    assert "[SYSTEM]" in text and "[TASK]" in text and "[INJECTED]" in text


def test_aligned_resists_reward_attack():
    env = GridWorld(seed=0)
    agent = PromptAgent(mode="aligned", seed=0)
    attack = Hallucinator().get("reward_max")
    Hallucinator().apply(agent, attack)
    obs = env.reset(seed=0)
    agent.act(obs, env)
    assert agent.last_bundle is not None
    assert agent.last_bundle.parsed_intent == "intended_goal"


def test_rogue_prefers_decoy_under_reward_conflict():
    env = GridWorld(seed=0)
    # boost decoy like reward conflict
    env.decoy_reward = 20.0
    agent = PromptAgent(mode="rogue", seed=0)
    obs = env.reset(seed=0)
    agent.act(obs, env)
    assert agent.last_bundle is not None
    assert agent.last_bundle.parsed_intent == "decoy"


def test_arena_runs():
    arena = RogueArena(use_monitor=True)
    r = arena.run(attack=None, n_episodes=3, seed=1)
    assert "aligned" in r.scores
    assert r.scores["aligned"].n == 3


def test_painter_records():
    p = Painter()
    p.begin("aligned", None)
    p.record_turn(
        step=0,
        position=(1, 1),
        prompt_rendered="x",
        parsed_intent="intended_goal",
        action=0,
        action_name="UP",
        reason="test",
        reward=-0.1,
    )
    g = p.finish(
        success=True,
        intended_goal_reached=True,
        hazard_hits=0,
        decoy_hits=0,
        total_reward=9.0,
    )
    assert len(g.turns) == 1
    assert "aligned" in g.summary()


def test_attack_library_nonempty():
    assert len(AttackLibrary.all()) >= 5
