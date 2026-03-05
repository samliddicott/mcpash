# Plan 007: POSIX Interactive and Job-Control Closure

Date: 2026-03-05

Goal:

- Bring the previously POSIX-lane out-of-scope interactive/job-control rows into scope.
- Close all 14 rows with strict comparator evidence and no out-of-scope carve-out.

Rows in scope:

- `C7.INT.01` prompt escapes in `PS1/PS2/PS4`
- `C7.INT.02` `PROMPT_COMMAND` timing
- `C7.INT.03` readline emacs/vi modes
- `C7.INT.04` `bind` keymap/query/assignment
- `C7.INT.05` history list/edit/delete/write/read
- `C7.INT.06` history expansion `!` forms
- `C7.INT.07` `fc` editor/list/re-exec
- `C7.INT.08` programmable completion
- `C7.INT.09` completion variables (`COMP_*`, `COMPREPLY`)
- `C7.INT.10` `interactive_comments`
- `C8.JOB.03` `fg` jobspec resume foreground
- `C8.JOB.07` signal delivery to foreground jobs
- `C8.JOB.11` `set -m` monitor mode behavior
- `C8.JOB.12` notification mode `set -b` / `notify`

## Execution Strategy

1. Baseline and comparator framing

- Comparator: `bash --posix` as primary for this lane.
- Harness: PTY-based tests only for interactive rows.
- Acceptance: semantic parity (status + observable markers), not byte-identical prompts.

2. Interactive UX tranche (`C7.INT.01`..`C7.INT.03`, `C7.INT.10`)

- Extend `tests/compat/run_interactive_ux_matrix.sh` with strict marker assertions for:
  - prompt escape expansion snapshots
  - `PROMPT_COMMAND` ordering before primary prompt
  - mode toggles relevant to emacs/vi behavior surface
  - interactive comments enable/disable semantics
- Add dedicated row-level case files where matrix granularity is too coarse.

3. Readline/completion tranche (`C7.INT.04`, `C7.INT.08`, `C7.INT.09`)

- Extend `tests/compat/run_completion_interactive_matrix.sh` with:
  - `bind` query/assignment surfaces with deterministic keymap probes
  - `complete`/`compgen`/`compopt` status and effect probes
  - `COMP_*` and `COMPREPLY` population behavior in controlled completion functions

4. History/fc tranche (`C7.INT.05`..`C7.INT.07`)

- Extend existing history/fc cases with strict deterministic flows:
  - history I/O roundtrip and deletion semantics
  - history expansion forms in interactive context
  - `fc` list/range/edit/re-exec paths using deterministic editor command
- Keep explicit comparator policy note where ash lacks `fc`; bash comparator is authoritative here.

5. Job control tranche (`C8.JOB.03`, `C8.JOB.07`, `C8.JOB.11`, `C8.JOB.12`)

- Extend `tests/compat/run_jobs_interactive_matrix.sh` and trap/job cross-cases to assert:
  - `%jobspec` foreground resume behavior (`fg`)
  - signal forwarding to foreground jobs
  - monitor mode toggling and effects
  - notification mode behavior under controlled background jobs

6. Matrix closure and gates

- For each row:
  - attach or narrow row-level test IDs in `docs/specs/bash-man-implementation-matrix.tsv`
  - flip `mctash_posix` from `partial` to `covered` only after strict pass
- Required gate for closure:
  - `STRICT=1 make completion-interactive-matrix`
  - `STRICT=1 make interactive-ux-matrix`
  - `STRICT=1 make jobs-interactive-matrix`
  - `STRICT=1 make trap-interactive-matrix`
  - `make bash-posix-man-matrix`
  - `make category-buckets-matrix`

## Risks and Controls

- PTY flakiness:
  - use stable marker-based assertions and time-bounded waits
  - fail closed (no statistical pass criteria)
- Environment sensitivity:
  - pin locale/env in harness where behavior depends on terminal/readline state
- Race behavior in job-control:
  - deterministic process setup and explicit synchronization markers

## Definition of Done

- All 14 rows set to `covered` in both lanes.
- No `out_of_scope` interactive/job-control rows remain in POSIX lane.
- Strict interactive/job-control gates pass at HEAD.
- Reports regenerated:
  - `docs/specs/bash-man-implementation-matrix.md`
  - `docs/reports/bash-posix-partials-latest.md`
  - `docs/reports/bash-compliance-remaining-work-latest.md`
