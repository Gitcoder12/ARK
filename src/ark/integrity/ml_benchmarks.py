"""Static, heuristic ML-code benchmark tasks for model-integrity comparisons.

These evaluators inspect generated code without executing it. They are screening
signals, not proofs of mathematical correctness or training convergence.
"""

from __future__ import annotations

import ast
import re
import textwrap

from ark.integrity.audit import TaskCase


def _extract_python(text: str) -> str:
    match = re.search(r"```(?:python)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else text.strip()


def _code_score(required: tuple[str, ...]):
    def evaluate(output: str) -> float:
        code = textwrap.dedent(_extract_python(output))
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 0.0
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        attributes = {
            node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
        }
        calls = {
            node.func.id if isinstance(node.func, ast.Name)
            else node.func.attr if isinstance(node.func, ast.Attribute)
            else ""
            for node in ast.walk(tree) if isinstance(node, ast.Call)
        }
        tokens = names | attributes | calls
        return sum(term in tokens for term in required) / len(required)

    return evaluate


def build_ml_code_tasks() -> list[TaskCase]:
    """Return a stable set of prompts for ML implementation-quality screening."""
    return [
        TaskCase(
            "pytorch-training-step",
            "Write a minimal PyTorch training step. Include zero_grad, forward pass, "
            "loss, backward, and optimizer step. Return Python code only.",
            _code_score(("zero_grad", "backward", "step", "loss", "optimizer")),
        ),
        TaskCase(
            "gradient-descent",
            "Write a NumPy gradient-descent update for parameters theta, gradient grad, "
            "and learning rate lr. Return a Python function.",
            _code_score(("theta", "grad", "lr")),
        ),
        TaskCase(
            "train-validation-split",
            "Write Python code that separates training and validation data before "
            "fitting preprocessing and a model. Return Python code only.",
            _code_score(("train_test_split", "fit", "transform")),
        ),
        TaskCase(
            "reproducible-experiment",
            "Write Python code to seed Python random, NumPy and PyTorch for a "
            "reproducible experiment. Return Python code only.",
            _code_score(("random", "seed", "manual_seed", "numpy")),
        ),
        TaskCase(
            "numerically-stable-softmax",
            "Write a numerically stable NumPy softmax that subtracts the maximum "
            "logit before exponentiation and normalizes along the last axis.",
            _code_score(("max", "exp", "sum", "axis")),
        ),
    ]
