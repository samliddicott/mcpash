# Bash Shell Variables Detail Audit

Date: 2026-03-06

Scope:

- `man bash` sections reviewed in detail:
  - `Shell Variables`
  - `PROMPTING`
  - `SIGNALS`

Objective:

- Move from variable-surface presence checks to behavior-level checks.
- Record missed detail and add requirement rows/tests for those details.

## What We Missed

1. `PS1` behavior is not only "variable exists"; prompt text is decoded and then expanded at render time.
   - Man-page detail: PROMPTING says prompt strings are decoded, then expanded (parameter/command/arithmetic), subject to `promptvars`.
   - Prior gap: matrix mostly treated `PS1` as surface-presence via `bash-man-variables-surface.sh`.
   - Action taken:
     - `src/mctash/main.py` prompt rendering now applies expansion in prompt path.
     - Added explicit requirement row `C7.INT.11`.
     - Added promptvars-focused checks to `tests/compat/run_interactive_ux_matrix.sh`.

2. Interactive `SIGINT` behavior for foreground external commands was under-specified in matrix evidence.
   - Man-page detail: SIGNALS says interactive `SIGINT` is caught/handled; behavior should not simply terminate the shell.
   - Prior gap: trap matrices existed, but no dedicated no-trap PTY `Ctrl-C` foreground-command continuation check.
   - Action taken:
     - Added requirement row `C8.JOB.13`.
     - Added `tests/compat/run_interactive_sigint_matrix.sh`.
     - Current status: row is `partial` (probe currently reveals parity gap).

## Added Matrix Rows

- `C7.INT.11` (interactive prompt-time expansion semantics): `covered`
- `C8.JOB.13` (interactive Ctrl-C foreground command continuity): `partial`

Files updated:

- `docs/specs/bash-man-requirements.tsv`
- `docs/specs/bash-man-implementation-matrix.tsv`

## Variable-Detail Audit Method (To Apply Across Entire Shell Variables List)

For each variable in `Shell Variables`, split validation into:

1. `surface`:
   - variable exists / is readable / assignable
2. `runtime behavior`:
   - side effects and timing semantics (e.g., prompt-time expansion, startup-time influence)
3. `mode interactions`:
   - default bash mode vs `--posix` behavior
4. `interactive dependencies`:
   - requires PTY/interactivity to validate correctly

This avoids marking a row `covered` from pure presence checks when behavior semantics are not tested.

## Why We Missed This Earlier

- We over-relied on "surface" probes (`set`, variable dumps, static checks) and bucket-level green gates.
- We did not consistently force requirement rows to include one behavior-level test for sections with dynamic semantics (`PROMPTING`, `SIGNALS`, interactive paths).
- We accepted matrix closure claims before adding detail-level, section-specific audits for man-page text that includes "is expanded", "is handled", and similar normative behavior words.

## Reread Process Upgrade (For Entire Man Page)

When re-reading each section, extract and classify statements by verbs:

- `is expanded` / `is substituted` / `is subject to` -> runtime semantic row + dedicated behavior test.
- `is ignored` / `is caught and handled` -> signal/state row + PTY/non-PTY test.
- `is displayed` / `is printed` -> formatting/output row + comparator-sensitive tests.

Then enforce:

- No row may be marked `covered` without at least one behavior-evidence case id.
- Interactive claims require PTY evidence, not pipe-based pseudo-interactive runs.
