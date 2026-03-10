# Effective Gap Board

Generated: 2026-03-10

Purpose: merge static row coverage with runnable gate evidence, so "covered" means "implemented and still passing evidence."

## Current Row Coverage (Static Matrix)

Source: `docs/specs/bash-man-implementation-matrix.tsv`

- Total rows: `422`
- `mctash_default=covered`: `422`
- `mctash_posix=covered`: `422`
- Rows not marked covered: `0`

Interpretation: matrix labeling is complete, but this does not by itself prove live parity.

## Effective Gaps (Evidence-Backed)

### EGB-001: Diff parity matrix still non-green

- Source: `docs/reports/bash-gap-latest.md`
- Current evidence:
  - ash lane mismatches: `8`
  - bash lane mismatches: `33`
- Gap to close:
  - reduce both mismatch sets to `0`
  - keep `tests/diff/run_parity_matrix.sh` green in gate runs

### EGB-002: Upstream bash POSIX lane not full parity

- Source: `docs/reports/bash-posix-upstream-gap-latest.md`
- Current evidence:
  - core full parity: `4/9`
  - failing rows: `5`
    - `posix2.tests`
    - `posixexp.tests`
    - `ifs-posix.tests`
    - `comsub-posix.tests`
    - `builtins.tests`
- Gap to close:
  - bring upstream core parity to `9/9`
  - keep `make bash-posix-upstream-matrix` green

### EGB-003: BusyBox stage blocks full conformance run

- Sources:
  - bounded conformance run logs (`make conformance-full` with bounded timeouts)
  - `docs/reports/busybox-timeout-reproducer-latest.md`
- Current evidence:
  - BusyBox stage can exit `124` (timeout)
  - timeout offenders shown by reproducer scan (module-dependent on timeout budget)
  - strict allowlist policy still reports unexpected BusyBox `.fail` files in bounded runs
- Gap to close:
  - no timeout exits under agreed CI time budget
  - policy decision and implementation for BusyBox fail-file handling:
    - either reduce unexpected fail files to policy target, or
    - explicitly track/allowlist with rationale

### EGB-004: Compliance truth drift risk

- Source: prior `compliance-truth-check` failures in gate sweeps
- Current evidence:
  - report state and gate state can diverge (e.g., "remaining work: 0" while gates fail)
- Gap to close:
  - regenerate reports from current gate outputs before `compliance-truth-check`
  - make truth-check green on same commit as gate results

## Gate Snapshot (Most Recent Known)

- `make regressions`: pass (local run in this workspace on 2026-03-10)
- `make bash-posix-man-matrix`: previously green in latest sweep cycle
- `make diff-parity-matrix`: currently non-green by latest gap report
- `make bash-posix-upstream-matrix`: currently non-green by latest gap report
- `make conformance-full`: currently blocked by BusyBox stage timeout/policy failures in bounded runs

## Closure Definition For "Full Coverage Of Current Rows"

For current rows to be considered fully covered in practice:

1. static row status remains fully covered (`422/422` in both lanes), and
2. all mapped evidence gates are green on the same commit, and
3. compliance truth check is green on the same commit.

