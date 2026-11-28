"""Privacy-first token and cost ledger for AI model calls.

The caller must pass provider-reported token counts when available. Estimated
counts must be explicitly labelled; missing usage is never silently guessed.
No prompts, completions, credentials, or headers are stored.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from threading import RLock
from typing import Any


@dataclass(frozen=True)
class UsageEvent:
    provider: str
    model: str
    input_tokens: int | None
    output_tokens: int | None
    source: str = "provider"
    request_id: str | None = None
    repo: str = "unknown"
    module: str = "unknown"
    task: str = "unknown"
    latency_ms: int | None = None
    success: bool = True
    is_local: bool = False
    input_usd_per_million: float | None = None
    output_usd_per_million: float | None = None
    occurred_at: str | None = None

    def __post_init__(self) -> None:
        if not self.provider.strip() or not self.model.strip():
            raise ValueError("provider and model are required")
        for name in ("input_tokens", "output_tokens", "latency_ms"):
            value = getattr(self, name)
            if value is not None and value < 0:
                raise ValueError(f"{name} cannot be negative")
        if self.source not in {"provider", "estimated", "unknown"}:
            raise ValueError("source must be provider, estimated, or unknown")
        for name in ("input_usd_per_million", "output_usd_per_million"):
            value = getattr(self, name)
            if value is not None and value < 0:
                raise ValueError(f"{name} cannot be negative")

    @property
    def total_tokens(self) -> int | None:
        if self.input_tokens is None or self.output_tokens is None:
            return None
        return self.input_tokens + self.output_tokens

    @property
    def estimated_cost_usd(self) -> float | None:
        if self.is_local:
            return 0.0
        if (
            self.input_tokens is None
            or self.output_tokens is None
            or self.input_usd_per_million is None
            or self.output_usd_per_million is None
        ):
            return None
        return (
            self.input_tokens * self.input_usd_per_million
            + self.output_tokens * self.output_usd_per_million
        ) / 1_000_000


class UsageLedger:
    """Append-only SQLite ledger; callers choose the database location."""

    def __init__(self, database: str | Path) -> None:
        self.database = str(database)
        self._lock = RLock()
        Path(self.database).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS usage_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    occurred_at TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    repo TEXT NOT NULL,
                    module TEXT NOT NULL,
                    task TEXT NOT NULL,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    total_tokens INTEGER,
                    source TEXT NOT NULL,
                    estimated_cost_usd REAL,
                    latency_ms INTEGER,
                    success INTEGER NOT NULL,
                    is_local INTEGER NOT NULL,
                    request_id TEXT
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_usage_time ON usage_events(occurred_at)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_usage_model ON usage_events(provider, model)"
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def record(self, event: UsageEvent) -> int:
        """Persist metadata and usage only; never accepts prompt or key fields."""
        occurred_at = event.occurred_at or datetime.now(UTC).isoformat()
        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO usage_events (
                    occurred_at, provider, model, repo, module, task,
                    input_tokens, output_tokens, total_tokens, source,
                    estimated_cost_usd, latency_ms, success, is_local, request_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    occurred_at, event.provider, event.model, event.repo,
                    event.module, event.task, event.input_tokens,
                    event.output_tokens, event.total_tokens, event.source,
                    event.estimated_cost_usd, event.latency_ms,
                    int(event.success), int(event.is_local), event.request_id,
                ),
            )
            return int(cursor.lastrowid)

    def summary(self, *, since: str | None = None) -> dict[str, Any]:
        """Return totals; costs remain null when pricing/usage is unknown."""
        query = "SELECT * FROM usage_events"
        params: tuple[Any, ...] = ()
        if since is not None:
            query += " WHERE occurred_at >= ?"
            params = (since,)
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()

        known_input = [row["input_tokens"] for row in rows if row["input_tokens"] is not None]
        known_output = [row["output_tokens"] for row in rows if row["output_tokens"] is not None]
        known_costs = [row["estimated_cost_usd"] for row in rows if row["estimated_cost_usd"] is not None]
        return {
            "requests": len(rows),
            "successful_requests": sum(row["success"] for row in rows),
            "failed_requests": sum(not row["success"] for row in rows),
            "input_tokens": sum(known_input),
            "output_tokens": sum(known_output),
            "total_tokens": sum(known_input) + sum(known_output)
            if len(known_input) == len(rows) and len(known_output) == len(rows)
            else None,
            "estimated_cost_usd": round(sum(known_costs), 10)
            if len(known_costs) == len(rows)
            else None,
            "unpriced_requests": sum(row["estimated_cost_usd"] is None for row in rows),
            "local_requests": sum(row["is_local"] for row in rows),
            "by_provider_model": self._group(rows, ("provider", "model")),
            "by_repo_module": self._group(rows, ("repo", "module")),
        }

    @staticmethod
    def _group(rows: list[sqlite3.Row], fields: tuple[str, str]) -> list[dict[str, Any]]:
        groups: dict[tuple[str, str], dict[str, Any]] = {}
        for row in rows:
            key = (row[fields[0]], row[fields[1]])
            item = groups.setdefault(
                key, {"requests": 0, "input_tokens": 0, "output_tokens": 0,
                      "estimated_cost_usd": 0.0, "unpriced_requests": 0}
            )
            item["requests"] += 1
            item["input_tokens"] += row["input_tokens"] or 0
            item["output_tokens"] += row["output_tokens"] or 0
            if row["estimated_cost_usd"] is None:
                item["unpriced_requests"] += 1
            else:
                item["estimated_cost_usd"] += row["estimated_cost_usd"]
        return [
            {fields[0]: key[0], fields[1]: key[1], **value,
             "estimated_cost_usd": round(value["estimated_cost_usd"], 10)}
            for key, value in sorted(groups.items())
        ]

    def budget_status(self, daily_limit_usd: float, *, day: date | None = None) -> dict[str, Any]:
        """Compare recorded estimated cost with a user-configured UTC daily cap."""
        if daily_limit_usd < 0:
            raise ValueError("daily_limit_usd cannot be negative")
        selected_day = day or datetime.now(UTC).date()
        start = datetime.combine(selected_day, datetime.min.time(), tzinfo=UTC).isoformat()
        end = datetime.combine(selected_day, datetime.max.time(), tzinfo=UTC).isoformat()
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT estimated_cost_usd FROM usage_events WHERE occurred_at BETWEEN ? AND ?",
                (start, end),
            ).fetchall()
        unknown = sum(row["estimated_cost_usd"] is None for row in rows)
        spend = sum(row["estimated_cost_usd"] or 0.0 for row in rows)
        return {
            "date_utc": selected_day.isoformat(),
            "daily_limit_usd": daily_limit_usd,
            "recorded_estimated_cost_usd": round(spend, 10),
            "remaining_usd": round(max(0.0, daily_limit_usd - spend), 10),
            "limit_reached": spend >= daily_limit_usd,
            "unpriced_requests": unknown,
            "warning": "Some requests have unknown cost; actual spend may be higher."
            if unknown else None,
        }


def event_from_provider_usage(
    *,
    provider: str,
    model: str,
    usage: Any,
    **metadata: Any,
) -> UsageEvent:
    """Build an event from explicit token counts; accepts dicts or SDK usage objects.

    Provider-specific adapters should map their documented usage fields into
    input_tokens/output_tokens before calling this function.
    """
    if isinstance(usage, dict):
        input_tokens = usage.get("input_tokens", usage.get("prompt_tokens"))
        output_tokens = usage.get("output_tokens", usage.get("completion_tokens"))
    else:
        input_tokens = getattr(usage, "input_tokens", getattr(usage, "prompt_tokens", None))
        output_tokens = getattr(usage, "output_tokens", getattr(usage, "completion_tokens", None))
    if input_tokens is None or output_tokens is None:
        metadata.setdefault("source", "unknown")
    return UsageEvent(
        provider=provider,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        **metadata,
    )


def format_summary(summary: dict[str, Any]) -> str:
    """Stable JSON output for CLI use and CI artifacts."""
    return json.dumps(summary, indent=2, sort_keys=True)
