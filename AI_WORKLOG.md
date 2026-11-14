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


## 2026-11-13 — Identity measurement review fixes

### Findings addressed
- Identity drift for unseen stimuli now uses the captured baseline entity's name prefix, matching the behavioral-signature format and avoiding false drift for unchanged entities.
- An explicitly empty baseline signature is now respected; only `None` selects the captured baseline.
- Memory replacement accepts an explicit simulation step. If omitted, it advances from the last recorded step rather than using the number of log entries.
- Charter integrity now uses Jaccard similarity, so both removed and added principles reduce integrity. Empty/empty charters remain fully intact.

### Regression coverage
- Added tests for unseen stimuli, explicitly empty baseline signatures, added conflicting charter principles, and replacement-log step continuity.
- Updated ValueCharter integrity expectation to reflect symmetric charter comparison.

### Exact-head validation
- Validated branch head: `f081d21eb6ae96886c074594abd1fb7a3e4f851e`.
- GitHub Actions run: [43411923032](https://github.com/Gitcoder12/ARK/actions/runs/43411923032).
- Python 3.11, 3.12 and 3.13: strict Ruff and pytest passed.
- Pytest: 130 passed on each Python version.
- No merge performed; independent review and repository approval remain required.

## 2026-11-13 — Portfolio audit of current main and open engineering PRs

### Audit record
- Audited main HEAD: `703481a0eaffd32e7340643a6b6a02de33e17472`.
- Main recursive tree: 83 tracked files, 14 test modules, one CI workflow, package metadata, examples, and research documentation.
- Recommendation: IMPROVE / highest-priority research-engineering flagship.

### Confirmed main-branch findings
- Main CI is fail-open: `.github/workflows/ci.yml` runs `ruff check src/ || true` and `pytest tests/ -v || echo "Tests finished with warnings"`. Lint and test failures do not fail the workflow. Treat any green status from this workflow as non-evidence of a passing quality gate.
- In main `src/ark/evaluation/monitor.py`, `SafetyMonitor.evaluate` obtains candidate position from `obs["position"]`. If observations are attacker-controlled or corrupted, the monitor can evaluate a move from a forged position. Open PR #18 changes the trust boundary to use environment-owned `env.agent_pos` and validates malformed action values.
- The threat meter is explicitly documented as an experimental heuristic, not a calibrated real-world risk probability. Do not present its output as a probability or safety guarantee.
- The README describes scripted baseline agents and outstanding research limitations. The new Q-learning baseline in PR #18 is still a bounded tabular, partial-observation experiment; empirical benchmark performance has not yet been recorded.

### Existing review work
- [PR #17](https://github.com/Gitcoder12/ARK/pull/17) replaces the failure-suppressing CI behavior and includes identity/charter changes plus AI_WORKLOG.
- [PR #18](https://github.com/Gitcoder12/ARK/pull/18) adds learned baseline, adversarial monitor probes, threat-threshold calibration, regression tests, and AI_WORKLOG.
- GitHub Actions runs associated with the current PR heads completed successfully: [PR #17 run 43413225240](https://github.com/Gitcoder12/ARK/actions/runs/43413225240) and [PR #18 run 43458320424](https://github.com/Gitcoder12/ARK/actions/runs/43458320424).
- Codex review receipt comments exist on PRs #17 and #18, but the recorded review state is COMMENTED and the receipt text is generic. This is not a substantive independent approval of the current final head.
- PR #20 is documentation-only; do not duplicate the existing AI_WORKLOG on the deep-dive code branch.

### Verification
- Inspected main README, pyproject, CI workflow, monitor, threat meter, recursive source/test tree, open issues and relevant PR metadata.
- No local tests were run in this audit.
- PR CI evidence is branch-specific and does not change main until the PR is reviewed and merged.
- Independent final-head review: NOT COMPLETE.
- Q-learning benchmark, broad multi-step adversarial evaluation, monitor livelock analysis, and threat-index external validation: NOT RUN in this audit.

### Next actions
1. Review and reconcile PRs #17 and #18; do not merge until their final exact heads have a substantive independent review.
2. Run benchmark seeds and publish measured results with uncertainty, baseline details, and limitations.
3. Add multi-step monitor bypass, livelock, and limiter privilege tests.
4. Keep simulator privileged-state assumptions explicit; do not claim real-robot deployment safety.
