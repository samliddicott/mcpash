# Milestone-2 Week-2 UX Report

Date: 2026-03-02
Plan reference: `docs/plans/003-milestone-2-bridge-hardening-and-ux.md`

## Completed Steps

1. `python:` diagnostic UX
- `python:` now emits entry-specific usage/error prefixes.
- Added explicit fallback failure diagnostic when callable resolution fails and statement fallback also fails.
- Added bridge conformance case:
  - `python_colon_non_callable_fallback_exec_error_diag`

2. Scalar coercion messaging
- Callable invocation now reports both coercion-path and raw-string-path `TypeError` details when both fail.
- Added bridge conformance case:
  - `py_callable_coercion_diag_on_total_typeerror`

3. Docs and examples
- Added usage-focused bridge examples for ash mode:
  - `docs/bridge-examples-ash-mode.md`
- Added `make stress-bridge` to README and linked bridge examples.

4. UX regression rows
- Added regression guardrails for:
  - `python:` fallback diagnostics
  - coercion/fallback TypeError diagnostics
  - structured exception reset behavior

## Evidence

Executed locally:

- `tests/bridge/run.sh` -> pass
- `tests/regressions/run.sh` -> pass
- `BRIDGE_STRESS_REPEATS=20 tests/stress/bridge.sh` -> `checks=60 pass=60 fail=0`
- `make conformance-quick` ->
  - regressions: pass
  - Oil subset (`shell-grammar`, `command-parsing`): `pass=43 fail=0`

## Residual Gaps (Post Week-2)

- Full Bash-compat typed collections remain deferred:
  - shell arrays/assoc runtime model
  - bridge list/dict mapping and tie `array`/`assoc` semantics behind explicit extension gate
- Interactive/job-control parity remains separate from this bridge-focused milestone.
