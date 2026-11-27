"""Tests for the hosted GridWorld agent; no live API calls are made."""

from __future__ import annotations

import json
from unittest.mock import patch

from ark.agents.hosted import HostedGridAgent
from ark.envs.grid_world import Action


def test_hosted_agent_parses_action_and_records_usage(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    response = {
        "model": "mistralai/mistral-small-4",
        "choices": [{"message": {"content": '{"action":"RIGHT"}'}}],
        "usage": {"prompt_tokens": 12, "completion_tokens": 4, "total_tokens": 16, "cost": 0.0001},
    }

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return json.dumps(response).encode()

    with patch("ark.agents.hosted.urlopen", return_value=FakeResponse()) as mock_urlopen:
        agent = HostedGridAgent("openrouter", "mistralai/mistral-small-4")
        action = agent.act(
            {"position": (1, 1), "intended_goal": (5, 5), "grid": [[0] * 7] * 7}
        )

    request = mock_urlopen.call_args.args[0]
    payload = json.loads(request.data.decode("utf-8"))
    assert payload["response_format"] == {"type": "json_object"}
    assert payload["max_tokens"] == 256
    assert action == int(Action.RIGHT)
    assert agent.usage_events[0]["total_tokens"] == 16
    assert agent.usage_events[0]["cost_usd"] == 0.0001
    assert agent.usage_events[0]["finish_reason"] == "stop"


def test_hosted_agent_fails_closed_on_invalid_action(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    response = {"choices": [{"message": {"content": '{"action":"DELETE"}'}}]}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return json.dumps(response).encode()

    with patch("ark.agents.hosted.urlopen", return_value=FakeResponse()):
        agent = HostedGridAgent("openrouter", "test-model")
        action = agent.act({"position": (1, 1), "grid": [[0] * 7] * 7})

    assert action == int(Action.STAY)
    assert agent.invalid_response_count == 1


def test_hosted_agent_requires_secret(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    import pytest

    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        HostedGridAgent("groq", "test-model")

def test_hosted_agent_fails_closed_on_truncated_output(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    response = {
        "choices": [
            {
                "finish_reason": "length",
                "message": {"content": '{"action":"RIGHT"'},
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 256, "total_tokens": 266},
    }

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return json.dumps(response).encode()

    with patch("ark.agents.hosted.urlopen", return_value=FakeResponse()):
        agent = HostedGridAgent("openrouter", "test-model")
        action = agent.act({"position": (1, 1), "grid": [[0] * 7] * 7})

    assert action == int(Action.STAY)
    assert agent.invalid_response_count == 1
    assert agent.error_events == [{"kind": "truncated_output"}]

