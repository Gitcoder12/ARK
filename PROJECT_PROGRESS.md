# ARK — Whole-Project Progress

**Snapshot:** 2026-11-20  
**Default branch:** `main`  
**Active work branch:** `feat/arkbox-reproducible-environments`  
**Tracking PR:** [#47 — ARKBox](https://github.com/Gitcoder12/ARK/pull/47)  
**Scope:** Whole ARK project, including ARKWorld and ARKBox as separate systems.  
**Estimate:** **47%** — engineering and research maturity estimate, not test coverage or a claim of real-world safety.

## Progress meter

```text
ARK  [█████████░░░░░░░░░░░] 47%
```

## Capability ledger

| Capability | Estimate | Current evidence / remaining work |
|---|---:|---|
| Core GridWorld environment | 85% | Existing configurable grid, hazards, goals, decoys and seeded runs; broaden scenario validation and environment abstractions |
| Scripted agents and benchmark experiments | 80% | Multiple baselines and controlled conditions exist; add stronger baselines and independent reproductions |
| Perturbations and memory attacks | 70% | Reward conflict, false goal, altered evaluation, observation noise, action delay, goal drift and memory corruption exist; extend adversarial coverage |
| Runtime monitor and safety controls | 55% | ALLOW/BLOCK/REPLAN and related controls exist; address livelock, bypasses, formal constraints and false decisions |
| Corrigibility and governance | 55% | Shutdown, limiters, ownership and governance prototypes exist; verify distinct behavior and adversarial robustness |
| ARKWorld | 70% | Simulation registry and launch hub organize independent worlds; strengthen common run interface and exports |
| ARKBox | 30% | Versioned GridWorld scenarios, integrity checks and experiment records implemented in PR #47; add more adapters and full orchestration |
| Reproducibility and research validation | 45% | Results and confidence intervals are documented; reproduce from exact commits, seeds and configurations and improve statistical protocol |
| Learned / real AI-agent integration | 15% | Early Q-learning baseline work exists; robust learned agents and live model adapters are not yet a complete benchmark integration |
| Robotics simulator integration | 0% | MuJoCo / Isaac / PyBullet adapter and robot-specific evaluation not yet implemented |

**Whole-project estimate: 47%.** The ledger is a reasoned engineering estimate. It is not the arithmetic average of line counts, PRs or test counts.

## Architecture boundary — do not blur these modules

- **ARKWorld:** simulation registry and launch hub. It organizes and launches bounded environments and research tools.
- **ARKBox:** scenario and experiment library. It stores reusable environment definitions, versions, configuration snapshots, seeds, provenance and experiment records.
- **World engines:** remain independent modules under ARKWorld. They load a scenario from ARKBox when appropriate and return run traces / metrics for storage.
- ARKBox must not become a simulation engine. ARKWorld must not become a file-storage replacement.

## Current implementation record

### ARKBox v0.1 foundation

- Validated GridWorld scenario definitions.
- Content-hash verification when loading scenario files.
- Build the existing GridWorld from a stored scenario.
- Store experiment provenance: scenario hash, agent, seed, config, metrics, code revision and environment metadata.
- CLI entry point: `ark-box`.
- Tests cover scenario validation, storage integrity, environment construction, experiment records and CLI.
- Documentation: [docs/ARKBOX.md](docs/ARKBOX.md).
- Separation from ARKWorld documented in [docs/ARKWORLD.md](docs/ARKWORLD.md).

**Limitations:** The first adapter supports ARK's existing GridWorld only. ARKBox records experiment metadata and caller-supplied metrics; it does not itself execute or certify an experiment. No physical-robot simulator is included.

## Release gates still required

1. Reproduce documented benchmark tables from the exact committed scripts, seeds and configurations.
2. Fix monitor livelock and verify limiter levels with adversarial regression tests.
3. Add bypass probes, long-horizon goal integrity, evaluator gaming and tool-use scenarios.
4. Integrate learned agents and real model adapters without confusing scripted baselines with learned systems.
5. Expand ARKBox to reusable environment adapters and full scenario / experiment orchestration.
6. Add a robotics simulator adapter with safety-focused tests; keep simulation and physical hardware claims separate.
7. Produce independent research evaluation, ablations, failure traces and limitations.

## Update protocol

- Update this file in the same work branch/session whenever project code is changed.
- Change a capability percentage only when implementation evidence supports it; record the code commit and exact CI run.
- A green CI result applies only to the exact tested commit. Documentation-only commits after that run must be marked unverified until rechecked.
- Never count a draft PR or generated code as shipped.
- Keep ARKWorld and ARKBox separate.
- Do not modify forked repositories or repositories outside RepoForge and ARK.
- Do not merge to `main` without review and verified checks.

## Latest verified baseline

- Main at snapshot: `894d6b92fb3ac01d12c7b9fb0a60635a62780cea`.
- ARKBox CI run [44601156241](https://github.com/Gitcoder12/ARK/actions/runs/44601156241) passed test / lint jobs on commit `c1ec89ecdf2f51307f28c515c0c906239604b61f`.
- PR #47 remains open and draft. No merge to `main` has been made by this work.
