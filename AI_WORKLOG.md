# AI Engineering Worklog

## ✅ Work Done

### 2026-11-13 — Deep-dive sprint (deep-dive-sprint)

- Added a tabular Q-learning baseline with epsilon-greedy exploration and reproducible training seeds.
- Added a benchmark CLI comparing the learned policy with the scripted goal-following reference on the same held-out seed range, with the safety monitor enabled for both.
- Added remaining episode horizon to the learned state abstraction for the finite episode budget.
- Exported learned-policy APIs through the package.
- Added monitor adversarial regression cases covering prompt-injection-like, roleplay/jailbreak-like and token-smuggling-like inputs, forged observation fields and invalid actions.
- Hardened the safety monitor to use env.agent_pos as the authoritative position and reject boolean, fractional, string and out-of-range action values.
- Added cost-weighted threat alert-threshold calibration from labeled validation scores, reporting FPR, FNR, confusion counts and expected cost.
- Aligned package __version__ with pyproject.toml at 0.6.0.
- Added research notes describing methodology and limitations.

## 🚧 Work Left

- Run the full test suite and Ruff locally or through strict pull-request CI; no local execution is claimed.
- Existing main-branch CI has historically suppressed Ruff/pytest failures. PR #17 proposes making those checks blocking; verify its status and ensure the effective acceptance workflow is strict.
- Run the Q-learning benchmark and record real metrics across the documented held-out seeds. No performance claim is made yet.
- Add stronger learned baselines (e.g. DQN/PPO) only after the compact tabular baseline is measured and its limitations are understood.
- The current local-observation Q-learning state omits distant map structure; it is a partial-observation abstraction, not a fully Markov encoding for arbitrary layouts.
- Fix and test the already documented limiter privilege-level behavior.
- Address the documented safety-monitor livelock on repeated blocked actions and compare success/recovery with and without monitor intervention.
- Validate the threat-index threshold using independently adjudicated validation episodes; report validation-set size, label protocol and held-out performance. Event weights remain heuristic.
- Conduct independent review of the actual PR diff by another model or reviewer; not performed by this agent.
- Explore adversarial multi-step bypasses, not only single-step structured inputs.

## 📊 Current Health

- Tests: New regression tests added; execution status NOT RUN in this connected GitHub-only session.
- Coverage: Not measured.
- CI: Existing main-branch workflow can suppress lint/test failures; separate strict-CI PR #17 exists.
- Lint: NOT RUN locally.
- Security audit: Focused monitor trust-boundary hardening performed by source inspection; no full security audit executed.
- Build: NOT RUN locally.
- Research benchmark: Not run for this change set; no measured Q-learning result claimed.
- Independent review: NOT PERFORMED.

## 🧱 Architecture and Engineering Risks

- Q-learning is tabular and uses a compact partial-observation state; state aliasing is expected when different distant layouts share the same local observation.
- Training uses the environment reward. A policy that maximizes reward may learn reward-hacking behavior under conflicting incentives; that is a research signal, not a goal-alignment guarantee.
- The monitor uses privileged environment state (agent_pos, intended_goal) in this simulator. This is a trusted simulator boundary, not a deployable real-world sensor trust architecture.
- Prompt text itself is not parsed by the monitor. Prompt-injection tests exercise the PromptAgent parser and a separate structured monitor boundary.
- The adversarial bypass rate only describes the finite cases in the committed regression suite; it is not a comprehensive security rate.
- Threat-meter calibration selects an alert threshold on labeled validation data. It does not calibrate heuristic event weights or make the index a probability.

## 🔐 Security Findings

- Fixed on branch: monitor no longer trusts the position field supplied in an agent observation when checking candidate moves.
- Fixed on branch: invalid or malformed action values fail closed as BLOCK.
- Remaining: multi-step, state-manipulation, monitor-livelock and broader agent/tool threat-model testing.

## 🔍 Verification

- Inspected README, package metadata, CI workflow, monitor, grid-world environment, baseline agents, experiment runner, metrics, threat meter, existing tests and handoff document via the connected GitHub file interface.
- Checks actually executed: GitHub branch comparison and repository file retrieval only.
- pytest: NOT RUN.
- Ruff: NOT RUN.
- Build/install: NOT RUN.
- CI workflow result for this branch: Not yet verified.
- Next step: open a review PR, then inspect actual GitHub Actions results and resolve every failure before merge.
