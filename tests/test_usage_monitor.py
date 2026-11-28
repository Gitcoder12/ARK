from datetime import date

import pytest

from ark.usage_monitor import UsageEvent, UsageLedger, event_from_provider_usage


def test_records_actual_usage_and_calculates_cost(tmp_path):
    ledger = UsageLedger(tmp_path / "usage.sqlite3")
    event = UsageEvent(
        provider="openai", model="example-model", input_tokens=1000,
        output_tokens=500, input_usd_per_million=2.0,
        output_usd_per_million=4.0, repo="ARK", module="tests",
    )
    assert ledger.record(event) == 1
    summary = ledger.summary()
    assert summary["total_tokens"] == 1500
    assert summary["estimated_cost_usd"] == pytest.approx(0.004)
    assert summary["by_repo_module"][0]["repo"] == "ARK"


def test_unknown_usage_is_not_guessed_or_priced(tmp_path):
    ledger = UsageLedger(tmp_path / "usage.sqlite3")
    event = event_from_provider_usage(
        provider="provider", model="model", usage={}, repo="ARK"
    )
    ledger.record(event)
    summary = ledger.summary()
    assert summary["total_tokens"] is None
    assert summary["estimated_cost_usd"] is None
    assert summary["unpriced_requests"] == 1


def test_local_models_have_zero_api_cost(tmp_path):
    ledger = UsageLedger(tmp_path / "usage.sqlite3")
    ledger.record(UsageEvent(
        provider="ollama", model="qwen-local", input_tokens=20,
        output_tokens=10, is_local=True,
    ))
    assert ledger.summary()["estimated_cost_usd"] == 0.0


def test_daily_budget_reports_unknown_cost(tmp_path):
    ledger = UsageLedger(tmp_path / "usage.sqlite3")
    ledger.record(UsageEvent(
        provider="unknown", model="model", input_tokens=None,
        output_tokens=None, source="unknown",
    ))
    status = ledger.budget_status(1.0, day=date.today())
    assert status["unpriced_requests"] == 1
    assert status["warning"]


@pytest.mark.parametrize("tokens", [-1, None])
def test_negative_token_counts_rejected_but_unknown_allowed(tokens):
    if tokens is None:
        UsageEvent(provider="p", model="m", input_tokens=tokens, output_tokens=0)
    else:
        with pytest.raises(ValueError):
            UsageEvent(provider="p", model="m", input_tokens=tokens, output_tokens=0)
\n\ndef test_ollama_usage_fields_are_supported(tmp_path):\n    ledger = UsageLedger(tmp_path / "usage.sqlite3")\n    event = event_from_provider_usage(\n        provider="ollama", model="qwen2.5:3b",\n        usage={"prompt_eval_count": 42, "eval_count": 18},\n        is_local=True,\n    )\n    ledger.record(event)\n    summary = ledger.summary()\n    assert summary["input_tokens"] == 42\n    assert summary["output_tokens"] == 18\n    assert summary["total_tokens"] == 60\n    assert summary["estimated_cost_usd"] == 0.0\n