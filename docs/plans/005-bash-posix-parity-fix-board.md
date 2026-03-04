# 005 - Bash POSIX Parity Fix Board

Date: 2026-03-04

Goal:

- Close all `partial`/uncovered builtins that are **not** marked `out_of_scope` in the bash POSIX coverage map.
- Use strict differential evidence against `bash --posix`.

Baseline references:

- Coverage map: `tests/compat/bash_posix_man_coverage.tsv`
- Current man-matrix: `docs/reports/bash-posix-man-matrix-latest.md`
- Pre-implementation mismatch analysis: `docs/reports/bash-posix-mismatch-analysis-pre-implementation.md`

## In-Scope Partial Builtins To Close

From coverage map (`partial`, excluding `out_of_scope`):

- `.` (dot/source semantics)
- `bg` (interactive)
- `break`
- `builtin`
- `continue`
- `declare` (posix-lane assertions for current policy)
- `exit`
- `fc`
- `fg` (interactive)
- `jobs` (interactive)
- `return`
- `source` (alias of `.` behavior in compatibility lane)

Definition of done for each builtin:

1. Dedicated bash-posix case file exists under `tests/diff/cases/`.
2. Added to `tests/compat/bash_posix_man_coverage.tsv` as `covered`.
3. Included in `make bash-posix-man-matrix` run.
4. Passes differential check in strict mode (status/stdout/stderr parity or explicitly documented allowed diagnostic wording deltas).

## Work Board

## A. Harness/Case-Splitting (No runtime changes)

A1. Split POSIX lane from extension-heavy upstream tests

- Keep strict gate on POSIX-core subset:
  - `posix2.tests`, `posixexp.tests`, `posixexp2.tests`, `posixpat.tests`, `posixpipe.tests`, `ifs-posix.tests`, `comsub-posix.tests`, `set-e.tests`
- Move `builtins.tests` to informational lane, then carve POSIX-safe slices into targeted differential case files.

Benefit:

- Prevents bash-extension noise from obscuring true POSIX defects.

A2. Add matrix reports

- `docs/reports/bash-posix-man-matrix-latest.md` (existing)
- `docs/reports/bash-posix-upstream-gap-latest.md` (existing)
- New aggregate status row in gap board linking both.

Benefit:

- Single visibility for targeted builtin closure + upstream semantic drift.

## B. Partial Builtin Closure Board

B1. `.` and `source`

Cases to add:

- `man-bash-posix-05-dot-source.sh`

Coverage:

- relative vs absolute path resolution
- positional arguments through dot invocation
- failure status when file missing
- `PATH` search behavior differences (posix mode)

B2. `break` and `continue`

Cases to add:

- `man-bash-posix-06-loop-control.sh`

Coverage:

- simple loop levels (`break`, `continue`)
- numeric argument (`break 2`, `continue 2`) in nested loops
- out-of-range/error status behavior

B3. `builtin`

Cases to add:

- `man-bash-posix-07-builtin-dispatch.sh`

Coverage:

- builtin dispatch success (`builtin echo`, `builtin test`)
- missing builtin diagnostic/status
- interaction with aliases/functions shadowing builtin names

B4. `declare` (posix-lane assertions)

Cases to add:

- `man-bash-posix-08-declare-posix-policy.sh`

Coverage:

- behavior in `--posix` with/without `BASH_COMPAT` as currently documented policy
- ensure diagnostics/status are stable and intentional

B5. `return` and `exit`

Cases to add:

- `man-bash-posix-09-return-exit.sh`

Coverage:

- function return statuses
- `return` outside function diagnostic/status
- `exit` status propagation in script and subshell contexts

B6. `jobs`, `fg`, `bg` (interactive lane)

Cases to add:

- `man-bash-posix-10-jobs-fg-bg-interactive.sh`

Coverage:

- PTY-only matrix with deterministic probes
- job listing, foreground/background movement, error status for invalid job specs

B7. `fc`

Cases to add/extend:

- extend `man-ash-fc*.sh` with bash-posix baseline variant and mode pinning

Coverage:

- listing, range selection, editor env behavior (`FCEDIT`/`EDITOR`) for non-interactive script-safe checks

## C. Known Current Mismatch Queue (From existing matrix)

C1. `unset readonly` control-flow in `man-bash-posix-01-core-state.sh`

- mismatch type: status + stdout tail truncation + stderr wording
- expected: script continues and emits trailing lines

C2. `command -v`/`type` in `man-bash-posix-02-path-command.sh`

- mismatch type: stdout content + miss status + stderr prefix
- expected: bash-style status and output selection in posix lane

C3. `times` + alias-miss diag in `man-bash-posix-04-misc-builtins.sh`

- mismatch type: stdout format + extra stderr
- expected: bash-compatible formatting/policy in this lane

## D. Execution Order

1. A1/A2 (harness and report clarity)
2. C1/C2/C3 (close currently failing covered man-matrix cases)
3. B1-B5 (non-interactive partial builtins)
4. B6/B7 (interactive/history-sensitive builtins)
5. promote all in-scope partials to `covered`

## E. Exit Criteria

Mandatory:

1. `make bash-posix-man-matrix` passes with zero mismatches.
2. `tests/compat/bash_posix_man_coverage.tsv` has no remaining `partial` rows except user-approved deferrals.
3. Upstream POSIX-core subset report shows no parser hard-fail/timeouts in selected strict lane.

Deferred (explicitly next milestone unless re-prioritized):

- Full bash-extension builtin surface (`enable`, `shopt`, `typeset`, completion/readline stack).
- Non-POSIX interactive/editor extras beyond declared scope.
