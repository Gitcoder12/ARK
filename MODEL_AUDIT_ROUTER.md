# Independent Model Audit Router — ARK

**Revision date:** 2026-11-13

## Non-negotiable data-integrity rules
- Never replace maintainer/user-provided data with fabricated or synthetic records.
- Trace every benchmark, dataset, label, seed, metric, model ID and source to a reproducible origin.
- Keep synthetic episodes explicitly labelled and separate from external/real-world evidence.
- Never invent model results, alignment claims, test runs, citations or people.
- Report unknown or unverifiable details as unknown; do not fill gaps by guessing.
- Do not call a heuristic score a calibrated probability or claim general safety from a finite benchmark.

## README preservation
Recover the last maintainer-authored README from Git history before changing it. Preserve its wording, structure, links, and original claims. Do not replace it. Any AI-maintained explanation must be a dated, clearly labelled section at the bottom only.

## Independent review agents
1. **Research-methods checker:** threat model, hypotheses, baselines, seeds, train/evaluation separation, confidence intervals, ablations, metric validity.
2. **Data-provenance checker:** origin, licences, label process, synthetic-vs-real status, benchmark contamination and reproducibility.
3. **Agent-safety reviewer:** threat model, monitor trust boundaries, bypasses, fail-open/fail-closed behaviour, privileged simulator state, false positives and false negatives.
4. **Code reviewer:** architecture, types, edge cases, reproducibility and error handling.
5. **Test/CI reviewer:** exact PR-head test/lint/build results; detect suppressed failures and stale green checks.
6. **Documentation reviewer:** ensure research claims match code and evidence, preserve README original and attribution.
7. **Career-integrity reviewer:** ensure portfolio claims are demonstrable and no employer relationship is implied.

## Required audit output
For every issue report severity (P0/P1/P2/P3), exact file/line/symbol, reproduction, expected/actual result, evidence and commit SHA, confirmed/suspected/unverifiable status, smallest fix, and a regression test. Do not modify code while performing the audit.

## Required audit sequence
1. Record exact repository HEAD and PR head.
2. Inspect merged, open, closed-unmerged and reverted work separately.
3. Trace all benchmark data and generated artefacts.
4. Review README provenance and preserve the original.
5. Run tests and lint on the exact reviewed commit.
6. Review security assumptions, limitations and monitor trust boundaries.
7. Independently reproduce key results before endorsing them.

## Merge gate
- [ ] No fabricated data or unsupported claims.
- [ ] Real and user-provided data preserved.
- [ ] Synthetic environments clearly labelled.
- [ ] Metrics reproducible with documented seeds and methodology.
- [ ] CI passes at exact PR head or failures explicitly disclosed.
- [ ] README original preserved; AI addendum appears at bottom only.
- [ ] Independent second review completed.
- [ ] Maintainer approval recorded.

**Repository-specific reminder:** ARK is an experimental agent-alignment and reliability research framework. Passing simulator tests does not establish real-world alignment, robustness or safety. Clearly document privileged simulator state, partial observability, heuristic threat weights, benchmark coverage and all unrun experiments.
