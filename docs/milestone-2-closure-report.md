# Milestone-2 Closure Report

Date: 2026-02-28

## Scope Closed

Milestone-2 is closed for ash-mode bridge scope with the following boundaries:

- Ash-mode remains scalar-first shell semantics.
- Shared variables are implemented for scalar values and cross-process visibility.
- Bash-compat-only extensions (typed shell arrays/hashes and related bridge semantics) are deferred.

## Validation Evidence

Executed in this repo:

- `make conformance-quick`
  - regressions: pass
  - Oil targeted subset (`shell-grammar`, `command-parsing`): `pass=43 fail=0`

- `make conformance-full`
  - BusyBox ash corpus: `ok=356 fail=1 skip=0` with allowlisted known fail identity (`ash-signals-sigquit_exec.tests.fail`), effective gate pass
  - Oil configured subset: `total=372 pass=245 fail=0 skip=127`
  - overall gate: pass

## Key Milestone-2 Deliverables

- `py` and `PYTHON ... END_PYTHON` bridge execution paths with structured exceptions.
- `python:` pseudo-function path:
  - resolves and invokes Python callables directly when callable,
  - falls back to Python statement execution when target is not callable (`import`, `from`, etc.).
- `sh` object mappings: `vars`, `env`, `fn`, `shared`, `stack`, and callback APIs (`sh()`, `run`, `popen`).
- `from ... import ...` bridge wrappers.
- tie support for ash-mode in-scope types (`scalar`, `integer`).
- shared backend with cross-process visibility.
- frame-based stack diagnostics with frame kinds and innermost-first ordering.
- conformance quick/full targets and module-scoped BusyBox timeout handling.
- machine-readable parity summary contract with schema validation:
  - `make parity-summary`
  - `make parity-summary-validate`
  - schema: `docs/reports/parity-summary.schema.json`

## Deferred to Bash-Compat Milestone

- First-class shell arrays/associative arrays semantics.
- tie semantics for `array` / `assoc`.
- typed shared flags (`-a`, `-A`, `-i`, `-d`) as normative behavior.

## Follow-on (Milestone-3 candidates)

1. Introduce explicit Bash-extension option gate (`set -o bash_ext` or equivalent).
2. Implement first-class array/hash runtime model behind that gate.
3. Upgrade bridge/tie semantics to typed array/hash behavior.
4. Tighten trap/source/subshell stack-frame completeness and optional frame IDs.

## Evidence Snapshot (Latest Local)

- `tests/bridge/run.sh`: pass (includes `python:` callable and fallback-exec coverage).
- `tests/regressions/run.sh`: pass.
- `PARITY_SKIP_BUSYBOX=1 make parity-summary-validate`: pass and schema-valid JSON emitted.
