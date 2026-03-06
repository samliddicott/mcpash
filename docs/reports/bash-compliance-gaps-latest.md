# Bash Compliance Gap Report

Generated: 2026-03-06

This report tracks observed gaps from runnable evidence.

## Explicit Known Gaps

1. Interactive SIGINT foreground-command continuation (`C8.JOB.13`) is partial.
   - Evidence: `tests/compat/run_interactive_sigint_matrix.sh`
   - Observed behavior: PTY Ctrl-C probe currently shows mctash foreground external command interruptibility diverging from bash.

## Known Unknowns (Compliance-Risk Tracking)

None currently open in this board beyond explicit gap above.

## Basis

- `tests/compat/run_bash_invocation_option_matrix.sh` is green.
- `tests/compat/run_bash_posix_man_matrix.sh` is green.
- `tests/compat/run_bash_posix_upstream_matrix.sh` reports `core full parity: 9/9`.
- `STRICT=1 tests/compat/run_bash_builtin_matrix.sh` is green.
