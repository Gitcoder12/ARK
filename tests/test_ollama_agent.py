import json
from io import BytesIO

from ark.agents.ollama import OllamaGridAgent
from ark.envs.grid_world import Action


def test_ollama_agent_posts_to_local_api_and_parses_action(monkeypatch):
    def fake_urlopen(request, timeout):
        payload = json.loads(request.data.decode("utf-8"))
        assert payload["model"] == "llama3"
        assert payload["stream"] is False
        assert timeout == 10
        response = {"response": json.dumps({"action": "UP"})}
        return BytesIO(json.dumps(response).encode("utf-8"))

    monkeypatch.setattr("ark.agents.ollama.urlopen", fake_urlopen)
    agent = OllamaGridAgent(model="llama3", timeout=10)
    action = agent.act(
        {
            "position": (1, 1),
            "intended_goal": (1, 2),
            "grid": [[0, 0], [0, 3]],
        }
    )

    assert action == int(Action.UP)
    assert agent.invalid_response_count == 0


def test_ollama_agent_fails_closed_on_invalid_action(monkeypatch):
    def fake_urlopen(request, timeout):
        response = {"response": json.dumps({"action": "FLY"})}
        return BytesIO(json.dumps(response).encode("utf-8"))

    monkeypatch.setattr("ark.agents.ollama.urlopen", fake_urlopen)
    agent = OllamaGridAgent(model="llama3")
    action = agent.act({"position": (0, 0), "intended_goal": (1, 1)})

    assert action == int(Action.STAY)
    assert agent.invalid_response_count == 1
    assert agent.last_error is not None
