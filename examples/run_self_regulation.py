"""Run a tiny, deterministic demonstration of ARK's self-regulation gate.

From the repository root:
    python examples/run_self_regulation.py
"""

from ark.alignment.self_regulation import ActionProposal, SelfRegulationGate


def main() -> None:
    gate = SelfRegulationGate()
    proposals = [
        ActionProposal(
            action="inspect_sensor",
            risk_level=1,
            evidence_confidence=0.99,
            authorized=True,
            goal_consistent=True,
        ),
        ActionProposal(
            action="override_safety_interlock",
            risk_level=9,
            evidence_confidence=0.98,
            authorized=False,
            goal_consistent=False,
        ),
        ActionProposal(
            action="send_external_command",
            risk_level=3,
            evidence_confidence=0.35,
            authorized=None,
            goal_consistent=True,
        ),
    ]

    for proposal in proposals:
        result = gate.evaluate(proposal)
        print(f"{result.decision.value.upper():6} {proposal.action}")
        for reason in result.reasons:
            print(f"       - {reason}")


if __name__ == "__main__":
    main()
