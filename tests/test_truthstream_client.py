import io
import json
from unittest.mock import patch

import pytest

from ark.governance.truthstream_client import TruthstreamClient


def test_client_rejects_plain_http_remote_endpoint():
    with pytest.raises(ValueError):
        TruthstreamClient("http://example.org")


def test_client_allows_loopback_development_endpoint():
    assert TruthstreamClient("http://127.0.0.1:8000").endpoint.endswith("/verify")


def test_client_posts_and_parses_truthstream_response():
    body = json.dumps([{
        "claim": {"text": "test"},
        "status": "likely_true",
        "confidence_score": 0.9,
        "provenance": {"status": "demo_or_incomplete"},
        "supporting_evidence": [],
        "contradicting_evidence": [],
        "neutral_evidence": [],
    }]).encode()

    class Response(io.BytesIO):
        pass

    class FakeOpener:
        def open(self, request, timeout):
            assert request.full_url == "https://truth.example/verify"
            assert request.get_method() == "POST"
            assert timeout == 5.0
            return Response(body)

    with patch("ark.governance.truthstream_client.build_opener", return_value=FakeOpener()):
        results = TruthstreamClient("https://truth.example").verify("A test claim")
    assert len(results) == 1
    assert not results[0].usable_as_context
