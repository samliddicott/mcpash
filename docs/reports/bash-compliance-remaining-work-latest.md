# Bash Compliance Remaining Work List

Generated: 2026-03-06

Evidence sources:

- `tests/compat/run_bash_invocation_option_matrix.sh`
- `tests/compat/run_bash_posix_man_matrix.sh`
- `tests/compat/run_bash_posix_upstream_matrix.sh`
- `STRICT=1 tests/compat/run_bash_builtin_matrix.sh`

## Summary

Total remaining items: 1

- Known behavior mismatches: 1
- Known-unknown/completeness risks tracked in this board: 0

## Remaining Items

1. Interactive SIGINT continuation parity:
   - Requirement row: `C8.JOB.13`
   - Evidence: `tests/compat/run_interactive_sigint_matrix.sh`
   - Current status: `partial` (mctash does not yet match bash for Ctrl-C interruption of a foreground external command in PTY probe).

## Notes

- Compliance status should continue to be asserted from executable gates, not static matrix labels alone.
