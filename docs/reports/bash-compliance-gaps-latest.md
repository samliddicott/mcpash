# Bash Compliance Gap Report

Generated: 2026-03-06

This report tracks observed gaps from runnable evidence.

## Explicit Known Gaps

1. `${v@op}` parameter transformation operators (`C3.EXP.016`) are partial.
   - Evidence: `tests/diff/cases/bash-man-param-transform-ops.sh`, `tests/diff/cases/bash-man-param-transform-ops-variants.sh`, `tests/diff/cases/bash-man-param-transform-prompt.sh`
   - Note: core scalar/positional/array/prompt lanes now run; deeper `${v@P}` edge semantics remain open (notably `\\w`/tilde behavior).
2. `TIMEFORMAT` semantics (`C6.VAR.BASH.TIMEFORMAT`) are partial.
   - Evidence: `tests/diff/cases/bash-man-timeformat.sh`
3. `BASH_XTRACEFD` behavior (`C6.VAR.BASH.BASH_XTRACEFD`) is partial.
   - Evidence: `tests/diff/cases/bash-man-bash_xtracefd.sh`
4. `TMOUT` interactive behavior (`C6.VAR.BASH.TMOUT`) is partial.
   - Evidence: `tests/compat/run_interactive_tmout_matrix.sh`
5. `HISTTIMEFORMAT` behavior-depth (`C6.VAR.BASH.HISTTIMEFORMAT`) is partial.
   - Evidence: currently surface-only mapping.
6. Prompt escape depth (`C7.INT.01`) is partial.
   - Evidence: current interactive lane focuses on PS1; PS2/PS4 dedicated assertions still missing.
7. Interactive SIGINT foreground-command continuation (`C8.JOB.13`) is partial.
   - Evidence: `tests/compat/run_interactive_sigint_matrix.sh`

## Known Unknowns (Compliance-Risk Tracking)

None currently open in this board beyond explicit gap above.

## Basis

- `tests/compat/run_bash_invocation_option_matrix.sh` is green.
- `tests/compat/run_bash_posix_man_matrix.sh` is green.
- `tests/compat/run_bash_posix_upstream_matrix.sh` reports `core full parity: 9/9`.
- `STRICT=1 tests/compat/run_bash_builtin_matrix.sh` is green.
