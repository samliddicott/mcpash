# Bash Compliance Gap Report

Generated: 2026-03-11

This report tracks observed gaps from runnable evidence.

## Explicit Known Gaps

None at current HEAD.

## Known Unknowns (Compliance-Risk Tracking)

None at current HEAD.

## Basis

- `tests/compat/run_bash_invocation_option_matrix.sh` is green.
- `tests/compat/run_bash_posix_man_matrix.sh` is green.
- `tests/compat/run_bash_posix_upstream_matrix.sh` reports `core full parity: 9/9`.
- `STRICT=1 tests/compat/run_bash_builtin_matrix.sh` is green.
- `tests/diff/run_parity_matrix.sh` reports ash lane mismatch `0` and bash lane mismatches `0`.
