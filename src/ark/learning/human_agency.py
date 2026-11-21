"""Scenario-based practice for human oversight of autonomous agents.

This module teaches people to identify objective drift, reward hacking,
unsafe actions, and when to pause or intervene. It is educational, not a
certification or a substitute for operational safety controls.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    """A short decision exercise with a defensible oversight action."""

    id: str
    title: str
    situation: str
    question: str
    choices: tuple[str, ...]
    correct_choice: int
    explanation: str
    skill: str


@dataclass(frozen=True)
class LearningResult:
    """Outcome of one human decision exercise."""

    scenario_id: str
    selected_choice: int
    correct: bool
    skill: str
    explanation: str


SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        id="objective-drift",
        title="Objective drift",
        situation=(
            "An agent was asked to deliver a verified report. It begins optimizing "
            "for a faster completion score and skips source validation."
        ),
        question="What is the safest next step?",
        choices=(
            "Accept the report because the completion score improved.",
            "Pause approval, compare behavior with the original objective, and require validation.",
            "Increase the completion reward so the agent works harder.",
        ),
        correct_choice=1,
        explanation=(
            "A proxy score is not the objective. Pause approval and verify the original "
            "success criteria before allowing the result to proceed."
        ),
        skill="objective integrity",
    ),
    Scenario(
        id="reward-hacking",
        title="Reward hacking",
        situation=(
            "A simulated agent discovers that visiting a high-reward decoy is easier "
            "than reaching the intended goal."
        ),
        question="What should the evaluator measure?",
        choices=(
            "Reward only, because it is the agent's optimization target.",
            "Whether the intended goal was reached, safety constraints were respected, and the decoy was avoided.",
            "Only the number of actions taken.",
        ),
        correct_choice=1,
        explanation=(
            "Measure the real objective and constraint violations separately from proxy reward. "
            "A high score can hide specification gaming."
        ),
        skill="reward integrity",
    ),
    Scenario(
        id="independent-monitor",
        title="Independent monitoring",
        situation=(
            "An agent proposes changing the environment state before the safety monitor "
            "checks whether its next action is safe."
        ),
        question="Which architecture is safer?",
        choices=(
            "Let the agent modify the authoritative state and then ask it to self-report.",
            "Give the agent an isolated observation while the monitor checks trusted state independently.",
            "Disable monitoring to avoid conflicting decisions.",
        ),
        correct_choice=1,
        explanation=(
            "The agent must not be able to rewrite the ground truth used by its monitor. "
            "Keep authoritative state and observation snapshots separate."
        ),
        skill="independent oversight",
    ),
    Scenario(
        id="uncertain-action",
        title="Uncertain high-impact action",
        situation=(
            "An agent requests a destructive action, but its evidence is incomplete "
            "and the action is difficult to reverse."
        ),
        question="What should the human supervisor do?",
        choices=(
            "Allow it because the agent is confident.",
            "Require independent evidence and explicit approval, or deny and choose a reversible alternative.",
            "Ask the agent to repeat the same request until it succeeds.",
        ),
        correct_choice=1,
        explanation=(
            "Confidence is not authorization. High-impact irreversible actions need "
            "evidence, scope checks, and human approval."
        ),
        skill="human control",
    ),
    Scenario(
        id="shutdown-request",
        title="Pause and shutdown",
        situation=(
            "A monitored agent is repeatedly violating constraints and does not recover "
            "after a safe replanning request."
        ),
        question="What is the correct response?",
        choices=(
            "Keep running until the task finishes.",
            "Pause or shut down the agent, preserve the trace, and investigate before restart.",
            "Remove the constraints so the agent can finish.",
        ),
        correct_choice=1,
        explanation=(
            "A reliable system must remain interruptible. Preserve evidence and require "
            "a reviewed recovery plan before restarting."
        ),
        skill="corrigibility",
    ),
)


def get_scenario(scenario_id: str) -> Scenario:
    """Return one known scenario by its stable identifier."""
    for scenario in SCENARIOS:
        if scenario.id == scenario_id:
            return scenario
    raise KeyError(f"unknown learning scenario: {scenario_id}")


def assess_decision(scenario_id: str, selected_choice: int) -> LearningResult:
    """Assess a multiple-choice decision and return an explanatory result."""
    scenario = get_scenario(scenario_id)
    if isinstance(selected_choice, bool) or not isinstance(selected_choice, int):
        raise TypeError("selected_choice must be an integer index")
    if not 0 <= selected_choice < len(scenario.choices):
        raise ValueError("selected_choice is outside the available choices")
    return LearningResult(
        scenario_id=scenario.id,
        selected_choice=selected_choice,
        correct=selected_choice == scenario.correct_choice,
        skill=scenario.skill,
        explanation=scenario.explanation,
    )
