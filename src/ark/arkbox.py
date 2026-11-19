"""ARKBox: versioned scenario storage and reproducible experiment records.

The first adapter manages ARK's existing GridWorld environments. It does not
claim to simulate physical robots; additional simulator adapters can be added
behind the same scenario/experiment storage contract later.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ark.envs.grid_world import GridWorld


class ARKBoxError(RuntimeError):
    """Raised when an ARKBox operation cannot be completed safely."""


_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def _safe_id(value: str, label: str) -> str:
    if not isinstance(value, str) or not _SAFE_ID.fullmatch(value) or value in {".", ".."}:
        raise ValueError(\n            f"{label} must be 1-64 safe letters, numbers, dots, underscores or hyphens"\n        )
    return value


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


@dataclass(frozen=True)
class GridScenario:
    """A portable, validated GridWorld scenario definition."""

    scenario_id: str
    name: str
    size: int = 7
    start: tuple[int, int] = (1, 1)
    goal: tuple[int, int] = (5, 5)
    hazards: tuple[tuple[int, int], ...] = ((2, 3), (3, 2), (4, 4))
    decoy: tuple[int, int] | None = (3, 5)
    max_steps: int = 50

    def __post_init__(self) -> None:
        _safe_id(self.scenario_id, "scenario_id")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("scenario name must be a non-empty string")
        if isinstance(self.size, bool) or not isinstance(self.size, int) or self.size < 5:
            raise ValueError("size must be an integer of at least 5")
        if (
            isinstance(self.max_steps, bool)
            or not isinstance(self.max_steps, int)
            or self.max_steps < 1
        ):
            raise ValueError("max_steps must be a positive integer")

        def check_cell(cell: tuple[int, int], label: str) -> None:
            if (
                not isinstance(cell, (tuple, list))
                or len(cell) != 2
                or any(isinstance(v, bool) or not isinstance(v, int) for v in cell)
                or not all(1 <= v < self.size - 1 for v in cell)
            ):
                raise ValueError(f"{label} must be an interior (row, column) coordinate")

        check_cell(self.start, "start")
        check_cell(self.goal, "goal")
        if self.start == self.goal:
            raise ValueError("start and goal must be different")
        for hazard in self.hazards:
            check_cell(hazard, "hazard")
        if len(set(self.hazards)) != len(self.hazards):
            raise ValueError("hazard coordinates must be unique")
        reserved = {self.start, self.goal}
        if self.decoy is not None:
            check_cell(self.decoy, "decoy")
            reserved.add(self.decoy)
        if any(hazard in reserved for hazard in self.hazards):
            raise ValueError("hazards cannot overlap start, goal or decoy")
        if self.decoy == self.start or self.decoy == self.goal:
            raise ValueError("decoy must be separate from start and goal")

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "name": self.name,
            "environment": "gridworld",
            "size": self.size,
            "start": list(self.start),
            "goal": list(self.goal),
            "hazards": [list(cell) for cell in self.hazards],
            "decoy": list(self.decoy) if self.decoy is not None else None,
            "max_steps": self.max_steps,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GridScenario:
        if not isinstance(data, dict) or data.get("environment") != "gridworld":
            raise ValueError("unsupported or invalid ARKBox scenario")
        return cls(
            scenario_id=data["scenario_id"],
            name=data["name"],
            size=data["size"],
            start=tuple(data["start"]),
            goal=tuple(data["goal"]),
            hazards=tuple(tuple(cell) for cell in data["hazards"]),
            decoy=tuple(data["decoy"]) if data.get("decoy") is not None else None,
            max_steps=data["max_steps"],
        )


class ARKBox:
    """Store reusable scenarios and immutable experiment evidence."""

    def __init__(self, root: str | Path):
        self.root = Path(root).expanduser().resolve()
        self.scenarios_dir = self.root / "scenarios"
        self.experiments_dir = self.root / "experiments"
        self.scenarios_dir.mkdir(parents=True, exist_ok=True)
        self.experiments_dir.mkdir(parents=True, exist_ok=True)

    def add_scenario(self, scenario: GridScenario) -> dict[str, str]:
        if not isinstance(scenario, GridScenario):
            raise TypeError("scenario must be a GridScenario")
        payload = scenario.to_dict()
        digest = hashlib.sha256(_canonical_json(payload)).hexdigest()
        destination = self.scenarios_dir / f"{scenario.scenario_id}.json"
        if destination.exists():
            raise FileExistsError(f"scenario already exists: {scenario.scenario_id}")
        envelope = {"schema_version": 1, "sha256": digest, "scenario": payload}
        temporary = destination.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(envelope, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        temporary.replace(destination)
        return {"scenario_id": scenario.scenario_id, "sha256": digest, "path": str(destination)}

    def load_scenario(self, scenario_id: str) -> GridScenario:
        scenario_id = _safe_id(scenario_id, "scenario_id")
        path = (self.scenarios_dir / f"{scenario_id}.json").resolve()
        if path.parent != self.scenarios_dir.resolve() or not path.is_file():
            raise KeyError(f"unknown ARKBox scenario: {scenario_id}")
        try:
            envelope = json.loads(path.read_text(encoding="utf-8"))
            if envelope.get("schema_version") != 1:
                raise ARKBoxError("unsupported scenario schema version")
            payload = envelope["scenario"]
            actual = hashlib.sha256(_canonical_json(payload)).hexdigest()
            if actual != envelope.get("sha256"):
                raise ARKBoxError(f"scenario integrity check failed: {scenario_id}")
            scenario = GridScenario.from_dict(payload)
            if scenario.scenario_id != scenario_id:
                raise ARKBoxError("scenario identifier does not match its file name")
            return scenario
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            if isinstance(exc, ARKBoxError):
                raise
            raise ARKBoxError(f"scenario is unreadable or invalid: {exc}") from exc

    def list_scenarios(self) -> list[dict[str, str]]:
        records = []
        for path in sorted(self.scenarios_dir.glob("*.json")):
            scenario = self.load_scenario(path.stem)
            records.append({"scenario_id": scenario.scenario_id, "name": scenario.name})
        return records

    def build_gridworld(self, scenario_id: str, *, seed: int | None = None) -> GridWorld:
        scenario = self.load_scenario(scenario_id)
        return GridWorld(
            size=scenario.size,
            start=scenario.start,
            goal=scenario.goal,
            hazards=list(scenario.hazards),
            decoy=scenario.decoy,
            max_steps=scenario.max_steps,
            seed=seed,
            randomize=False,
        )

    def record_experiment(
        self,
        *,
        scenario_id: str,
        agent: str,
        seed: int,
        config: dict[str, Any],
        metrics: dict[str, Any],
        code_revision: str | None = None,
        environment: dict[str, Any] | None = None,
    ) -> dict[str, str]:
        scenario = self.load_scenario(scenario_id)
        if not isinstance(agent, str) or not agent.strip():
            raise ValueError("agent must be a non-empty string")
        if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
            raise ValueError("seed must be a non-negative integer")
        payload = {
            "schema_version": 1,
            "experiment_id": uuid.uuid4().hex,
            "created_at": datetime.now(UTC).isoformat(),
            "scenario_id": scenario.scenario_id,
            "scenario_sha256": hashlib.sha256(_canonical_json(scenario.to_dict())).hexdigest(),
            "agent": agent,
            "seed": seed,
            "config": config,
            "metrics": metrics,
            "code_revision": code_revision,
            "environment": environment or {},
        }
        try:
            encoded = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
        except (TypeError, ValueError) as exc:
            raise ValueError(\n                f"experiment data must be finite JSON-compatible values: {exc}"\n            ) from exc
        destination = self.experiments_dir / f"{payload['experiment_id']}.json"
        destination.write_text(encoded, encoding="utf-8")
        digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
        return {\n            "experiment_id": payload["experiment_id"],\n            "sha256": digest,\n            "path": str(destination),\n        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ARKBox scenario and experiment library")
    parser.add_argument(
        "--root",
        default=str(Path.home() / ".ark" / "arkbox"),
        help="ARKBox storage directory",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="list stored scenarios")
    add = commands.add_parser("add-default", help="store the standard 7x7 baseline scenario")
    add.add_argument("--scenario-id", default="gridworld-baseline-v1")
    args = parser.parse_args(argv)
    box = ARKBox(args.root)
    if args.command == "list":
        result: Any = box.list_scenarios()
    else:
        result = box.add_scenario(
            GridScenario(scenario_id=args.scenario_id, name="Standard 7x7 GridWorld baseline")
        )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
