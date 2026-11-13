# AI Engineering Worklog

## ✅ Work Done

### 2026-11-13 — Deep-dive sprint (deep-dive-sprint)

- Added a tabular Q-learning baseline with epsilon-greedy exploration and reproducible training seeds.
- Added a benchmark CLI comparing the learned policy with the scripted goal-following reference on the same held-out seed range, with the safety monitor enabled for both.
- Added remaining episode horizon to the learned state abstraction for the finite episode budget.
- Exported learned-policy APIs through the package.
- Added monitor adversarial regression cases covering prompt-injection-like, roleplay/jailbreak-like and token-smuggling-like inputs, forged observation fields and invalid actions.
- Hardened the safety monitor to use `env.agent_pos` as the authoritative position and reject boolean, fractional, string and out-of-range action values.
- Added cost-weighted threat alert-threshold calibration from labeled validation scores, reporting FPR, FNR, confusion counts and mean cost per validation sample.
- Aligned package `__version__` with `pyproject.toml` at 0.6.0.
- Added research notes describing methodology and limitations.
- Replaced failure-suppressing CI commands with blocking Ruff and pytest steps on Python 3.11, 3.12 and 3.13.
- Fixed strict Ruff findings discovered by the first unsuppressed CI run.

## 🚧 Work Left

- Run the Q-learning benchmark and record real metrics across the documented held-out seeds. No performance claim is made yet.
- Add stronger learned baselines (e.g. DQN/PPO) only after the compact tabular baseline is measured and its limitations are understood.
- The current local-observation Q-learning state omits distant map structure; it is a partial-observation abstraction, not a fully Markov encoding for arbitrary layouts.
- Fix and test the already documented limiter privilege-level behavior.
- Address the documented safety-monitor livelock on repeated blocked actions and compare success/recovery with and without monitor intervention.
- Validate the threat-index threshold using independently adjudicated validation episodes; report validation-set size, label protocol and held-out performance. Event weights remain heuristic.
- Obtain independent human/model review of the current full PR diff; earlier automated comments were inspected, but a fresh review of the final head is still outstanding.
- Explore adversarial multi-step bypasses, not only single-step structured inputs.

## 📊 Current Health

- Tests: GitHub Actions strict pytest suite PASSED on Python 3.11, 3.12 and 3.13 at commit `a76f018f3c21dfd8c5b2774ad97dea18003d243a`.
- Lint: GitHub Actions strict `ruff check src tests` PASSED on Python 3.11, 3.12 and 3.13 at the same commit.
- CI: All three matrix jobs passed in workflow run [43406239705](https://github.com/Gitcoder12/ARK/actions/runs/43406239705). No `|| true` or warning-only pytest fallback remains in the branch workflow.
- Coverage: Not measured.
- Security audit: Focused monitor trust-boundary hardening performed by source inspection and regression tests; no full security audit executed.
- Build/install: Editable package installation succeeded in all three CI jobs; no release artifact build was performed.
- Research benchmark: Not run for this change set; no measured Q-learning result claimed.
- Independent review: Final-head independent review still pending.

## 🧱 Architecture and Engineering Risks

- Q-learning is tabular and uses a compact partial-observation state; state aliasing is expected when different distant layouts share the same local observation.
- Training uses the environment reward. A policy that maximizes reward may learn reward-hacking behavior under conflicting incentives; that is a research signal, not a goal-alignment guarantee.
- The monitor uses privileged environment state (`agent_pos`, `intended_goal`) in this simulator. This is a trusted simulator boundary, not a deployable real-world sensor trust architecture.
- Prompt text itself is not parsed by the monitor. Prompt-injection tests exercise the PromptAgent parser and a separate structured monitor boundary.
- The adversarial bypass rate only describes the finite cases in the committed regression suite; it is not a comprehensive security rate.
- Threat-meter calibration selects an alert threshold on labeled validation data. It does not calibrate heuristic event weights or make the index a probability.

## 🔐 Security Findings

- Fixed on branch: monitor no longer trusts the position field supplied in an agent observation when checking candidate moves.
- Fixed on branch: invalid or malformed action values fail closed as BLOCK.
- Remaining: multi-step, state-manipulation, monitor-livelock and broader agent/tool threat-model testing.

## 🔍 Verification

- Inspected README, package metadata, CI workflow, monitor, grid-world environment, baseline agents, experiment runner, metrics, threat meter, existing tests and handoff document via the connected GitHub file interface.
- Strict GitHub Actions workflow run: [43406239705](https://github.com/Gitcoder12/ARK/actions/runs/43406239705).
- Exact validated commit: `a76f018f3c21dfd8c5b2774ad97dea18003d243a`.
- Python matrix: 3.11 PASS; 3.12 PASS; 3.13 PASS.
- Ruff and pytest are blocking steps; both passed in all three jobs.
- No local test execution is claimed.
- Next step: review the final diff and address remaining research/monitor limitations before considering merge.
