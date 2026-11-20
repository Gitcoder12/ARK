# ARK demos

These demos exercise the currently implemented constitutional action gate. They do not prove general agent alignment or provide operating-system sandboxing.

## 1. Install and run the test suite

From the repository root:

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1

python -m pip install -e ".[dev]"
pytest -q
```

## 2. Run a constitutional action-gate demo

Save as `examples/constitution_gate_demo.py`:

```python
from ark.envs.grid_world import Action
from ark.limiters.gates import ActionLimiter, GateDecision

gate = ActionLimiter()

# A valid action from the finite GridWorld action set.
allowed = gate.gate(int(Action.STAY))
print("normal:", allowed.decision.value, "->", allowed.action)

# Explicitly deny one action and show the gate replacing it with STAY.
gate.denied_actions.add(int(Action.RIGHT))
blocked = gate.gate(int(Action.RIGHT))
print("denied:", blocked.decision.value, "->", blocked.action)
print("reason:", blocked.reason)

# Activate the kill switch: subsequent proposals resolve to STAY.
gate.kill("demo shutdown")
stopped = gate.gate(int(Action.RIGHT))
print("shutdown:", stopped.decision.value, "->", stopped.action)
assert stopped.decision is GateDecision.KILL
assert stopped.action == int(Action.STAY)

print("audit events:", len(gate.policy_engine.audit_events))
```

Run it:

```bash
python examples/constitution_gate_demo.py
```

Expected behavior: the ordinary action passes; the explicitly denied action is blocked and replaced with STAY; after shutdown, every proposed action is forced to STAY. Exact enum integer values are intentionally not hard-coded.

## 3. Run a small benchmark

```bash
python -m ark.experiments.runner --episodes 20
python -m ark.experiments.prompt_arena --attack all --episodes 10
```

## Current boundary

The constitutional engine currently gates discrete actions in the ARK runtime. It does not yet isolate arbitrary model code, tool processes, network access, filesystems, or external devices. The proposed DangerBox must add those boundaries separately; a Python policy check is not a sandbox.
