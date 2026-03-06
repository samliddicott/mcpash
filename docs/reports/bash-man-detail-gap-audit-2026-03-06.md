# Bash Man-Page Detail Gap Audit

Date: 2026-03-06

Scope:

- `man bash` sections:
  - `Shell Variables`
  - `PROMPTING`
  - `SIGNALS`

Method:

- Applied Plan 009 sentence-to-requirement decomposition and behavior-evidence rule.

## New Gaps Surfaced

1. `C3.EXP.016` `${v@op}` transformation operators: `partial`
   - Evidence: `tests/diff/cases/bash-man-param-transform-ops.sh`
   - Differential result: mismatch
   - Observed: mctash reports bad substitution for `${x@Q,P,A,a,E,U,u,L}`.
   - Scope note: this row also includes positional/array forms (`$@`/`$*`, `${arr[@]@op}`, `${arr[*]@op}`), which remain open.

2. `C6.VAR.BASH.TIMEFORMAT`: `partial` (new row)
   - Evidence: `tests/diff/cases/bash-man-timeformat.sh`
   - Differential result: mismatch
   - Observed: `%P` and related format behavior diverges; mctash output is incomplete compared with bash.

3. `C6.VAR.BASH.BASH_XTRACEFD`: `partial`
   - Evidence: `tests/diff/cases/bash-man-bash_xtracefd.sh`
   - Differential result: mismatch
   - Observed: bash routes xtrace to configured FD; mctash still emits trace on stderr and does not mirror file-FD routing behavior.

4. `C6.VAR.BASH.TMOUT`: `partial`
   - Evidence: `tests/compat/run_interactive_tmout_matrix.sh`
   - Differential result: fail
   - Observed: bash auto-logs out interactive shell at timeout; mctash does not auto-logout (probe hits timeout kill).

5. `C6.VAR.BASH.HISTTIMEFORMAT`: `partial`
   - Evidence status: surface-only (`bash-man-variables-surface.sh`)
   - Gap reason: no dedicated behavior test for history timestamp formatting semantics.

6. `C7.INT.01` prompt escapes (`PS1/PS2/PS4`): `partial`
   - Evidence: `tests/compat/run_interactive_ux_matrix.sh`
   - Gap reason: current test depth strongly covers PS1; dedicated PS2 and PS4 escape behavior assertions are still missing.

7. `C8.JOB.13` interactive foreground Ctrl-C continuation: `partial`
   - Evidence: `tests/compat/run_interactive_sigint_matrix.sh`
   - Differential result: fail
   - Observed: mctash diverges from bash continuation behavior after Ctrl-C during foreground external command.

## Net Effect

- Partial rows in implementation matrix increased to 7.
- This is expected under corrected process: previously hidden detail gaps are now explicit and test-backed.

## Commands Run

- `bash tests/diff/run.sh --case bash-man-param-transform-ops --case bash-man-timeformat --case bash-man-bash_xtracefd`
- `./tests/compat/run_interactive_tmout_matrix.sh`
- `./tests/compat/run_interactive_sigint_matrix.sh`
