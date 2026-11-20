"""Command-line demonstration for the Strategic Failure Simulator."""
from __future__ import annotations

import argparse
import json

from .core import AgentGroup, PremortemEngine, result_to_dict
from .scenarios import historical_scenarios


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ARK strategic failure simulations.")
    parser.add_argument("--scenario", choices=("all", "beas", "gedrosia", "succession", "engineering"),
                        default="all")
    parser.add_argument("--fail-role", action="append", default=[],
                        help="Inject a failure for a role (repeatable).")
    parser.add_argument("--invalid-role", action="append", default=[],
                        help="Inject invalid output for a role (repeatable).")
    parser.add_argument("--fail-backup-role", action="append", default=[],
                        help="Make the matching backup unavailable (repeatable).")
    parser.add_argument("--json", action="store_true", help="Print machine-readable results.")
    args = parser.parse_args()

    scenarios = historical_scenarios()
    selected = scenarios if args.scenario == "all" else {args.scenario: scenarios[args.scenario]}
    output = []
    for key, plan in selected.items():
        premortem = PremortemEngine().analyse(plan)
        group = AgentGroup().run(
            plan,
            fail_roles=args.fail_role,
            invalid_roles=args.invalid_role,
            fail_backup_roles=args.fail_backup_role,
        )
        output.append({
            "scenario": key,
            "plan": plan.name,
            "premortem": result_to_dict(premortem),
            "agent_group": result_to_dict(group),
        })

    if args.json:
        print(json.dumps(output, indent=2, default=str))
        return
    for item in output:
        print(f"\n=== {item['plan']} ===")
        print(f"Pre-mortem: {item['premortem']['recommended_decision']}")
        for finding in item["premortem"]["findings"]:
            print(f"- [{finding['severity']}] {finding['title']}: {finding['mitigation']}")
        group = item["agent_group"]
        print(f"Agent group: {group['decision']}")
        print(f"Active agents: {', '.join(group['active_agents']) or 'none'}")
        print(f"Replacements: {', '.join(group['replacements']) or 'none'}")
        if group["external_review_report"]:
            print("\n" + group["external_review_report"])


if __name__ == "__main__":
    main()
