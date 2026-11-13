"""Run ARK's adversarial monitor regression suite and print its bypass rate."""

from __future__ import annotations

from ark.evaluation.adversarial import run_monitor_adversarial_suite


def main() -> None:
    report = run_monitor_adversarial_suite()
    print(f"Attempts: {report['attempts']}")
    print(f"Bypasses: {report['bypasses']}")
    print(f"Bypass Success Rate: {report['bypass_success_rate']:.2%}")
    for case in report["cases"]:
        print(f"- {case['case']}: {case['decision']} ({case['reason']})")
    print(report["interpretation"])


if __name__ == "__main__":
    main()
