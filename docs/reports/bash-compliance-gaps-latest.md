# Bash Compliance Gap Report

Generated: 2026-03-10

This report tracks observed gaps from runnable evidence.

## Explicit Known Gaps

- `diff-parity-matrix` (bash lane) currently reports 8 mismatches:
  - `bash-compat-param-array-hash-extended` (stdout/stderr)
  - `bash-compat-param-array-hash-ops` (stdout/stderr)
  - `bash-compat-param-contexts` (stdout/stderr)
  - `bash-compat-subscript-eval-assoc-quoted` (stdout/stderr)
- `bash-posix-upstream-matrix` currently reports 3 core-row mismatches:
  - `posixexp.tests` (stdout mismatch)
  - `set-e.tests` (stderr mismatch)
  - `builtins.tests` (stdout mismatch)

## Known Unknowns (Compliance-Risk Tracking)

No known-unknown risk items are currently tracked.

## Basis

- `tests/compat/run_bash_invocation_option_matrix.sh` is green.
- `tests/compat/run_bash_posix_man_matrix.sh` is green.
- `tests/compat/run_bash_posix_upstream_matrix.sh` reports `core full parity: 6/9`.
- `STRICT=1 tests/compat/run_bash_builtin_matrix.sh` is green.
- `tests/diff/run_parity_matrix.sh` reports ash lane mismatch `1` and bash lane mismatches `8`.
