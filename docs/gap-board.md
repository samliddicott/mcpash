# Gap Board

Date: 2026-02-27

Purpose:

- Track parity progress with a compact status board.
- Tie each status to executable evidence in `tests/diff/cases` and POSIX trace docs.

Status legend:

- `covered`: differential case exists and currently passes (`ash` vs `mctash`).
- `partial`: case exists, but does not yet exercise full option/error matrix.
- `untested`: no dedicated differential case yet.

## Ash Man Builtins (Current Corpus)

| Command/Area | Status | Evidence | Notes |
|---|---|---|---|
| `set` | covered | `tests/diff/cases/man-ash-set.sh`, `tests/diff/cases/set-listing.sh` | Covers option toggles, positional reset, and listing behavior.
| `test` / `[` | covered | `tests/diff/cases/man-ash-test.sh` | Unary/file/numeric/string/logical combinations.
| `getopts` | covered | `tests/diff/cases/man-ash-getopts.sh` | Basic iteration + missing-arg behavior.
| redirection surface | covered | `tests/diff/cases/man-ash-redir.sh` | `>`, `>>`, heredoc, fd duplication smoke paths.
| `export` / `unset` / `readonly` | covered | `tests/diff/cases/man-ash-env.sh` | Readonly-protection path validated.
| `read` | covered | `tests/diff/cases/man-ash-read.sh` | Ash-supported options only; advanced variants are separate gap.
| `trap` | covered | `tests/diff/cases/man-ash-trap.sh` | EXIT/INT/HUP signal paths.
| `kill` / `wait` | covered | `tests/diff/cases/man-ash-kill-wait.sh` | Includes `kill -0` probe behavior.
| `hash` / `times` / `ulimit` / `umask` | covered | `tests/diff/cases/man-ash-resource.sh` | Normalized to deterministic status checks.
| `jobs` / `fg` / `bg` | covered | `tests/diff/cases/man-ash-jobs.sh` | Non-interactive job-control semantics.
| `alias` / `unalias` / `command` / `builtin` | covered | `tests/diff/cases/man-ash-alias.sh` | Alias lookup and post-unalias behavior.
| `cd` / `.` (`source`) | covered | `tests/diff/cases/man-ash-cd-source.sh` | Directory changes and script sourcing.
| `eval` / `exec` | covered | `tests/diff/cases/man-ash-eval-exec.sh` | Replacement/termination path is exercised.
| `printf` / `echo` | covered | `tests/diff/cases/man-ash-printf-echo.sh` | Escape behavior aligned for tested patterns.
| `shift` | covered | `tests/diff/cases/man-ash-shift.sh` | Default, multi-shift, and over-shift tolerance path.
| `type` | covered | `tests/diff/cases/man-ash-type.sh` | Function/builtin/missing command behavior.
| `pwd` | covered | `tests/diff/cases/man-ash-pwd.sh` | PWD consistency under `cd`.
| `fc` | covered | `tests/diff/cases/man-ash-fc.sh` | Uses availability-safe branch for ash variants.
| `:` / `true` / `false` / `break` / `continue` / `return` / `exit` | covered | `tests/diff/cases/man-ash-logic.sh` | Control-flow and status semantics.

## Remaining Builtin Gaps (Depth)

| Area | Status | What is missing |
|---|---|---|
| `read` advanced option matrix | partial | No dedicated differential coverage for full `-d`/`-n`/timeout variants across ash variants.
| `type` option matrix | partial | `-t`/`-a` not covered in canonical differential case due ash-variant incompatibilities.
| `fc` editor/history parity | partial | No external-editor invocation path and minimal history-edit scenarios only.
| `ulimit` full flag set | partial | Case currently checks baseline behavior, not full per-resource option table.
| `trap` signal matrix | partial | Core paths covered; full signal-by-signal and nested trap interactions untested.
| `jobs` interactive monitor semantics | partial | Non-interactive semantics covered; interactive job control remains limited.

## POSIX Chapter 2 Areas

Reference summary source: `docs/posix-shall-trace.md`.

| POSIX Area | Status | Evidence |
|---|---|---|
| 2.6 Word Expansions | partial | `docs/posix-shall-trace.md` + BusyBox/Oil corpus references.
| 2.7 Redirection | covered | `docs/posix-shall-trace.md` + `tests/diff/cases/man-ash-redir.sh`.
| 2.8 Exit Status and Errors | covered | `docs/posix-shall-trace.md` + differential command-status cases.
| 2.9 Shell Commands | partial | Differential builtin cases + BusyBox/Oil references, but not full production-by-production closure.
| 2.10 Shell Grammar | partial | Parser acceptance/rejection covered in corpora; still tracking deeper production checklist.
| 2.11 Signals/Traps | partial | `man-ash-trap` plus signal corpus; full matrix still open.

## Untested/Backlog Buckets

| Bucket | Status | Next concrete step |
|---|---|---|
| Requirement-level trace completeness (all "shall" rows) | untested | Expand `docs/posix-shall-trace.md` to include explicit case-id links for every row.
| Grammar production closure | untested | Fill `docs/grammar-production-checklist.md` with parser production-to-test mapping.
| Threaded-runtime parity checks | untested | Add dedicated differential cases for thread-specific cwd/fd behavior from `docs/threaded-runtime-deviations.md`.

