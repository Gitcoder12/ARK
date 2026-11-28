# Test Evidence Ledger

This directory defines the evidence contract for ARK/RepoForge test runs. It must contain only reports produced by an actual test execution; never commit fabricated, hand-edited, or illustrative results as real evidence.

## Required evidence for every run

- Repository and exact commit SHA
- Branch, UTC timestamp, runner/OS, Python and dependency versions
- Exact command and test scope
- Exit code and pass/fail/error/skip counts
- JUnit XML report and complete console log
- Related issue/PR or change identifier
- Whether the run used mocks, local services, or live external APIs

## CI evidence

GitHub Actions creates a downloadable `test-evidence` artifact for each test job. The artifact contains JUnit XML output. The workflow run itself retains the console log, environment and commit identity. Each matrix/runtime job has a distinct artifact name.

Artifacts are evidence of that specific commit and environment only. They do not prove real-world safety, production readiness, or behavior outside the tested scope.

## Local run

From the repository root:

```bash
python -m pip install -e ".[dev]"
mkdir -p test-results
pytest -v --strict-markers --junitxml=test-results/junit-local.xml
```

For RepoForge, use the repository's configured pytest command and add the same `--junitxml` option.

## Evidence integrity rules

1. Never overwrite a previous run's report; use a unique run identifier or timestamp.
2. Keep failed runs. A failure is useful evidence, not something to erase.
3. Separate unit, integration, adversarial, performance, and live-provider tests.
4. Label mocked/simulated tests clearly; never describe them as live tests.
5. Record skipped tests and missing credentials/services.
6. Do not store API keys, tokens, private data, or secrets in logs or artifacts.
7. A test passing is not proof that the tested system is safe in general.
