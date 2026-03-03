# Gap Board

Date: 2026-03-03

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
| `trap` | covered | `tests/diff/cases/man-ash-trap.sh`, `tests/diff/cases/man-ash-trap-matrix.sh`, `tests/diff/cases/man-ash-trap-signals.sh`, `tests/diff/cases/man-ash-trap-full.sh`, `tests/diff/cases/man-ash-trap-nested.sh` | EXIT/HUP/INT/TERM behavior plus list/clear, numeric-signal, common signal-name, and nested trap interaction paths.
| `kill` / `wait` | covered | `tests/diff/cases/man-ash-kill-wait.sh` | Includes `kill -0` probe behavior.
| `hash` / `times` / `ulimit` / `umask` | covered | `tests/diff/cases/man-ash-resource.sh`, `tests/diff/cases/man-ash-ulimit-flags.sh`, `tests/diff/cases/man-ash-ulimit-set.sh`, `tests/diff/cases/man-ash-ulimit-errors.sh`, `tests/diff/cases/man-ash-ulimit-soft-hard.sh` | Includes hash miss, umask roundtrip, expanded ulimit query matrix, set-with-current-value paths, soft/hard interaction checks, and error-status matrix.
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
| `ulimit` full flag set | partial | Query/set/error paths are covered for `-f/-n/-c/-v`, but full per-resource set/error matrix across all limits remains open.
| `trap` signal matrix | partial | Common signal-name and action-execution coverage added; full signal-by-signal and nested-trap interaction matrix remains open.
| `fc` comparator availability | partial | Current ash target reports `fc` unavailable, so differential parity for `fc -e` semantics is blocked on comparator support (`docs/fc-comparator-blocker.md`).
| `jobs` interactive monitor semantics | partial | Non-interactive semantics covered; interactive job control remains limited.

## POSIX Chapter 2 Areas

Reference summary source: `docs/posix-shall-trace.md`.

| POSIX Area | Status | Evidence |
|---|---|---|
| 2.6 Word Expansions | partial | `docs/posix-shall-trace.md` + BusyBox/Oil corpus references.
| 2.7 Redirection | covered | `docs/posix-shall-trace.md` + `tests/diff/cases/man-ash-redir.sh`.
| 2.8 Exit Status and Errors | covered | `docs/posix-shall-trace.md` + differential command-status cases.
| 2.9 Shell Commands | partial | Differential builtin cases + BusyBox/Oil references, but not full production-by-production closure.
| 2.10 Shell Grammar | partial | `docs/posix-shall-trace.md`, `docs/grammar-production-checklist.md`, `tests/diff/cases/man-ash-prefix-suffix.sh`, `tests/diff/cases/man-ash-grammar-negative.sh`, `tests/diff/cases/man-ash-grammar-reserved.sh`.
| 2.11 Signals/Traps | partial | `man-ash-trap` plus signal corpus; full matrix still open.

## Bash-Compat Lane (Differential vs bash baseline)

| Area | Status | Evidence | Notes |
|---|---|---|---|
| Indexed-vs-assoc subscript evaluation mode | covered | `tests/diff/cases/bash-compat-subscript-eval-indexed.sh`, `tests/diff/cases/bash-compat-subscript-eval-indexed-extended.sh`, `tests/diff/cases/bash-compat-subscript-eval-indexed-sideeffects.sh`, `tests/diff/cases/bash-compat-subscript-eval-indexed-assign.sh`, `tests/diff/cases/bash-compat-subscript-eval-indexed-unset.sh`, `tests/diff/cases/bash-compat-subscript-eval-assoc.sh`, `tests/diff/cases/bash-compat-subscript-eval-assoc-quoted.sh` | Indexed paths use arithmetic evaluation in read/assign/unset flows; assoc paths use string-key semantics. |
| Array/hash operator expansion contexts (`[@]`/`[*]`, quoted/unquoted) | covered | `tests/diff/cases/bash-compat-param-array-contexts.sh`, `tests/diff/cases/bash-compat-param-array-hash-ops.sh`, `tests/diff/cases/bash-compat-param-array-hash-extended.sh`, `tests/diff/cases/bash-compat-param-contexts.sh`, `tests/diff/cases/bash-compat-param-collection-slicing.sh` | Replacement/trim/substr and field-boundary behavior are covered in bash lane. |

## Untested/Backlog Buckets

| Bucket | Status | Next concrete step |
|---|---|---|
| Requirement-level trace completeness (all "shall" rows) | partial | Continue adding explicit case-id links for every remaining row in `docs/posix-shall-trace.md`.
| Grammar production closure | partial | Closure-order artifacts are completed; remaining work is deeper word-level/operator combinatorics and diagnostic text parity.
| Threaded-runtime parity checks | partial | Core cwd/fd/var isolation cases are covered (`man-ash-thread-cwd.sh`, `man-ash-thread-fd.sh`, `man-ash-thread-vars.sh`, `man-ash-thread-pipeline-cwd.sh`, `man-ash-thread-pipeline-fd.sh`) plus fallback-diag/process-subst regressions (`thread_unshare_fallback_diag`, `thread_unshare_forced_fail_diag`, `process_subst_*`, `thread_combined_bg_pipeline_process_subst`, `thread_multi_job_concurrency_isolation`, `thread_high_load_concurrency_isolation`, `monitor_mode_noninteractive_diag` in `tests/regressions/run.sh`); expand to long-running mixed workloads and interactive monitor semantics.

## Sentinel-To-Structured Expansion Transition

| Area | Status | Evidence | Next step |
|---|---|---|---|
| Expansion engine migration plan exists | covered | `docs/plan.md` ("Expansion Engine Transition: Sentinels -> Structured Data") | Track execution progress here as items move from design to implementation. |
| Sentinel usage inventory and guard | covered | `tests/regressions/asdl_fallback_audit.sh`, `tests/regressions/asdl_fallback_allowlist.txt`, `tests/regressions/sentinel_transport_audit.sh` | Keep deny-surface current as structured coverage expands. |
| Typed expansion model introduction | partial | `src/mctash/expansion_model.py`, `src/mctash/runtime.py` (`_asdl_word_to_expansion_fields`) | Extend segment metadata usage beyond adapter-only scope and cover unquoted split/glob path end-to-end. |
| Typed adapters (ASDL and legacy parser) | partial | `src/mctash/runtime.py` (`_asdl_word_to_expansion_fields`, `_legacy_word_to_expansion_fields`), `tests/regressions/run.sh` (`legacy_expansion_adapter_equiv`) | Promote adapter use from equivalence-only to primary execution paths. |
| Split/glob/pattern stages on structured fields | partial | `src/mctash/runtime.py` (`_split_structured_field`, `_glob_structured_field`, `_asdl_case_pattern_from_word`) | Complete migration for remaining legacy text-expansion paths and operator-arg pipelines. |
| Sentinel collision proof cases | partial | `tests/diff/experimental/unicode-pua-literals.sh`, `tests/diff/experimental/unicode-pua-operators.sh`, `tests/diff/experimental/unicode-pua-case-assignment.sh` | Resolve current mctash-vs-bash deltas for these cases, then graduate them into `tests/diff/cases` parity gate. |
