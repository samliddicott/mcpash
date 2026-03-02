# Milestone-2 Week-1 Hardening Report

Date: 2026-03-02
Plan reference: `docs/plans/003-milestone-2-bridge-hardening-and-ux.md`

## Completed Steps

1. Scope freeze
- Ash-mode bridge scope is now consistently documented as scalar-first.
- `list`/`dict` shell mapping and `array`/`assoc` tie types are explicitly deferred.
- Updated docs:
  - `docs/bridge-limitations.md`
  - `docs/bridge-test-trace.md`
  - `docs/bash-brush-python-bridge-spec.md`
  - `docs/bash-brush-python-bridge-implementation-checklist.md`

2. Failure contract normalization
- Structured exception mode now clears stale `PYTHON_EXCEPTION*` values before each `-x` run.
- Added conformance case proving reset behavior:
  - `tests/bridge/run.sh` -> `py_structured_exception_reset_on_success`

3. Hardening regressions
- Enforced deferred-type policy in runtime:
  - `sh.vars` list/tuple assignment now raises `TypeError` in ash mode.
  - `sh.vars` dict assignment now raises `TypeError` in ash mode.
  - `sh.tie(..., type="array"|"assoc")` now raises `ValueError` in ash mode.
- Added regressions:
  - `py_sh_vars_list_rejected_in_ash_mode`
  - `py_sh_vars_dict_rejected_in_ash_mode`
  - `py_tie_array_rejected_in_ash_mode`
  - `py_tie_assoc_rejected_in_ash_mode`

4. Stress reliability pass
- Added strict bridge stress runner:
  - `tests/stress/bridge.sh`
  - `make stress-bridge`
- Testing policy updated to include bridge stress semantics.

## Evidence

Executed locally:

- `tests/bridge/run.sh` -> pass
- `tests/regressions/run.sh` -> pass
- `BRIDGE_STRESS_REPEATS=20 tests/stress/bridge.sh` -> `checks=60 pass=60 fail=0`

## Remaining Work for Week 2

- Improve `python:` diagnostics when callable resolution and fallback execution fail.
- Improve scalar coercion diagnostics for callable invocation failures.
- Add docs/examples for current ash-mode bridge behavior.
- Add UX-focused regression rows and finalize week-2 report.
