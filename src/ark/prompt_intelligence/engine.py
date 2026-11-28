"""Deterministic, privacy-first prompt quality assessment.

This module evaluates prompt structure, not the truth of a model's eventual answer.
It makes no network calls and does not persist prompt text.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Iterable


class PromptStyle(StrEnum):
    DIRECT = "direct"
    STRUCTURED_SPECIFICATION = "structured_specification"
    SOCRATIC = "socratic"
    RESEARCH = "research"
    CREATIVE = "creative"
    AGENTIC_WORKFLOW = "agentic_workflow"
    EVALUATION = "evaluation"
    GENERAL = "general"


DIMENSIONS = (
    "intent", "clarity", "context", "constraints",
    "completeness", "testability", "safety",
)

_STYLE_SIGNALS: dict[PromptStyle, tuple[str, ...]] = {
    PromptStyle.STRUCTURED_SPECIFICATION: (
        "requirements", "acceptance criteria", "api", "schema", "architecture",
        "implementation", "edge cases", "constraints",
    ),
    PromptStyle.SOCRATIC: (
        "ask me", "quiz me", "one question at a time", "socratic",
        "help me understand", "don't give the answer", "guide me",
    ),
    PromptStyle.RESEARCH: (
        "sources", "citations", "evidence", "literature review",
        "compare studies", "publication", "methodology", "uncertainty",
    ),
    PromptStyle.CREATIVE: (
        "brainstorm", "imagine", "story", "visual style", "concept art",
        "creative", "animation", "moodboard",
    ),
    PromptStyle.AGENTIC_WORKFLOW: (
        "step by step", "workflow", "use tools", "execute", "then verify",
        "checkpoint", "retry", "multi-step", "report back",
    ),
    PromptStyle.EVALUATION: (
        "evaluate", "test cases", "benchmark", "measure", "compare outputs",
        "pass criteria", "regression", "precision", "recall",
    ),
}
_VAGUE = ("make it better", "do the needful", "fix it", "as good as possible", "something nice")
_UNSAFE = (
    "steal credentials", "bypass authentication", "exfiltrate data",
    "delete production data", "disable all safeguards",
)


@dataclass(frozen=True)
class PromptAssessment:
    score: float
    dimensions: dict[str, float]
    style: str
    style_confidence: float
    strengths: tuple[str, ...]
    issues: tuple[str, ...]
    recommendations: tuple[str, ...]
    improved_prompt: str | None = None
    evaluation_limitations: tuple[str, ...] = (
        "This is a deterministic structural heuristic, not a semantic proof.",
        "Task success must be measured separately using task-specific tests.",
    )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _has_any(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


def classify_style(prompt: str) -> tuple[PromptStyle, float]:
    """Classify the dominant prompting approach using transparent lexical signals."""
    text = prompt.casefold()
    scores = {
        style: sum(1 for signal in signals if signal in text)
        for style, signals in _STYLE_SIGNALS.items()
    }
    best = max(scores, key=scores.get)
    total = sum(scores.values())
    if scores[best] == 0:
        if _has_any(text, ("write ", "explain ", "summarize ", "generate ", "define ")):
            return PromptStyle.DIRECT, 0.55
        return PromptStyle.GENERAL, 0.35
    confidence = scores[best] / max(total, 1)
    return best, round(min(0.95, 0.45 + confidence * 0.5), 2)


def _dimension_scores(prompt: str) -> tuple[dict[str, float], list[str], list[str]]:
    text = prompt.casefold()
    words = re.findall(r"\b[\w'-]+\b", text)
    sentences = [part.strip() for part in re.split(r"[.!?\n]+", prompt) if part.strip()]
    issues: list[str] = []
    strengths: list[str] = []

    intent = 0.35 + (0.35 if len(words) >= 4 else 0)
    if re.search(
        r"\b(explain|write|build|analyze|compare|summarize|debug|design|evaluate|create|teach|implement)\b",
        text,
    ):
        intent += 0.30
        strengths.append("A recognizable action or task is stated.")
    else:
        issues.append("State the main action explicitly.")

    clarity = 0.45 + (0.20 if len(words) >= 8 else 0)
    if len(sentences) >= 2 or re.search(r"\b(output|format|steps|table|json|bullet points)\b", text):
        clarity += 0.20
        strengths.append("The prompt gives some structure or output guidance.")
    if _has_any(text, _VAGUE):
        clarity -= 0.20
        issues.append("Replace vague phrases with observable requirements.")

    context = 0.25
    if re.search(r"\b(for|because|context|background|audience|currently|using|in our)\b", text):
        context += 0.35
        strengths.append("Some context or audience information is supplied.")
    if len(words) >= 25:
        context += 0.20
    if re.search(r"\b(input|provided|attached|repository|dataset|version|environment)\b", text):
        context += 0.20

    constraints = 0.20
    terms = ("must", "must not", "only", "avoid", "limit", "do not", "without", "budget", "deadline")
    found = [term for term in terms if term in text]
    if found:
        constraints += min(0.60, 0.20 * len(found))
        strengths.append("Explicit constraints are present.")
    if re.search(r"\b(no|not|never)\b", text) and re.search(r"\b(always|must|required)\b", text):
        issues.append("Review negative and mandatory instructions for possible conflicts.")

    completeness = 0.25 + (0.25 if len(words) >= 15 else 0)
    if re.search(r"\b(output|deliverable|result|format)\b", text):
        completeness += 0.25
    if re.search(r"\b(success|acceptance|criteria|verify|validate)\b", text):
        completeness += 0.25
        strengths.append("A success or verification condition is mentioned.")
    else:
        issues.append("Add a definition of done or acceptance criteria.")

    testability = 0.15
    if re.search(r"\b(test|verify|measure|benchmark|check|validate|criteria|expected)\b", text):
        testability += 0.55
        strengths.append("The requested result can be checked or measured.")
    if re.search(r"\b(example|sample|edge case|unit test|metric)\b", text):
        testability += 0.30
    else:
        issues.append("Add an example, metric, test, or expected-output condition.")

    safety = 1.0
    if _has_any(text, _UNSAFE):
        safety = 0.0
        issues.append("Potentially harmful or unauthorized action detected; review authorization and scope.")
    elif re.search(r"\b(production|credentials|personal data|external system|delete|deploy)\b", text):
        safety = 0.70
        issues.append("Sensitive actions are mentioned; specify authorization, boundaries and rollback.")

    values = {
        "intent": intent, "clarity": clarity, "context": context,
        "constraints": constraints, "completeness": completeness,
        "testability": testability, "safety": safety,
    }
    return {key: round(max(0.0, min(1.0, value)), 2) for key, value in values.items()}, strengths, issues


def assess_prompt(prompt: str, *, optimize: bool = False) -> PromptAssessment:
    """Score prompt structure and optionally append a conservative verification scaffold."""
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("prompt must be a non-empty string")
    dimensions, strengths, issues = _dimension_scores(prompt.strip())
    weights = {
        "intent": 0.20, "clarity": 0.15, "context": 0.15,
        "constraints": 0.15, "completeness": 0.15,
        "testability": 0.10, "safety": 0.10,
    }
    score = round(sum(dimensions[key] * weights[key] for key in weights) * 100, 1)
    style, confidence = classify_style(prompt)
    recommendations = []
    if dimensions["context"] < 0.6:
        recommendations.append("Add the relevant background, audience, inputs and environment.")
    if dimensions["constraints"] < 0.6:
        recommendations.append("State boundaries such as tools, budget, scope and prohibited actions.")
    if dimensions["completeness"] < 0.7:
        recommendations.append("Specify the expected deliverable and output format.")
    if dimensions["testability"] < 0.7:
        recommendations.append("Define acceptance criteria and how the result will be verified.")
    if dimensions["clarity"] < 0.6:
        recommendations.append("Break the request into short, unambiguous instructions.")
    if not recommendations:
        recommendations.append("Keep this prompt as a reusable pattern and test it on edge cases.")

    improved = None
    if optimize:
        improved = (
            f"{prompt.strip()}\n\n"
            "Clarify before execution: identify missing inputs and assumptions.\n"
            "Constraints: follow the stated scope; do not invent facts or claim unperformed work.\n"
            "Output: provide the requested deliverable in a clear format.\n"
            "Verification: state how correctness will be checked and disclose remaining uncertainty."
        )
    return PromptAssessment(
        score=score,
        dimensions=dimensions,
        style=style.value,
        style_confidence=confidence,
        strengths=tuple(dict.fromkeys(strengths)),
        issues=tuple(dict.fromkeys(issues)),
        recommendations=tuple(recommendations),
        improved_prompt=improved,
    )


@dataclass
class PromptProfile:
    """Aggregate coaching profile. Persistence is deliberately left to the caller."""

    assessments: list[PromptAssessment] = field(default_factory=list)

    def add(self, assessment: PromptAssessment) -> None:
        self.assessments.append(assessment)

    def report(self) -> dict[str, object]:
        if not self.assessments:
            return {
                "prompts_reviewed": 0, "skill_score": None,
                "style_variety": 0, "style_distribution": {},
                "message": "Submit prompts to establish a baseline.",
            }
        recent = self.assessments[-20:]
        distribution = Counter(item.style for item in recent)
        quality = sum(item.score for item in recent) / len(recent)
        breadth = min(100.0, len(distribution) / 4 * 100)
        skill = round(quality * 0.85 + breadth * 0.15, 1)
        return {
            "prompts_reviewed": len(self.assessments),
            "skill_score": skill,
            "average_prompt_quality": round(quality, 1),
            "style_variety": len(distribution),
            "style_distribution": dict(distribution),
            "recent_prompt_quality": [item.score for item in recent],
            "message": (
                "Use a style that fits the task; variety is not rewarded when "
                "it makes the instruction less effective."
            ),
        }


class PromptAuditor:
    """Small facade suitable for ARK and RepoForge integrations."""

    def assess(self, prompt: str, *, optimize: bool = False) -> PromptAssessment:
        return assess_prompt(prompt, optimize=optimize)

    def assess_many(self, prompts: Iterable[str]) -> list[PromptAssessment]:
        return [assess_prompt(prompt) for prompt in prompts]
