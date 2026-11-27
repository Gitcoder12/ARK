# ARK User Guide

This is the operational guide. The root README is intentionally a short entry point.

## 1. Install

Python 3.11 or newer is required.

### Windows PowerShell

```powershell
git clone https://github.com/Gitcoder12/ARK.git
cd ARK
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

If PowerShell blocks activation, allow it for the current terminal only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
git clone https://github.com/Gitcoder12/ARK.git
cd ARK
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## 2. Run the baseline experiments

```bash
ark --help
ark run --help
ark run --agent goal_following --perturbation none --monitor safety --episodes 5 --seed 42 --output baseline.json
ark run --agent reward_maximizing --perturbation reward_conflict --monitor safety --episodes 10 --seed 42 --output reward-conflict.json
```

Compare the JSON summaries. Keep the seed, agent, perturbation, monitor, and episode count with every reported result.

Available built-in CLI agents: `goal_following`, `reward_maximizing`, `safety_constrained`, and `random`. Conditions include no perturbation, reward conflict, false goal, altered evaluation, goal drift, observation noise, and action delay.

## 3. Run a local model

ARK currently exposes one live model adapter: Ollama.

1. Install Ollama and start its local service.
2. Pull a model, for example `ollama pull llama3`.
3. Run:

```bash
ark run --agent ollama --model llama3 --perturbation goal_drift --monitor safety --episodes 5 --seed 42 --output ollama-test.json
```

For a custom endpoint, set `OLLAMA_HOST` or use the CLI's `--ollama-host` option. The model receives the agent-facing observation and must return one of `UP`, `DOWN`, `LEFT`, `RIGHT`, or `STAY`. Invalid action text is converted to `STAY` and counted. Network/server errors fail the run rather than being reported as a completed evaluation.

The Ollama adapter tests use a mocked HTTP response in CI. A live model run requires a reachable local Ollama server and a model installed on that machine.

## 4. Open ARKWorld

```bash
streamlit run arkworld.py
```

Open http://localhost:8501. ARKWorld is a Streamlit hub for the available research and simulation pages. It is not currently a drag-and-drop multi-agent GridWorld editor.

## 5. Test and validate

```bash
ruff check src tests pages
python -m compileall -q src pages
pytest tests -q
```

The release workflow also runs deterministic baseline and reward-conflict experiments and checks that ARKWorld starts over HTTP.

## 6. Evidence and interpretation

- Treat each run as a synthetic experiment, not a real-world safety result.
- Keep generated JSON reports and exact source commit together.
- Report invalid model actions, monitor interventions, hazard hits, decoy attraction, and success metrics; do not reduce results to a single score.
- A green test suite verifies covered software paths only. It does not prove that every research module or external model behaves correctly.

## 7. Safety boundary

ARK's rule-based monitor is not an OS sandbox and does not stop a model from performing actions outside the simulated harness. No physical robot controller is connected. Use only controlled, synthetic environments for these experiments.
