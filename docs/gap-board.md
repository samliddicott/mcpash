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
| `read` | covered | `tests/diff/cases/man-ash-read.sh`, `tests/diff/cases/man-ash-read-options.sh` | IFS/raw/cooked/arg-count and option support matrix for this ash target.
| `trap` | covered | `tests/diff/cases/man-ash-trap.sh`, `tests/diff/cases/man-ash-trap-matrix.sh`, `tests/diff/cases/man-ash-trap-signals.sh` | EXIT/HUP plus list/clear, numeric-signal, and common signal-name matrix paths.
| `kill` / `wait` | covered | `tests/diff/cases/man-ash-kill-wait.sh` | Includes `kill -0` probe behavior.
| `hash` / `times` / `ulimit` / `umask` | covered | `tests/diff/cases/man-ash-resource.sh`, `tests/diff/cases/man-ash-ulimit-flags.sh`, `tests/diff/cases/man-ash-ulimit-set.sh` | Includes hash miss, umask roundtrip, expanded ulimit query matrix, and set-with-current-value paths.
| `jobs` / `fg` / `bg` | covered | `tests/diff/cases/man-ash-jobs.sh`, `tests/diff/cases/man-ash-set-monitor.sh` | Includes `jobs -p` and explicit non-interactive monitor-mode behavior.
| `alias` / `unalias` / `command` / `builtin` | covered | `tests/diff/cases/man-ash-alias.sh` | Alias lookup and post-unalias behavior.
| `cd` / `.` (`source`) | covered | `tests/diff/cases/man-ash-cd-source.sh` | Directory changes and script sourcing.
| `eval` / `exec` | covered | `tests/diff/cases/man-ash-eval-exec.sh` | Replacement/termination path is exercised.
| `printf` / `echo` | covered | `tests/diff/cases/man-ash-printf-echo.sh` | Escape behavior aligned for tested patterns.
| `shift` | covered | `tests/diff/cases/man-ash-shift.sh` | Default, multi-shift, and over-shift tolerance path.
| `type` | covered | `tests/diff/cases/man-ash-type.sh`, `tests/diff/cases/man-ash-type-options.sh` | Function/alias/builtin/external reporting plus `-t/-a` status behavior for this ash target.
| `pwd` | covered | `tests/diff/cases/man-ash-pwd.sh` | PWD consistency under `cd`.
| `fc` | covered | `tests/diff/cases/man-ash-fc.sh` | Includes reverse listing and invalid-reference status checks.
| `:` / `true` / `false` / `break` / `continue` / `return` / `exit` | covered | `tests/diff/cases/man-ash-logic.sh` | Control-flow and status semantics.

## Remaining Builtin Gaps (Depth)

| Area | Status | What is missing |
|---|---|---|
| `read` option matrix across ash variants | partial | Covered for current ash target via `man-ash-read-options.sh`; cross-variant matrix remains open.
| `fc` editor/history parity | partial | External-editor workflow (`fc -e`) and richer history-edit flows remain untested.
| `ulimit` full flag set | partial | Query and safe set paths are covered (`-S/-H`, `-f/-n/-c/-v`), but full per-resource set/error matrix remains open.
| `trap` signal matrix | partial | Common signal-name coverage added; full signal-by-signal and nested-trap interaction matrix remains open.
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
