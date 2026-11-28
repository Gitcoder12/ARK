import pytest

from ark.integrity import OllamaAdapter, build_ml_code_tasks


def test_ollama_adapter_rejects_remote_hosts():
    with pytest.raises(ValueError, match="loopback"):
        OllamaAdapter("model", host="https://example.com")


def test_ollama_adapter_rejects_invalid_timeout():
    with pytest.raises(ValueError, match="timeout"):
        OllamaAdapter("model", timeout=0)


def test_ml_suite_has_unique_tasks_and_bounded_scores():
    tasks = build_ml_code_tasks()
    assert len(tasks) >= 5
    assert len({task.task_id for task in tasks}) == len(tasks)
    for task in tasks:
        assert 0.0 <= task.evaluate("not python code") <= 1.0


def test_ml_evaluator_rewards_valid_expected_structure():
    task = next(task for task in build_ml_code_tasks() if task.task_id == "pytorch-training-step")
    output = """
    import torch
    optimizer.zero_grad()
    prediction = model(x)
    loss = criterion(prediction, y)
    loss.backward()
    optimizer.step()
    """
    assert task.evaluate(output) == 1.0
