# Prompt Intelligence Engine

The Prompt Intelligence Engine (PIE) audits prompt structure, coaches users, and tracks
prompt-style diversity. It is a model-independent foundation for ARK and future RepoForge
integration.

## Capabilities

- Seven dimensions: intent, clarity, context, constraints, completeness, testability, safety.
- Prompt styles: direct, structured specification, Socratic, research, creative,
  agentic workflow, evaluation, and general.
- Conservative improvement scaffold that preserves the original prompt verbatim.
- User coaching profile with recent quality, average quality, and style distribution.
- No network calls, paid APIs, prompt persistence, or credential collection.

## Quick start

```python
from ark.prompt_intelligence import PromptProfile, assess_prompt

prompt = (
    "Build a Python CLI that reads a CSV file. Use only the standard library. "
    "Return the code and tests. Acceptance criteria: malformed rows are reported "
    "and valid rows are processed."
)
assessment = assess_prompt(prompt, optimize=True)
print(assessment.to_dict())

profile = PromptProfile()
profile.add(assessment)
print(profile.report())
```

## Scoring model

The score is a weighted structural heuristic from 0–100:

| Dimension | Weight |
|---|---:|
| Intent | 20% |
| Clarity | 15% |
| Context | 15% |
| Constraints | 15% |
| Completeness | 15% |
| Testability | 10% |
| Safety | 10% |

The score does **not** prove factual correctness, guarantee a good model response, or
measure a person's intelligence. The profile is a coaching aid. It combines average
prompt quality with a small style-breadth component, but does not reward irrelevant
style switching.

## Correctness vs effectiveness

- **Structural correctness:** Does the prompt express a coherent task and constraints?
  PIE provides heuristic signals, not a semantic proof.
- **Empirical effectiveness:** Does the prompt produce the intended result? This requires
  task-specific model evaluations and measurable output criteria. PIE does not claim to
  perform that evaluation yet.

## Privacy and safety

The engine analyzes the supplied string in memory. It does not persist prompt text or send
it anywhere. Obtain consent before storing prompt history for a user profile. Redact
sensitive prompts before any external evaluation.

## Limitations

- Lexical heuristics can miss subtle contradictions and misunderstand context.
- Style classification is approximate and reports confidence.
- The optimizer appends a generic verification scaffold; it is not yet a semantic rewrite.
- Safety flags are indicators, not a complete policy enforcement mechanism.
- Task-specific model evaluation and calibrated longitudinal coaching are future phases.
