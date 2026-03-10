# Cross-Gate Sweep Report

Generated: 2026-03-10
Runner: local `make` gates with per-target timeout guards

## Targets Run

- `make regressions` (timeout 600s)
- `make bridge-conformance` (timeout 600s)
- `make diff-parity-matrix` (timeout 600s)
- `make compat-posix-bash-strict` (timeout 1200s)
- `make bash-builtin-matrix` (timeout 1200s)
- `make bash-posix-man-matrix` (timeout 1200s)
- `make bash-posix-upstream-matrix` (timeout 1200s)
- `make compliance-truth-check` (timeout 1200s)
- `make conformance-full` (timeout 1800s)

## Summary

- Passed: 6/9
- Failed: 3/9
- Timed out: 0/9

Pass:

- `regressions`
- `bridge-conformance`
- `conformance-full`
- `compat-posix-bash-strict`
- `bash-builtin-matrix`
- `bash-posix-man-matrix`

Fail:

- `diff-parity-matrix`
- `bash-posix-upstream-matrix`
- `compliance-truth-check`

## Failure Details

1. `diff-parity-matrix`

- Matrix completed and reported mismatches:
  - ash lane: `mismatches=1`
  - bash lane: `mismatches=8`
- Gap report written: `docs/reports/bash-gap-latest.md`

2. `bash-posix-upstream-matrix`

- Gate failed for upstream core lane.
- Gap report: `docs/reports/bash-posix-upstream-gap-latest.md`
- Current upstream core parity: `6/9` (3 failing rows)

3. `compliance-truth-check`

- Failure reason: `inconsistent reports: failing gates but remaining-work says 0`

## Artifacts

- Raw sweep log: `docs/reports/cross-gate-sweep-latest.log`
- Consolidated sweep report: `docs/reports/cross-gate-sweep-latest.md`
- Parity matrix gap report: `docs/reports/bash-gap-latest.md`
- POSIX upstream gap report: `docs/reports/bash-posix-upstream-gap-latest.md`

## Immediate Next Fix Order

1. Resolve `bash-posix-upstream-matrix` failing rows (from `bash-posix-upstream-gap-latest.md`).
2. Re-run `diff-parity-matrix` and reduce ash/bash lane mismatch counts.
3. Keep `docs/reports/bash-compliance-remaining-work-latest.md` and `docs/reports/bash-compliance-gaps-latest.md` aligned with gate outputs so `compliance-truth-check` passes.
