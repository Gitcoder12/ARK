# ARK local model integrity quickstart

This integration uses Ollama on loopback only. It makes no hosted-provider
requests and has no paid fallback.

```powershell
ollama list
ollama run qwen2.5vl:3b
```

In another terminal, from the ARK repository after `pip install -e ".[dev]"`, run the ready-made audit. It compares the same local model at two sampling temperatures (a configuration comparison, not an independent-model comparison):\n\n```powershell\npython examples/run_local_integrity_audit.py\n```\n\nTo compare two installed local models, pass both names:\n\n```powershell\npython examples/run_local_integrity_audit.py --baseline qwen2.5vl:3b --candidate another-local-model\n```\n\nThe Python API is also available:

```python
from ark.integrity import OllamaAdapter, audit_models, build_ml_code_tasks

local_model = OllamaAdapter("qwen2.5vl:3b")
comparison_model = OllamaAdapter("another-local-model")

report = audit_models(
    baseline_id="qwen2.5vl:3b",
    baseline=local_model,
    candidate_id="another-local-model",
    candidate=comparison_model,
    tasks=build_ml_code_tasks(),
)
print(report.to_json())
```

The included ML-code evaluators are static AST/structure heuristics. They check
syntax and expected operations; they do not execute generated code, prove
gradient correctness, or measure loss convergence. Treat scores as screening
signals. A later phase should add an isolated execution harness and known-good
numerical reference tests before making stronger quality claims.

The adapter rejects non-loopback hosts, requires an explicit local model name,
and never selects another model automatically.
