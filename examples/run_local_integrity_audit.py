"""Run a zero-hosted-cost ARK ML-code audit against local Ollama.

Usage:
    python examples/run_local_integrity_audit.py
    python examples/run_local_integrity_audit.py --baseline qwen2.5vl:3b --candidate qwen2.5vl:3b
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ark.integrity import OllamaAdapter, audit_models, build_ml_code_tasks


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit local Ollama model behavior")
    parser.add_argument("--baseline", default="qwen2.5vl:3b")
    parser.add_argument("--candidate", default="qwen2.5vl:3b")
    parser.add_argument("--host", default="http://127.0.0.1:11434")
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--output", default="ark_model_integrity_report.json")
    args = parser.parse_args()

    baseline = OllamaAdapter(
        args.baseline, host=args.host, timeout=args.timeout, temperature=0.0
    )
    candidate = OllamaAdapter(
        args.candidate, host=args.host, timeout=args.timeout, temperature=0.2
    )
    report = audit_models(
        baseline_id=f"{args.baseline}@temperature-0.0",
        baseline=baseline,
        candidate_id=f"{args.candidate}@temperature-0.2",
        candidate=candidate,
        tasks=build_ml_code_tasks(),
    )
    output = Path(args.output)
    output.write_text(report.to_json() + "\\n", encoding="utf-8")
    print(json.dumps({
        "status": report.status,
        "baseline_mean": report.baseline_mean,
        "candidate_mean": report.candidate_mean,
        "mean_drop": report.mean_drop,
        "report": str(output.resolve()),
        "interpretation": report.interpretation,
    }, indent=2))


if __name__ == "__main__":
    main()
