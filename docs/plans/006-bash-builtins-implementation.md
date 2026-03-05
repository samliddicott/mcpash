# 006 - Bash Builtins Implementation Plan

Date: 2026-03-04

## Goal

Implement missing Bash builtin surface in controlled tranches, with explicit comparator lanes and parity evidence.

## Comparator Policy

- Primary comparator for Bash-extension builtins: `bash` (default mode).
- POSIX compliance checks: `bash --posix` for behaviors that remain in-scope under POSIX mode.
- For interactive-only builtins (`bind`, `complete`, `compgen`, `compopt`), use PTY harnesses and keep non-interactive lanes clean.

## Tranches

1. `declare` / `typeset` / `local`
- Extend option and alias parity (`typeset` as `declare` alias, function-local behavior).
- Preserve current `BASH_COMPAT` gate for array/assoc in mctash policy.
- Add differential cases for aliasing, local scoping, and option behavior.

2. `mapfile` / `readarray`
- Implement non-interactive core flags first (`-t`, `-n`, `-s`, `-O`, `-u`, `-d`).
- Validate array population semantics and status behavior.

3. `enable`
- Implement builtin enable/disable registry (`-n`, `-a`, `-p`, names).
- Wire dispatch path so disabled builtins resolve like bash (external lookup path).
- Add differential status tests for disable/reenable cycles.

4. `help`
- Implement minimal command-oriented help surface and unknown-command failure semantics.
- Keep output text stable enough for tests by asserting status + key line presence.

5. `dirs` / `pushd` / `popd`
- Implement directory-stack behavior and key listing options.

6. `disown`
- Implement non-interactive-safe behavior over internal job table.

7. `bind` / `complete` / `compgen` / `compopt`
- Stage interactive/completion subsystem parity (PTY and readline/completion lanes).

## Acceptance Criteria Per Builtin

- Command is recognized and dispatched.
- Core advertised options/arguments in scope behave with correct status.
- Differential tests exist under `tests/diff/cases/` and pass.
- Matrix docs updated with `covered` or scoped `partial` status.

## Immediate Execution Order

Proceed now through tranches 1-4, commit after each tranche, and report before 5-7.
