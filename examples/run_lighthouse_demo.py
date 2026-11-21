"""Run a tiny synthetic Lighthouse demonstration."""
from ark.lighthouse import create_lighthouse


def main() -> None:
    light, trusted = create_lighthouse()
    light.observe_claim(
        event_id="claim-1", agent_id="demo-agent", episode_id="demo-episode",
        timestamp=1.0, claim="Task completed", metadata={"success": True},
    )
    trusted.record_outcome(
        event_id="outcome-1", agent_id="demo-agent", episode_id="demo-episode",
        timestamp=2.0, source="environment", outcome="failure",
        evidence_ref="simulator:episode-1",
    )
    report = light.report("demo-agent", "demo-episode")
    print(f"Lighthouse level: {report.level.value}")
    print(f"Heuristic score (not a probability): {report.heuristic_score:.2f}")
    for indicator in report.indicators:
        print(f"- {indicator.code}: {indicator.explanation}")
    print(report.recommendation)


if __name__ == "__main__":
    main()
