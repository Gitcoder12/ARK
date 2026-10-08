# ARK v0.3 → v0.5.0 merge

## Decision
v0.4.1 is the architectural baseline. The old v0.3 package tree was not copied into the repository because it used a competing `ark/` layout and environment/evaluator interfaces.

## Kept and integrated
- **Goal drift** → `ark.perturbations.legacy.GoalDrift`
- **Observation noise** → `ark.perturbations.legacy.ObservationNoise`
- **Action delay** → `ark.perturbations.legacy.ActionDelay`
- **Model adapter abstraction** → `ark.adapters`
- v0.3 reward-hacking concept → retained by v0.4.1's `RewardConflict`
- v0.3 memory-corruption concept → retained and expanded by v0.4.1's `memory` module
- v0.3 safety-monitor concept → retained and expanded by v0.4.1's `evaluation` monitor
- v0.3 metrics/benchmark intent → retained by v0.4.1's `metrics` and `experiments`

## Not copied
- Old `ark/environments`, `ark/evaluators`, `ark/runner.py`, and `ark/config.py`: superseded by `src/ark/envs`, `evaluation`, and `experiments`.
- Old random/RL agent modules: v0.4.1 already has the current baseline-agent API; the old RL implementation was not carried forward without evidence it fits the new environment interface.
- Old report generator: v0.4.1's episode/aggregate metrics are the active reporting foundation; incompatible legacy reporting code was not duplicated.
- Generated `src/ark_alignment.egg-info/`: removed; it is build output and should not be versioned.

## Principle
Keep research ideas, not duplicate architectures. The merged codebase should have one active environment API, one evaluation API, and one package layout.

## Post-merge changes (v0.5.0 final)
- `legacy.py` rewritten: `GoalDrift` no longer deep-copies every step; returns the same env when nothing changes.
- Legacy stressors are now real benchmark conditions (`goal_drift`, `observation_noise`, `action_delay`) in `ark.experiments.runner`.
- Agents plan from the *perceived* grid (`perceived_grid`), so observation noise actually affects them. The safety monitor still reads ground truth.
- Adapter `Action` renamed `AdapterAction` (alias kept) to avoid clashing with the grid move enum.
