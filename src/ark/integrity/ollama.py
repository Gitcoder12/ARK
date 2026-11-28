"""Local-only Ollama adapter for ARK model audits.

The adapter deliberately accepts only loopback URLs. It never contacts hosted
providers and has no automatic fallback.
"""

from __future__ import annotations

import json
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class OllamaAdapter:
    """Callable adapter for a model served by a local Ollama instance."""

    def __init__(
        self,
        model: str,
        *,
        host: str = "http://127.0.0.1:11434",
        timeout: float = 120.0,
        temperature: float = 0.0,
    ) -> None:
        parsed = urlparse(host)
        if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("OllamaAdapter only permits http://localhost or loopback hosts")
        if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
            raise ValueError("Ollama host must be a base URL without path, query or fragment")
        if not model.strip():
            raise ValueError("model must be non-empty")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        if not 0 <= temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")
        self.model = model
        self.host = host.rstrip("/")
        self.timeout = timeout
        self.temperature = temperature

    def __call__(self, prompt: str) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": self.temperature},
            }
        ).encode("utf-8")
        request = Request(
            f"{self.host}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Local Ollama request failed: {exc}") from exc
        text = result.get("response")
        if not isinstance(text, str):
            raise RuntimeError("Ollama response did not contain a text 'response' field")
        return text
