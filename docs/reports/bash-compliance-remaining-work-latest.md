# Bash Compliance Remaining Work List

Generated: 2026-03-06

Evidence sources:

- `tests/compat/run_bash_invocation_option_matrix.sh`
- `tests/compat/run_bash_posix_man_matrix.sh`
- `tests/compat/run_bash_posix_upstream_matrix.sh`
- `STRICT=1 tests/compat/run_bash_builtin_matrix.sh`

## Summary

Total remaining items: 7

- Known behavior mismatches: 6
- Known-unknown/completeness risks tracked in this board: 0

## Remaining Items

1. `${v@op}` parameter transformation operator parity.
   - Requirement row: `C3.EXP.016`
   - Evidence: `tests/diff/cases/bash-man-param-transform-ops.sh`
   - Current status: `partial`.
2. `TIMEFORMAT` variable semantics parity.
   - Requirement row: `C6.VAR.BASH.TIMEFORMAT`
   - Evidence: `tests/diff/cases/bash-man-timeformat.sh`
   - Current status: `partial`.
3. `BASH_XTRACEFD` xtrace routing parity.
   - Requirement row: `C6.VAR.BASH.BASH_XTRACEFD`
   - Evidence: `tests/diff/cases/bash-man-bash_xtracefd.sh`
   - Current status: `partial`.
4. Interactive `TMOUT` auto-logout parity.
   - Requirement row: `C6.VAR.BASH.TMOUT`
   - Evidence: `tests/compat/run_interactive_tmout_matrix.sh`
   - Current status: `partial`.
5. `HISTTIMEFORMAT` behavior-depth coverage.
   - Requirement row: `C6.VAR.BASH.HISTTIMEFORMAT`
   - Evidence: surface-only at present.
   - Current status: `partial` until dedicated behavior case is added.
6. Prompt escape depth coverage (`PS2`/`PS4` lanes).
   - Requirement row: `C7.INT.01`
   - Evidence: `tests/compat/run_interactive_ux_matrix.sh`
   - Current status: `partial`.
7. Interactive SIGINT continuation parity:
   - Requirement row: `C8.JOB.13`
   - Evidence: `tests/compat/run_interactive_sigint_matrix.sh`
   - Current status: `partial` (mctash does not yet match bash for Ctrl-C interruption of a foreground external command in PTY probe).

## Notes

- Compliance status should continue to be asserted from executable gates, not static matrix labels alone.
