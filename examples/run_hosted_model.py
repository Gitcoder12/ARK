"""Run a small, explicitly selected hosted-model ARK GridWorld evaluation."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ark.agents.hosted import HostedGridAgent, PROVIDERS
from ark.envs.grid_world import GridWorld
from ark.evaluation.monitor import SafetyMonitor
from ark.experiments.runner import run_episode


def key_snapshot(provider: str, api_key: str) -> dict:
    """Return only safe quota metadata; never persist the key or raw response."""
    if provider != "openrouter":
        return {"status": "not_exposed_by_provider_api", "limit_remaining": None}
    request = Request(
        "https://openrouter.ai/api/v1/key",
        headers={"Authorization": f"Bearer {api_key}"},
        method="GET",
    )
    try:
        with urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
        data = payload.get("data", {})
        return {
            "status": "available",
            "limit": data.get("limit"),
            "limit_remaining": data.get("limit_remaining"),
            "limit_reset": data.get("limit_reset"),
            "usage": data.get("usage"),
            "usage_daily": data.get("usage_daily"),
            "usage_monthly": data.get("usage_monthly"),
            "expires_at": data.get("expires_at"),
        }
    except HTTPError as exc:
        return {"status": "http_error", "http_status": exc.code}
    except (URLError, TimeoutError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {"status": "unavailable", "error_type": type(exc).__name__}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=sorted(PROVIDERS), default="openrouter")
    parser.add_argument("--model", required=True)
    parser.add_argument("--episodes", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--output", type=Path, default=Path("ark-model-usage.json"))
    args = parser.parse_args()
    if not 1 <= args.episodes <= 20:
        parser.error("--episodes must be between 1 and 20")

    env_name, _ = PROVIDERS[args.provider]
    import os

    api_key = os.getenv(env_name, "").strip()
    if not api_key:
        parser.error(f"Missing environment variable {env_name}")

    agent = HostedGridAgent(args.provider, args.model, timeout=args.timeout, seed=args.seed)
    before = key_snapshot(args.provider, api_key)
    episodes = []
    run_error = None
    for index in range(args.episodes):
        try:
            env = GridWorld(seed=args.seed + index, randomize=True)
            metrics = run_episode(
                env,
                agent,
                monitor=SafetyMonitor(),
                seed=args.seed + index,
            )
            episodes.append(asdict(metrics))
        except Exception as exc:
            run_error = {"type": type(exc).__name__, "message": str(exc)}
            break

    after = key_snapshot(args.provider, api_key)
    report = {
        "schema_version": 1,
        "provider": args.provider,
        "model": args.model,
        "episodes_requested": args.episodes,
        "episodes_completed": len(episodes),
        "episodes": episodes,
        "usage_events": agent.usage_events,
        "error_events": agent.error_events,
        "invalid_model_actions": agent.invalid_response_count,
        "quota": {"before": before, "after": after},
        "run_error": run_error,
        "interpretation": (
            "OpenRouter key metadata reports the key's aggregate budget, not per-model "
            "remaining quota. Per-model tokens/cost are recorded only when returned by "
            "the provider. Direct-provider quota APIs are not inferred."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(json.dumps({
        "provider": args.provider,
        "model": args.model,
        "episodes_completed": len(episodes),
        "usage_events": len(agent.usage_events),
        "quota_status": after.get("status"),
        "limit_remaining": after.get("limit_remaining"),
        "report": str(args.output),
        "run_error": run_error,
    }, indent=2))
    return 1 if run_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
