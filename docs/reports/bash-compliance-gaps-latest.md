# Bash Compliance Gap Report

Generated: 2026-03-06

This report tracks observed gaps from runnable evidence.

## Explicit Known Gaps

None at current HEAD.

## Known Unknowns (Compliance-Risk Tracking)

None currently open in this board.

## Basis

- `tests/compat/run_bash_invocation_option_matrix.sh` is green.
- `tests/compat/run_bash_posix_man_matrix.sh` is green.
- `tests/compat/run_bash_posix_upstream_matrix.sh` reports `core full parity: 9/9`.
- `STRICT=1 tests/compat/run_bash_builtin_matrix.sh` is green.
