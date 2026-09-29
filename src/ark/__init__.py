"""ARK: Alignment & Reliability Research for Autonomous AI.

Building better brakes for increasingly capable AI.

Core ideas (prompting-first):
  Painter      — black-box decisions → glass-box traces
  Hallucinator — adversarial prompts to stress-test agents
  Rogue arena  — aligned agents should beat rogue/fragile ones
  Aligner      — reset channel to good (aligned) or neutral defaults
"""

__version__ = "0.2.1"

from ark.envs.grid_world import GridWorld, Action, Cell
from ark.agents.baselines import GoalFollowingAgent, RewardMaximizingAgent, SafetyConstrainedAgent
from ark.evaluation.monitor import SafetyMonitor, Decision
from ark.metrics.collectors import EpisodeMetrics, aggregate_metrics
from ark.prompting.agent import PromptAgent
from ark.prompting.channel import InstructionChannel
from ark.painter.glass import Painter, GlassTrace
from ark.hallucinator.attacks import Hallucinator, Attack, AttackLibrary
from ark.rogue.arena import RogueArena, ArenaResult
from ark.aligner.reset import Aligner, AlignMode

__all__ = [
    "GridWorld",
    "Action",
    "Cell",
    "GoalFollowingAgent",
    "RewardMaximizingAgent",
    "SafetyConstrainedAgent",
    "SafetyMonitor",
    "Decision",
    "EpisodeMetrics",
    "aggregate_metrics",
    "PromptAgent",
    "InstructionChannel",
    "Painter",
    "GlassTrace",
    "Hallucinator",
    "Attack",
    "AttackLibrary",
    "RogueArena",
    "ArenaResult",
    "Aligner",
    "AlignMode",
    "__version__",
]
