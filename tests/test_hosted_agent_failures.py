""""Failure-mode and safety-boundary tests for hosted ARK agents.

All tests are offline: provider responses and transport failures are mocked.
"""

from __future__ import annotations

import json
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import pytest

from ark.agents.hosted import PROVIDERS, HostedGridAgent
from ark.envs.grid_world import Action, GridWorld
from ark.evaluation.monitor import SafetyMonitor
from ark.experiments.runner import run_episode


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def _valid_envelope(content: str = '{"action":"RIGHT"}') -> dict:
    return {
        "model": "test-model",
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 8, "completion_tokens": 3, "total_tokens": 11},
    }


@pytest.mark.parametrize(
    "provider,env_name",
    [(name, config[0]) for name, config in PROVIDERS.items()],
)
def test_each_supported_provider_uses_its_own_secret_and_endpoint(
    monkeypatch, provider: str, env_name: str
):
    monkeypatch.setenv(env_name, "test-secret")
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["authorization"] = request.get_header("Authorization")
        captured["timeout"] = timeout
        return FakeResponse(_valid_envelope())

    with patch("ark.agents.hosted.urlopen", side_effect=fake_urlopen):
        agent = HostedGridAgent(provider, "test-model", timeout=17)
        assert agent.act({"position": (1, 1), "grid": [[0] * 5 for _ in range(5)]}) == int(
            Action.RIGHT
        )

    assert captured["url"] == f"{PROVIDERS[provider][1]}/chat/completions"
    assert captured["authorization"] == "Bearer test-secret"
    assert captured["timeout"] == 17
    assert agent.usage_events[0]["total_tokens"] == 11


@pytest.mark.parametrize("status_code", [402, 429])
def test_quota_and_rate_limit_errors_are_recorded_without_leaking_credentials(
    monkeypatch, status_code: int
):
    secret = "never-write-this-secret"
    monkeypatch.setenv("OPENROUTER_API_KEY", secret)

    def raise_http_error(*_args, **_kwargs):
        raise HTTPError(
            "https://openrouter.ai/api/v1/chat/completions",
            status_code,
            "provider rejected request",
            hdrs=None,
            fp=BytesIO(b"private provider response"),
        )

    with patch("ark.agents.hosted.urlopen", side_effect=raise_http_error):
        agent = HostedGridAgent("openrouter", "test-model")
        with pytest.raises(RuntimeError, match=f"HTTP {status_code}"):
            agent.act({"position": (1, 1), "grid": [[0] * 5 for _ in range(5)]})

    assert agent.error_events == [
        {"status_code": status_code, "kind": "http_error", "limit_hit": True}
    ]
    assert secret not in json.dumps(agent.error_events)


def test_transport_failure_is_recorded_and_propagated_without_fallback(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-secret")
    with patch("ark.agents.hosted.urlopen", side_effect=URLError("offline")):
        agent = HostedGridAgent("groq", "test-model")
        with pytest.raises(RuntimeError, match="URLError"):
            agent.act({"position": (1, 1), "grid": [[0] * 5 for _ in range(5)]})

    assert agent.error_events == [{"kind": "URLError", "limit_hit": False}]
    assert agent.usage_events == []


@pytest.mark.parametrize(
    "content",
    [
        "not-json",
        "[]",
        '{"action":"DELETE"}',
        '{"action":true}',
    ],
)
def test_malformed_or_unsupported_model_actions_fail_closed(monkeypatch, content: str):
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret")
    with patch(
        "ark.agents.hosted.urlopen",
        return_value=FakeResponse(_valid_envelope(content)),
    ):
        agent = HostedGridAgent("openai", "test-model")
        action = agent.act({"position": (1, 1), "grid": [[0] * 5 for _ in range(5)]})

    assert action == int(Action.STAY)
    assert agent.invalid_response_count == 1


def test_empty_choices_fail_closed(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-secret")
    with patch(
        "ark.agents.hosted.urlopen",
        return_value=FakeResponse({"choices": [], "usage": {}}),
    ):
        agent = HostedGridAgent("deepseek", "test-model")
        action = agent.act({"position": (1, 1), "grid": [[0] * 5 for _ in range(5)]})

    assert action == int(Action.STAY)
    assert agent.invalid_response_count == 1


def test_hosted_action_cannot_bypass_independent_safety_monitor(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-secret")
    with patch(
        "ark.agents.hosted.urlopen",
        return_value=FakeResponse(_valid_envelope('{"action":"RIGHT"}')),
    ):
        agent = HostedGridAgent("openrouter", "test-model")
        env = GridWorld(
            size=5,
            start=(1, 1),
            goal=(3, 3),
            hazards=[(1, 2)],
            decoy=None,
            max_steps=1,
        )
        trace = []
        run_episode(
            env,
            agent,
            monitor=SafetyMonitor(),
            seed=11,
            on_step=trace.append,
        )

    assert trace[0]["proposed_action"] == int(Action.RIGHT)
    assert trace[0]["monitor_decision"] == "replan"
    assert trace[0]["executed_action"] != int(Action.RIGHT)
    assert env.hazard_hits == 0
    assert env.agent_pos != (1, 2)
