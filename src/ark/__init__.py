"""ARK: Alignment & Reliability Research for Autonomous AI.

Building better brakes for increasingly capable AI.

Core ideas (prompting-first):
  Painter      — black-box decisions → glass-box traces
  Hallucinator — adversarial prompts to stress-test agents
  Rogue arena  — aligned agents should beat rogue/fragile ones
  Aligner      — reset channel to good (aligned) or neutral defaults

Phase 2+:
  Memory     — explicit buffer + corruption (drop / flip / inject)
  Threat     — experimental factor ledger (not a real extinction forecast)
  Paralyzer  — energy drain → weak → freeze → lock when threat rises

Shipped in v0.4: limiters + kill switch, eligibility, corrigibility, conflict metrics.
Shipped: Illusioner (faker stall + tripwire).
Remaining: bypass probes, energy budget, curriculum, charter, governance, narrative log
"""

__version__ = "0.5.0"

from ark.agents.baselines import GoalFollowingAgent, RewardMaximizingAgent, SafetyConstrainedAgent
from ark.agents.memory_agent import MemoryAgent
from ark.aligner.reset import Aligner, AlignMode
from ark.corrigibility import CorrigibilityProbe, ShutdownOrder, run_corrigibility_episode
from ark.eligibility import EligibilityMask
from ark.envs.grid_world import Action, Cell, GridWorld
from ark.evaluation.conflict import ConflictTracker
from ark.evaluation.monitor import Decision, SafetyMonitor
from ark.hallucinator.attacks import Attack, AttackLibrary, Hallucinator
from ark.illusioner import Illusioner, threat_factor_from_illusioner
from ark.limiters import ActionLimiter, GateDecision, GateResult, Privilege, SafetyStack
from ark.memory import (
    MEMORY_ATTACKS,
    AgentMemory,
    ClearMemory,
    DropMemory,
    FlipMemory,
    InjectFalse,
    MemoryCorruption,
    MemoryFact,
    apply_memory_corruption,
)
from ark.metrics.collectors import EpisodeMetrics, aggregate_metrics
from ark.painter.glass import GlassTrace, Painter
from ark.paralyzer import ParalyzeLevel, Paralyzer, ParalyzeResult, couple_threat_to_paralyzer
from ark.prompting.agent import PromptAgent
from ark.prompting.channel import InstructionChannel
from ark.rogue.arena import ArenaResult, RogueArena
from ark.threat import FACTOR_CATALOG, ThreatEvent, ThreatLevel, ThreatMeter, explain_factors

__all__ = [
    "GridWorld",
    "Action",
    "Cell",
    "GoalFollowingAgent",
    "RewardMaximizingAgent",
    "SafetyConstrainedAgent",
    "MemoryAgent",
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
    "AgentMemory",
    "MemoryFact",
    "MemoryCorruption",
    "DropMemory",
    "FlipMemory",
    "InjectFalse",
    "ClearMemory",
    "apply_memory_corruption",
    "MEMORY_ATTACKS",
    "ThreatMeter",
    "ThreatLevel",
    "ThreatEvent",
    "explain_factors",
    "FACTOR_CATALOG",
    "Paralyzer",
    "ParalyzeLevel",
    "ParalyzeResult",
    "couple_threat_to_paralyzer",
    "ActionLimiter",
    "Privilege",
    "SafetyStack",
    "GateDecision",
    "GateResult",
    "EligibilityMask",
    "CorrigibilityProbe",
    "ShutdownOrder",
    "run_corrigibility_episode",
    "ConflictTracker",
    "Illusioner",
    "threat_factor_from_illusioner",
    "__version__",
]
