# Milestone 2 Plan: Bridge Hardening + UX (Option 5)

Date: 2026-03-02
Status: approved for execution

## Scope

This milestone is an ash-mode bridge hardening and usability pass from the current stable baseline.

In-scope:
- shell<->python bridge correctness and diagnostics in ash mode
- deterministic failure contracts
- regression and stress coverage for bridge paths
- improved CLI/bridge usability docs and examples

Explicitly out-of-scope for this milestone:
- shell-side typed array/assoc semantics
- shell list/dict mapping behavior
- full bash-compat extensions (deferred to the next milestone)

## Week 1: Hardening

### Step 1: Scope freeze in docs and contracts
- Lock ash-mode bridge scope as scalar-first (`scalar`, `integer` only).
- Mark list/dict shell mapping and `array`/`assoc` tie types as deferred.
- Ensure docs/spec/checklist/limitations agree.

Exit:
- docs updated and consistent
- no ambiguity about deferred typed collections

### Step 2: Failure contract normalization
- Normalize bridge failure signaling for `py`, `python:`, and `PYTHON ... END_PYTHON`.
- Define and enforce structured exception variable behavior (`PYTHON_EXCEPTION*`).
- Ensure stale structured exception state is cleared on successful structured runs.

Exit:
- deterministic status + env-variable behavior for structured exception path
- regression tests for contract

### Step 3: Hardening regression cases
- Add focused regression rows for:
  - structured exception reset behavior
  - deferred list/dict and `array`/`assoc` tie rejection behavior
  - callable resolution edge diagnostics

Exit:
- targeted bridge regressions pass locally

### Step 4: Stress reliability pass
- Run/extend stress harness to exercise bridge paths repeatedly under bounded resources.
- Preserve fail-on-first-mismatch semantics; no masking of failures.

Exit:
- stress harness produces repeatable pass/fail outcome and artifacts

### Step 5: Week-1 checkpoint report
- Record implemented changes, remaining deltas, and evidence.

Exit:
- short report in `docs/reports/`

## Week 2: UX and ergonomics

### Step 6: `python:` diagnostic UX
- Improve diagnostics when callable resolution fails and fallback execution also fails.
- Keep behavior compatible with established `python:` dispatch rule.

Exit:
- clearer error messages with actionable context

### Step 7: Scalar coercion messaging
- Improve callable argument coercion diagnostics (where cast/fallback is ambiguous).
- Keep runtime behavior deterministic and backward-compatible for ash mode.

Exit:
- clearer argument/type error output in bridge paths

### Step 8: Docs and examples
- Add/update practical examples for `py`, `python:`, `PYTHON` block, `from ... import ...`, ties.
- Keep examples ash-mode-compatible and scalar-first.

Exit:
- docs reflect actual runtime behavior and constraints

### Step 9: UX regression rows
- Add regression cases for diagnostics and examples from Step 8.

Exit:
- coverage protects UX contract from regressions

### Step 10: Week-2 checkpoint report
- Record final week-2 outcomes and residual tasks.

Exit:
- report in `docs/reports/`

## Validation Gates

Per-step local checks:
- `tests/bridge/run.sh`
- `tests/regressions/run.sh`

Periodic broader checks:
- `make conformance-quick`
- selected BusyBox ash modules via `src/tests/run_busybox_ash.sh`

Resource guardrails:
- memory cap policy remains enforced (no implicit cap increase)
- fail-fast on first mismatch for reliability runs

## Bash-Gap Closure Backlog (Added 2026-03-03)

Source of truth report:
- `docs/reports/bash-gap-latest.md`

Dual-lane policy:
- ash lane remains strict against ash baseline and must stay green.
- bash lane uses `BASH_COMPAT`-mirrored parity against bash baseline (with `--posix` mirrored where set).

Current bash-lane mismatches:
1. `bash-compat-array-append`: stdout mismatch
2. `bash-compat-array-append`: stderr mismatch
3. `bash-compat-assoc-keys`: stdout mismatch

Planned closure order:
1. Fix `arr+=(...)` append semantics and remove diagnostic noise for bash lane.
2. Implement `${!assoc[@]}` key expansion parity and ordering behavior compatible with bash baseline expectations.
3. Re-run `make diff-parity-matrix` and reduce bash mismatch count to zero for current bash case set.
4. Expand bash case corpus (`declare`, array ops, assoc ops, expansion edge cases) and iterate with strict parity.

### Subscript Evaluation Semantics (Addendum)

Requirement:
- Indexed array subscripts are arithmetic-evaluated.
- Assoc subscripts are string keys (no arithmetic evaluation).

Implementation tasks:
1. Introduce indexed-subscript arithmetic evaluation helper in runtime.
2. Route indexed assignment/read/unset through helper.
3. Preserve assoc string-key path for assignment/read/unset.
4. Align diagnostics and non-zero statuses with bash-parity expectations for invalid indexed expressions.

Test tasks:
1. Add `tests/diff/cases/bash-compat-subscript-eval-indexed.sh`.
2. Add `tests/diff/cases/bash-compat-subscript-eval-assoc.sh`.
3. Include mixed cases where key text is numeric-like (`"01"`, `"1+1"`) to ensure mode-specific behavior.
4. Gate with `PARITY_BASH_COMPAT=50 PARITY_MIRROR_POSIX=1 tests/diff/run.sh --case bash-compat-subscript-eval-`.

## Delivery Model

- Commit after each numbered step.
- Keep commits scoped and message-prefixed by area (`docs`, `runtime`, `tests`, `report`).
