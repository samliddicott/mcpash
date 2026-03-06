# Plan 008: Compliance Gap Closure Priority

Date: 2026-03-06

Goal:

- Close known behavior mismatches and known-unknown reporting risks before any broad compliance/replacement claim.

## Priority Order

1. Fix invocation output parity (`--dump-po-strings`).
2. Close upstream POSIX strict-lane core failures.
3. Reconcile compliance reports so all dashboards agree.
4. Add a single "truth gate" that regenerates and validates every compliance report.

## Work Breakdown

### P1. Invocation parity fix

- Area: gettext dump output source marker for `-c`.
- Current mismatch:
  - bash: `#: -c:1`
  - mctash: `#: bash:1`
- Changes:
  - Update dump-strings/po emitter to preserve invocation-source label semantics for `-c` scripts.
  - Add direct regression case for exact expected line.
- Gate:
  - `tests/compat/run_bash_invocation_option_matrix.sh` fully green.

### P2. Upstream POSIX strict lane closure

- Area: `tests/compat/run_bash_posix_upstream_matrix.sh`.
- Current failing cases (from latest report):
  - `posix2.tests`
  - `posixexp.tests`
  - `ifs-posix.tests`
  - `comsub-posix.tests`
  - `set-e.tests`
- Changes:
  - Reproduce each failure with per-case diffs from `tests/bash/upstream/.../run-lanes/diff`.
  - Fix in this order: `set-e` -> `comsub` -> `ifs` -> `posix2` -> `posixexp`.
  - Keep strict status/stdout/stderr parity; do not widen normalizations.
- Gate:
  - `make bash-posix-upstream-matrix` green with `core full parity: 9/9`.

### P3. Report reconciliation

- Area: report consistency.
- Changes:
  - Rebuild/update:
    - `docs/reports/bash-compliance-remaining-work-latest.md`
    - `docs/reports/bash-compliance-gaps-latest.md`
    - `docs/reports/bash-category-buckets-latest.md`
    - `docs/reports/bash-posix-upstream-gap-latest.md`
    - `docs/reports/bash-posix-man-matrix-latest.md`
  - Sync partial/covered statuses with:
    - `docs/gap-board.md`
    - `docs/posix-shall-trace.md`
    - `docs/specs/bash-man-implementation-matrix.tsv`
- Gate:
  - No contradictory status statements across these files.

### P4. Truth gate for compliance claims

- Add `make compliance-truth-gate` that runs:
  - `tests/compat/run_bash_invocation_option_matrix.sh`
  - `tests/compat/run_bash_posix_man_matrix.sh`
  - `tests/compat/run_bash_posix_upstream_matrix.sh`
  - `tests/compat/run_bash_builtin_matrix.sh`
  - report regeneration + consistency checker script.
- Checker fails if:
  - any command gate fails, or
  - any report claims zero gaps while another canonical report marks partial/failing.

## Definition of Done

- Invocation matrix: pass.
- Upstream POSIX matrix: core 9/9 pass.
- Report set consistent (no conflicting closure claims).
- `make compliance-truth-gate` pass at HEAD.
