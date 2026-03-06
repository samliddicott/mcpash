# Gap Board

Date: 2026-03-05

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
| `read` option matrix across ash variants | covered | Ash-family and bash comparator coverage is now centralized in `tests/diff/run_read_matrix.sh` (`make read-matrix`), including `man-ash-read-options.sh`, `man-ash-read-ifs-matrix.sh`, `man-ash-read-option-probe.sh`, and `bash-read-options-core.sh`. |
| `fc` editor/history parity | covered | `tests/diff/cases/man-ash-fc.sh`, `tests/diff/cases/man-ash-fc-editor-env.sh`, `tests/diff/cases/man-ash-fc-ranges.sh`, `tests/diff/cases/man-ash-fc-edit-reexec.sh` now cover list/reverse/range, editor precedence, and deterministic edit/re-exec (`sed -i`) flows.
| `ulimit` full flag set | covered | Query/set/error/listing coverage now includes `man-ash-ulimit-flags.sh`, `man-ash-ulimit-set.sh`, `man-ash-ulimit-errors.sh`, `man-ash-ulimit-soft-hard.sh`, and `man-ash-ulimit-all.sh` for this ash comparator surface. |
| `trap` signal matrix | covered | Delivery/matrix coverage includes `man-ash-trap-delivery.sh`, `man-ash-trap-signal-matrix.sh`, plus strict compatibility gates (`STRICT=1 make trap-noninteractive-matrix`, `STRICT=1 make trap-interactive-matrix`) and variant reporting (`make trap-variant-matrix`). Coverage is scoped to declared Linux comparator/signal set. |
| `fc` comparator availability | covered | Policy accepted: when comparator ash lacks `fc`, differential parity uses temporary bash comparator (`man-ash-fc*.sh`) as documented in `docs/fc-comparator-blocker.md`. |
| `jobs` interactive monitor semantics | covered | Non-interactive semantics plus PTY interactive matrix now have a strict gate (`STRICT=1 make jobs-interactive-matrix`) for declared Linux comparator scope. |

## POSIX Chapter 2 Areas

Reference summary source: `docs/posix-shall-trace.md`.

| POSIX Area | Status | Evidence |
|---|---|---|
| 2.6 Word Expansions | covered | `docs/posix-shall-trace.md` + differential expansion matrices (`man-ash-var-ops*.sh`, `man-ash-word-nesting*.sh`, `man-ash-glob-matrix.sh`, `man-ash-glob-full-matrix.sh`).
| 2.7 Redirection | covered | `docs/posix-shall-trace.md` + `tests/diff/cases/man-ash-redir.sh`, `tests/diff/cases/man-ash-heredoc-edges.sh`, `tests/diff/cases/man-ash-redir-heredoc-matrix.sh`.
| 2.8 Exit Status and Errors | covered | `docs/posix-shall-trace.md` + differential command-status cases.
| 2.9 Shell Commands | covered | Special-builtin option/error rows are now covered in `docs/posix-shall-trace.md`; command grammar/control-flow rows are verified.
| 2.10 Shell Grammar | covered | `docs/posix-shall-trace.md`, `docs/grammar-production-checklist.md`, `tests/diff/cases/man-ash-prefix-suffix.sh`, `tests/diff/cases/man-ash-grammar-negative.sh`, `tests/diff/cases/man-ash-grammar-reserved.sh`.
| 2.11 Signals/Traps | covered | `man-ash-trap*` differential corpus plus strict non-interactive and PTY-interactive matrices (`STRICT=1 make trap-noninteractive-matrix`, `STRICT=1 make trap-interactive-matrix`) for declared Linux comparator/signal scope.

## Bash-Compat Lane (Differential vs bash baseline)

| Area | Status | Evidence | Notes |
|---|---|---|---|
| Indexed-vs-assoc subscript evaluation mode | covered | `tests/diff/cases/bash-compat-subscript-eval-indexed.sh`, `tests/diff/cases/bash-compat-subscript-eval-indexed-extended.sh`, `tests/diff/cases/bash-compat-subscript-eval-indexed-sideeffects.sh`, `tests/diff/cases/bash-compat-subscript-eval-indexed-assign.sh`, `tests/diff/cases/bash-compat-subscript-eval-indexed-unset.sh`, `tests/diff/cases/bash-compat-subscript-eval-assoc.sh`, `tests/diff/cases/bash-compat-subscript-eval-assoc-quoted.sh` | Indexed paths use arithmetic evaluation in read/assign/unset flows; assoc paths use string-key semantics. |
| Array/hash operator expansion contexts (`[@]`/`[*]`, quoted/unquoted) | covered | `tests/diff/cases/bash-compat-param-array-contexts.sh`, `tests/diff/cases/bash-compat-param-array-hash-ops.sh`, `tests/diff/cases/bash-compat-param-array-hash-extended.sh`, `tests/diff/cases/bash-compat-param-contexts.sh`, `tests/diff/cases/bash-compat-param-collection-slicing.sh` | Replacement/trim/substr and field-boundary behavior are covered in bash lane. |
| Bash `read` option surface (`-a -d -e -i -n -N -p -r -s -t -u`) | covered | `tests/diff/cases/bash-read-options-core.sh`, `tests/diff/run_read_matrix.sh` | Compared against `bash --posix` in bash-compat lane; ash-lane option probes remain separate. |
| Bash builtin extension tranche (`typeset/local`, `mapfile/readarray`, `enable/help`, `dirs/pushd/popd`, `disown`) | covered | `tests/diff/cases/bash-builtin-declare-typeset-local.sh`, `tests/diff/cases/bash-compat-mapfile-readarray.sh`, `tests/diff/cases/bash-builtin-enable.sh`, `tests/diff/cases/bash-builtin-help.sh`, `tests/diff/cases/bash-builtin-dirstack.sh`, `tests/diff/cases/bash-builtin-disown.sh`, `tests/compat/run_bash_builtin_matrix.sh` | Builtin parity lane now has dedicated matrix gate (`make bash-builtin-matrix`) with memory/time limits. |
| Execution/environment/errors/signals/jobs category lane | covered | `tests/diff/cases/man-bash-posix-13-exec-errors-signals-jobs.sh`, `tests/diff/cases/man-bash-posix-14-env-exec-flow.sh`, `tests/compat/run_bash_posix_man_matrix.sh` | Adds explicit category-5 parity checks for command lookup/exec statuses, trap/wait/job paths, environment propagation, and pipeline exec-failure flow. |
| Completion/readline interactive semantics (`bind/complete/compgen/compopt`) | covered | `tests/diff/cases/bash-builtin-completion.sh`, `tests/compat/run_completion_interactive_matrix.sh`, `tests/compat/run_interactive_ux_matrix.sh` | Covered for declared comparator scope: non-interactive behavior plus strict PTY marker checks for bind/query, completion status paths, prompt command, history bang expansion, and prompt expansion markers. |
| Interactive foreground SIGINT continuation (no-trap Ctrl-C) | partial | `tests/compat/run_interactive_sigint_matrix.sh` | Dedicated PTY probe added; current run shows mctash does not yet match bash continuation behavior after Ctrl-C during foreground external command. |
| Parameter transformation operators `${v@op}` | covered | `tests/diff/cases/bash-man-param-transform-ops.sh`, `tests/diff/cases/bash-man-param-transform-ops-variants.sh`, `tests/diff/cases/bash-man-param-transform-prompt.sh`, `tests/diff/cases/bash-man-param-transform-prompt-escapes.sh` | Scalar/positional/array transforms and prompt-transform escape lanes are now covered in bash-compat differential evidence. |
| TIMEFORMAT semantics | covered | `tests/diff/cases/bash-man-timeformat.sh` | `%P` rendering and invalid-format diagnostics are parity-covered against bash. |
| BASH_XTRACEFD semantics | partial | `tests/diff/cases/bash-man-bash_xtracefd.sh` | Trace stream routing to configured FD differs; mctash still emits xtrace on stderr path. |
| TMOUT interactive auto-logout | partial | `tests/compat/run_interactive_tmout_matrix.sh` | Bash exits idle interactive shell with TMOUT; mctash currently does not auto-logout. |
| HISTTIMEFORMAT behavior depth | partial | `tests/diff/cases/bash-man-variables-surface.sh` | Surface-only coverage exists; no dedicated behavior test yet for timestamp formatting in history output. |
| Prompt escape depth (`PS2`/`PS4`) | partial | `tests/compat/run_interactive_ux_matrix.sh` | PS1 prompt behavior covered; PS2/PS4 escape semantics need dedicated assertions. |
| Upstream `builtins.tests` strict lane | covered | `tests/compat/run_bash_posix_upstream_matrix.sh`, `docs/reports/bash-posix-upstream-gap-latest.md`, `docs/reports/bash-upstream-builtins-gap-latest.md` | Strict gating scope is active and current upstream core lane is green. |

## POSIX Lane In-Scope Interactive Closure

Status:

- Closed.
- Active plan completed: `docs/plans/007-posix-interactive-and-job-control-closure.md`.

Rows closed in this pass:

- `C7.INT.01`..`C7.INT.10`
- `C8.JOB.03`, `C8.JOB.07`, `C8.JOB.11`, `C8.JOB.12`

Evidence gates:

- `STRICT=1 make interactive-ux-matrix`
- `STRICT=1 make completion-interactive-matrix`
- `STRICT=1 make jobs-interactive-matrix`
- `STRICT=1 make trap-noninteractive-matrix`
- `STRICT=1 make trap-interactive-matrix`

## Untested/Backlog Buckets

| Bucket | Status | Next concrete step |
|---|---|---|
| Requirement-level trace completeness (all "shall" rows) | covered | `docs/posix-shall-trace.md` rows are now mapped with case evidence and kept aligned by compliance-truth gate.
| Category-bucket gate closure (man-bash categories 1..9) | covered | `tests/compat/run_bash_category_bucket_matrix.sh` (`make category-buckets-matrix`) now enforces all buckets as green gates in declared scope.
| Grammar production closure | covered | `docs/grammar-production-checklist.md`, `tests/diff/cases/man-ash-grammar-negative.sh`, `tests/diff/cases/man-ash-grammar-reserved.sh`, `tests/diff/cases/man-ash-grammar-word-matrix.sh`, `tests/diff/cases/man-ash-prefix-suffix.sh`.
| Threaded-runtime parity checks | covered | Core cwd/fd/var isolation cases are covered (`man-ash-thread-cwd.sh`, `man-ash-thread-fd.sh`, `man-ash-thread-vars.sh`, `man-ash-thread-pipeline-cwd.sh`, `man-ash-thread-pipeline-fd.sh`) plus fallback-diag/process-subst regressions (`thread_unshare_fallback_diag`, `thread_unshare_forced_fail_diag`, `process_subst_*`, `thread_combined_bg_pipeline_process_subst`, `thread_multi_job_concurrency_isolation`, `thread_high_load_concurrency_isolation`, `thread_long_running_mixed_stress`, `monitor_mode_noninteractive_diag`, `monitor_mode_interactive_pty`, `monitor_mode_interactive_jobs_fg` in `tests/regressions/run.sh`) for declared Linux comparator scope.

## Sentinel-To-Structured Expansion Transition

| Area | Status | Evidence | Next step |
|---|---|---|---|
| Expansion engine migration plan exists | covered | `docs/plan.md` ("Expansion Engine Transition: Sentinels -> Structured Data") | Track execution progress here as items move from design to implementation. |
| Sentinel usage inventory and guard | covered | `tests/regressions/asdl_fallback_audit.sh`, `tests/regressions/asdl_fallback_allowlist.txt`, `tests/regressions/sentinel_transport_audit.sh` | Keep deny-surface current as structured coverage expands. |
| Typed expansion model introduction | covered | `src/mctash/expansion_model.py`, `src/mctash/runtime.py` (`_asdl_word_to_expansion_fields`, `_split_structured_field`, `_glob_structured_field`), `tests/regressions/run.sh` (`asdl_argv_braced_default_unquoted_split_semantics`, `asdl_argv_braced_default_unquoted_glob_semantics`) | Structured metadata now drives unquoted alt-word split+glob behavior end-to-end in ASDL path. |
| Typed adapters (ASDL and legacy parser) | covered | `src/mctash/runtime.py` (`_asdl_word_to_expansion_fields`, `_legacy_word_to_expansion_fields`, `_expand_braced_param` with `arg_fields=`), `tests/regressions/run.sh` (`legacy_expansion_adapter_equiv`) | ASDL operator-arg expansion now consumes structured fields directly; legacy parser stays as compatibility adapter. |
| Split/glob/pattern stages on structured fields | covered | `src/mctash/runtime.py` (`_split_structured_field`, `_glob_structured_field`, `_asdl_case_pattern_from_word`, `_split_replace_spec_structured`, `_replace_pattern_structured`), `tests/regressions/run.sh` (`asdl_param_pattern_arg_quoted_vs_unquoted_semantics`, `asdl_param_replace_arg_quoted_vs_unquoted_semantics`) | Pattern operators (`#`,`##`,`%`,`%%`,`/`) and case patterns now consume structured fields in ASDL path. |
| Sentinel collision proof cases | covered | `tests/diff/cases/unicode-pua-literals.sh`, `tests/diff/cases/unicode-pua-case-assignment.sh`, `tests/diff/cases/unicode-pua-operators.sh` | Collision cases are now in the parity lane and passing. |
