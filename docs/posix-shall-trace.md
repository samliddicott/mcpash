# POSIX "Shall" Trace (Requirement-Level Working Trace)

Date: 2026-03-03

Scope:

- Requirement-level working trace for normative areas in POSIX Shell Command Language (Issue 8, XCU Chapter 2).
- This file links each row to concrete executable evidence:
  - BusyBox ash corpus tests
  - Oil POSIX/spec subset tests
  - local differential cases (`tests/diff/cases`)

References:

- POSIX Shell Command Language (Issue 8): `https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/V3_chap02.html`
- POSIX rationale (XCU C.2): `https://pubs.opengroup.org/onlinepubs/9699919799/xrat/V4_xcu_chap02.html`
- BusyBox ash tests: `tests/busybox/ash_test`
- Oil subset tests: `tests/oil/oils-master/spec`
- 2.9/2.10 strict map: `docs/posix-2.9-2.10-trace.md`

Legend:

- `Verified`: directly evidenced by automated tests listed.
- `Partial`: significant evidence exists but not full corner-case closure.
- `Gap`: not sufficiently evidenced yet.

Case link notation:

- BusyBox/Oil evidence references file paths.
- Differential evidence references concrete runnable scripts in `tests/diff/cases`.

## 2.6 Word Expansions

| Requirement (normative intent) | Status | Evidence | Notes |
|---|---|---|---|
| Parameter expansion supports unset/null-sensitive operators (`-`, `:-`, `+`, `:+`, `=`, `:=`, `?`, `:?`) | Verified | `tests/busybox/ash_test/ash-vars/param_expand_default.tests`, `tests/busybox/ash_test/ash-vars/param_expand_assign.tests`, `tests/busybox/ash_test/ash-vars/param_expand_indicate_error.tests`, `tests/oil/oils-master/spec/var-op-test.test.sh`, `tests/diff/cases/man-ash-var-ops.sh` | Dynamic assignment and error branches are exercised. |
| Prefix/suffix pattern removal (`#`, `##`, `%`, `%%`) behaves per shell pattern matching rules | Verified | `tests/busybox/ash_test/ash-vars/var-pattern-replacement-in-parameter-expansion-*.tests`, `tests/oil/oils-master/spec/var-op-strip.test.sh`, `tests/diff/cases/man-ash-var-ops.sh`, `tests/regressions/run.sh` (`asdl_param_pattern_arg_quoted_vs_unquoted_semantics`) | Includes shortest/longest and quoting-sensitive variants. |
| `${#@}` and `${#*}` length follows joined positional expansion semantics | Verified | `tests/regressions/run.sh` (`param_len_special_at_star`) | Aligned with ash/dash behavior using IFS-joined positional text length. |
| Command substitution result participates correctly in later expansion phases | Covered | `tests/busybox/ash_test/ash-psubst/tick*.tests`, `tests/oil/oils-master/spec/smoke.test.sh` (`command sub`), `tests/diff/cases/man-ash-word-nesting.sh`, `tests/diff/cases/man-ash-word-nesting-matrix.sh` | Covered for ash/POSIX in-scope nesting forms; deeper combinatorics continue via corpus + differential matrices. |
| Field splitting uses `IFS` rules and preserves/elides fields appropriately | Verified | `tests/busybox/ash_test/ash-vars/var_wordsplit_ifs*.tests`, `tests/busybox/ash_test/ash-z_slow/many_ifs.tests`, `tests/oil/oils-master/spec/word-split.test.sh`, `tests/diff/cases/man-ash-read-ifs-matrix.sh`, `tests/diff/cases/man-ash-read-option-probe.sh` | Includes hard edge cases for `read`/`IFS` interactions and option-surface probes for this ash comparator target. |
| Pathname expansion (globbing) occurs after splitting and follows pattern semantics | Partial | `tests/busybox/ash_test/ash-glob/glob*.tests`, `tests/busybox/ash_test/ash-vars/param_glob.tests`, `tests/regressions/run.sh` (`asdl_argv_braced_default_unquoted_glob_semantics`, `asdl_param_pattern_arg_quoted_vs_unquoted_semantics`) | Covered for ash corpus patterns; formal full-space proof remains open. |

### Word-Expansion Divergence Register (ASDL Runtime)

| Case | POSIX classification | Current behavior | Target behavior | Authority | Evidence |
|---|---|---|---|---|---|
| Assignment-word quote removal in RHS (`name=value`) | POSIX required | Hybrid path: native ASDL for safe subsets (literal, named var sub, safe braced forms, arith sub, command sub); quote/backslash-sensitive forms still use legacy expansion path | Full native ASDL assignment expansion with POSIX quote-removal parity | POSIX XCU Chapter 2 (`2.2`/`2.6`), `man ash` | `tests/busybox/ash_test/ash-quoting/squote_in_varexp3.tests`, `tests/busybox/ash_test/ash-vars/param_expand_assign.tests`, `tests/regressions/run.sh` (`asdl_exec_shassignment_*`) |
| Backslash handling in double-quoted expansion-heavy words | POSIX required | Native ASDL argv expansion not yet enabled globally due parity regressions; legacy path retained | Enable native ASDL argv expansion after context-accurate quote/backslash handling is complete | POSIX XCU Chapter 2 (`2.2`/`2.6`), rationale C.2 | `tests/busybox/ash_test/ash-quoting/bkslash_case1.tests`, `tests/regressions/run.sh` (`monitor_mode_interactive_pty`) |
| Command substitution evaluation source in ASDL word parts | POSIX required | Uses structured `word_part.CommandSub.child` when available; falls back to `child_source` text path otherwise | Remove text fallback once structured child coverage is complete | POSIX XCU Chapter 2 (`2.6.3`) and rationale C.2 | `tests/busybox/ash_test/ash-psubst/tick*.tests`, `tests/regressions/run.sh` (`asdl_exec_shassignment_cmdsub_*`) |

Diagnostic policy note:
- For malformed expansion forms, parity target is error behavior (non-zero status and control-flow impact), not byte-for-byte diagnostic text equality, unless POSIX explicitly requires text.

## 2.2 Quoting

| Requirement (normative intent) | Status | Evidence | Notes |
|---|---|---|---|
| Single quotes preserve literal characters until closing quote | Verified | `tests/busybox/ash_test/ash-quoting/squote_in_varexp.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` | Includes literalization and embedding behavior. |
| Double quotes preserve most literal characters while allowing parameter/command/arithmetic expansion | Verified | `tests/busybox/ash_test/ash-quoting/*.tests`, `tests/oil/oils-master/spec/var-sub.test.sh`, `tests/oil/oils-master/spec/shell-grammar.test.sh` | Expansion in quoted contexts is broadly exercised. |
| Backslash escaping obeys quoting context and newline-continuation rules | Partial | `tests/busybox/ash_test/ash-parsing/bkslash_newline*.tests`, `tests/busybox/ash_test/ash-parsing/escape*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` | Covered in parser suites; not yet exhaustively traced by requirement row. |

## 2.3 Token Recognition

| Requirement (normative intent) | Status | Evidence | Notes |
|---|---|---|---|
| Tokenization recognizes operators, words, and separators per shell lexical rules | Verified | `tests/busybox/ash_test/ash-parsing/*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` | Parser/lexer acceptance tests cover broad operator/word spaces. |
| Comment handling and escaped newline handling preserve command structure | Verified | `tests/busybox/ash_test/ash-parsing/comment*.tests`, `tests/busybox/ash_test/ash-parsing/bkslash_newline*.tests` | Core lexical conventions are covered in parsing corpus. |
| Here-doc token recognition and deferred body attachment follow grammar sequencing | Verified | `tests/busybox/ash_test/ash-heredoc/heredoc*.tests`, `tests/oil/oils-master/spec/posix.test.sh` (`Multiple here docs on one line`) | Queue/order behavior is validated. |

## 2.4 Reserved Words

| Requirement (normative intent) | Status | Evidence | Notes |
|---|---|---|---|
| Reserved words are recognized only in grammar-appropriate positions | Verified | `tests/busybox/ash_test/ash-parsing/groups_and_keywords1.tests`, `tests/busybox/ash_test/ash-misc/for_with_keywords.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh`, `tests/diff/cases/man-ash-grammar-reserved.sh`, `tests/regressions/run.sh` (`reserved_word_*`) | Context-sensitive reserved-word behavior is covered by corpus and local matrices. |
| Compound-command keywords (`if`, `then`, `fi`, `case`, `esac`, loops) parse and execute in order | Verified | `tests/busybox/ash_test/ash-misc/if_false_exitcode.tests`, `tests/busybox/ash_test/ash-misc/case1.tests`, `tests/busybox/ash_test/ash-misc/while*.tests`, `tests/oil/oils-master/spec/if_.test.sh`, `tests/oil/oils-master/spec/case_.test.sh` | Execution semantics covered across multiple corpora. |

## 2.5 Parameters and Variables

| Requirement (normative intent) | Status | Evidence | Notes |
|---|---|---|---|
| Variable assignment, retrieval, and unset/readonly behavior follow shell rules | Verified | `tests/busybox/ash_test/ash-vars/readonly*.tests`, `tests/busybox/ash_test/ash-vars/unset.tests`, `tests/diff/cases/man-ash-env.sh` | Differential case adds direct ash-vs-mctash behavior checks. |
| Positional parameters and special parameters (`$?`, `$#`, `$*`, `$@`) track command execution semantics | Verified | `tests/busybox/ash_test/ash-vars/var_posix*.tests`, `tests/busybox/ash_test/ash-misc/and-or.tests`, `tests/diff/cases/man-ash-set.sh` | Includes option/position reset and status sensitivity. |
| Parameter-length and default/assign/error operators behave for unset/null branches | Verified | `tests/busybox/ash_test/ash-vars/param_expand_*.tests`, `tests/oil/oils-master/spec/var-op-test.test.sh`, `tests/regressions/run.sh` (`param_len_special_at_star`) | Verified against broad operator matrix. |

## 2.7 Redirection

| Requirement (normative intent) | Status | Evidence | Notes |
|---|---|---|---|
| Input/output redirections (`<`, `>`, `>>`) apply to command environment correctly | Verified | `tests/busybox/ash_test/ash-redir/redir*.tests`, `tests/oil/oils-master/spec/redirect.test.sh` | Includes builtin/external combinations and restore behavior. |
| IO-number redirections (`n>`, `n<`, `n>&m`, `n<&m`) work and reject invalid FD forms | Verified | `tests/busybox/ash_test/ash-redir/redir_to_bad_fd*.tests`, `tests/busybox/ash_test/ash-redir/redir_escapednum.tests`, `tests/oil/oils-master/spec/redirect.test.sh` (`<&`, `2>&1`) | Error paths validated in both corpora. |
| Here-doc delimiter quoting controls expansion; body capture is syntactically correct | Partial | `tests/busybox/ash_test/ash-heredoc/heredoc*.tests`, `tests/oil/oils-master/spec/posix.test.sh` (`Multiple here docs on one line`), `tests/diff/cases/man-ash-redir.sh` | Wide coverage; remaining edge space is mostly undocumented ultra-corners. |
| Redirection failures produce non-success status and do not silently continue incorrectly | Verified | `tests/busybox/ash_test/ash-redir/redir_to_bad_fd.tests`, `tests/oil/oils-master/spec/command_.test.sh` (`Permission denied`, `Not a dir`) | Status/diagnostic mapping is now stable in tested paths. |

## 2.8 Exit Status and Errors

| Requirement (normative intent) | Status | Evidence | Notes |
|---|---|---|---|
| Command-not-found and non-executable failures map to shell-expected statuses (`127`/`126`) | Verified | `tests/busybox/ash_test/ash-misc/exitcode_ENOENT.tests`, `tests/busybox/ash_test/ash-misc/exitcode_EACCES.tests`, `tests/oil/oils-master/spec/command_.test.sh` | Slash-path and PATH lookup diagnostics were recently corrected. |
| Pipeline status follows shell option semantics (`pipefail` off/on) | Verified | `tests/busybox/ash_test/ash-misc/pipefail.tests`, `tests/oil/oils-master/spec/pipeline.test.sh` (`Exit code is last status`) | Oil includes one intentional ash-vs-OSH semantic difference on last-pipeline-process behavior. |
| `!` pipeline negation inverts status per shell grammar semantics | Verified | `tests/busybox/ash_test/ash-parsing/negate.tests`, `tests/oil/oils-master/spec/pipeline.test.sh` (`! turns non-zero into zero`, `! turns zero into 1`) | Negation is stable across simple and compound contexts. |

## 2.12 Shell Execution Environment

| Requirement (normative intent) | Status | Evidence | Notes |
|---|---|---|---|
| Prefix assignments and exported environment entries are applied for command execution | Verified | `tests/busybox/ash_test/ash-misc/assignment*.tests`, `tests/busybox/ash_test/ash-standalone/nofork_env.tests`, `tests/diff/cases/man-ash-env.sh` | Includes shell variable/export interaction paths. |
| Exec replacement and no-return behavior are correct for successful `exec` | Verified | `tests/busybox/ash_test/ash-misc/exec.tests`, `tests/diff/cases/man-ash-eval-exec.sh` | Differential case checks post-exec non-return path. |
| Threaded runtime deviations from forked shell process model are documented and bounded | Partial | `docs/threaded-runtime-deviations.md`, `tests/diff/cases/man-ash-thread-cwd.sh`, `tests/diff/cases/man-ash-thread-fd.sh`, `tests/diff/cases/man-ash-thread-vars.sh`, `tests/diff/cases/man-ash-thread-pipeline-cwd.sh`, `tests/diff/cases/man-ash-thread-pipeline-fd.sh`, `tests/regressions/run.sh` (`thread_unshare_fallback_diag`, `thread_unshare_forced_fail_diag`, `thread_combined_bg_pipeline_process_subst`, `thread_multi_job_concurrency_isolation`, `thread_high_load_concurrency_isolation`, `thread_long_running_mixed_stress`, `monitor_mode_interactive_pty`, `monitor_mode_interactive_jobs_fg`) | Design + differential evidence exists for core cwd/fd/var isolation and fallback diagnostics; broader threaded edge space remains partial. |

## 2.13 Shell Variables

| Requirement (normative intent) | Status | Evidence | Notes |
|---|---|---|---|
| Shell options/variables exposed by builtins (`set`, readonly/export state) are reflected consistently | Partial | `tests/busybox/ash_test/ash-vars/*.tests`, `tests/diff/cases/man-ash-set.sh`, `tests/diff/cases/set-listing.sh`, `tests/diff/cases/man-ash-set-monitor.sh` | Functional behavior is covered; output formatting parity remains partial. |
| `$PWD` behavior across `cd` aligns with shell semantics in non-interactive runs | Verified | `tests/diff/cases/man-ash-pwd.sh`, `tests/diff/cases/man-ash-cd-source.sh` | Differential cases enforce parity on observed outputs. |

### Bash-Compat Variable Extensions (Tracked with Differential Bash Lane)

| Extension requirement | Status | Evidence | Notes |
|---|---|---|---|
| Indexed-array subscripts evaluate in arithmetic mode | Covered | `tests/diff/cases/bash-compat-subscript-eval-indexed.sh`, `tests/diff/cases/bash-compat-subscript-eval-indexed-extended.sh`, `tests/diff/cases/bash-compat-subscript-eval-indexed-sideeffects.sh`, `tests/diff/cases/bash-compat-subscript-eval-indexed-assign.sh`, `tests/diff/cases/bash-compat-subscript-eval-indexed-unset.sh` | Includes variable/expression indices, read/assign/unset side effects, negative index behavior, and invalid-index non-success behavior. |
| Assoc-array subscripts use string-key mode (no numeric coercion) | Covered | `tests/diff/cases/bash-compat-subscript-eval-assoc.sh`, `tests/diff/cases/bash-compat-subscript-eval-assoc-quoted.sh` | Includes numeric-like keys (`01`, `1+1`) and quoted/expanded key forms. |
| Array operator expansion preserves quoted/unquoted `[@]`/`[*]` context behavior | Covered | `tests/diff/cases/bash-compat-param-array-contexts.sh`, `tests/diff/cases/bash-compat-param-array-hash-ops.sh`, `tests/diff/cases/bash-compat-param-array-hash-extended.sh`, `tests/diff/cases/bash-compat-param-contexts.sh`, `tests/diff/cases/bash-compat-param-collection-slicing.sh` | Covers replacement/trim/substr operators and field-boundary behavior under quoting variants. |

## 2.14 Special Built-In Utilities

| Requirement (normative intent) | Status | Evidence | Notes |
|---|---|---|---|
| `set` option toggles and positional updates follow special-builtin semantics | Verified | `tests/diff/cases/man-ash-set.sh`, `tests/diff/cases/set-listing.sh`, `tests/busybox/ash_test/ash-getopts/*.tests` | Status/option interactions are checked directly. |
| `eval` evaluates constructed command text in current shell context | Verified | `tests/diff/cases/man-ash-eval-exec.sh`, `tests/busybox/ash_test/ash-misc/eval*.tests` | Includes error-status-sensitive execution paths. |
| `command`/`builtin` affect lookup and bypass behavior correctly | Verified | `tests/diff/cases/man-ash-alias.sh`, `tests/busybox/ash_test/ash-misc/command*.tests` | Lookup semantics validated in both corpora. |
| `readonly`, `export`, `unset`, `trap`, `times`, `umask`, `ulimit` obey core semantics | Partial | `tests/diff/cases/man-ash-env.sh`, `tests/diff/cases/man-ash-trap.sh`, `tests/diff/cases/man-ash-trap-matrix.sh`, `tests/diff/cases/man-ash-trap-signals.sh`, `tests/diff/cases/man-ash-trap-delivery.sh`, `tests/diff/cases/man-ash-trap-signal-matrix.sh`, `tests/diff/cases/man-ash-trap-full.sh`, `tests/diff/cases/man-ash-trap-nested.sh`, `tests/diff/cases/man-ash-resource.sh`, `tests/diff/cases/man-ash-ulimit-flags.sh`, `tests/diff/cases/man-ash-ulimit-set.sh`, `tests/diff/cases/man-ash-ulimit-errors.sh`, `tests/diff/cases/man-ash-ulimit-soft-hard.sh`, `tests/busybox/ash_test/ash-vars/readonly*.tests`, `tests/busybox/ash_test/ash-signals/signal*.tests` | Core behavior covered with extended differential matrices; full option/signal universes remain partial. |

## 2.15 Shell Grammar Lexical Conventions

| Requirement (normative intent) | Status | Evidence | Notes |
|---|---|---|---|
| Newline, semicolon, and continuation handling produce expected command boundaries | Verified | `tests/busybox/ash_test/ash-parsing/noeol*.tests`, `tests/busybox/ash_test/ash-parsing/bkslash_newline*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` | Command boundary behavior is well covered. |
| Grammar-level parse failures return non-zero and avoid executing malformed constructs | Covered | `tests/busybox/ash_test/ash-parsing/nodone*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` (`Invalid token`), `tests/diff/cases/man-ash-grammar-negative.sh`, `tests/regressions/run.sh` (`parser_*`) | Rejection semantics and non-execution behavior are covered; exact diagnostic text equivalence remains implementation-specific. |

## 2.11 Signals, Traps, and Related Error Paths

| Requirement (normative intent) | Status | Evidence | Notes |
|---|---|---|---|
| `trap` installs and runs handlers for supported signals and EXIT where applicable | Partial | `tests/busybox/ash_test/ash-signals/signal*.tests`, `tests/busybox/ash_test/ash-signals/return_in_trap1.tests`, `tests/busybox/ash_test/ash-signals/save-ret.tests`, `tests/diff/cases/man-ash-trap.sh`, `tests/diff/cases/man-ash-trap-matrix.sh`, `tests/diff/cases/man-ash-trap-signals.sh`, `tests/diff/cases/man-ash-trap-delivery.sh`, `tests/diff/cases/man-ash-trap-signal-matrix.sh`, `tests/diff/cases/man-ash-trap-full.sh`, `tests/diff/cases/man-ash-trap-nested.sh` | Non-interactive trap matrix is broad; exhaustive signal-by-signal and interactive semantics remain out of scope. |
| Signal handling does not break command execution and wait/child behavior in tested cases | Verified | `tests/busybox/ash_test/ash-signals/reap1.tests`, `tests/busybox/ash_test/ash-signals/sigquit_exec.tests`, `tests/busybox/ash_test/ash-misc/wait*.tests` | Covers practical trap/wait integration paths. |

## 2.9 Shell Commands

| Requirement (normative intent) | Status | Evidence | Notes |
|---|---|---|---|
| Simple commands perform assignment prefix handling, command lookup, and argument execution in shell order | Verified | `tests/busybox/ash_test/ash-misc/assignment*.tests`, `tests/busybox/ash_test/ash-misc/command*.tests`, `tests/oil/oils-master/spec/command-parsing.test.sh` | Includes prefix assignments on normal and control-flow commands. |
| Lists and and/or chains (`;`, `&`, `&&`, `||`) execute with short-circuit semantics | Verified | `tests/busybox/ash_test/ash-misc/and-or.tests`, `tests/busybox/ash_test/ash-parsing/and_or_and_backgrounding.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` (`a && b || c`) | Backgrounding and chain precedence are exercised. |
| Compound commands (`if`, `case`, `while`, `until`, `for`, grouping, subshell) execute with correct control-flow behavior | Verified | `tests/busybox/ash_test/ash-misc/if_false_exitcode.tests`, `tests/busybox/ash_test/ash-misc/case1.tests`, `tests/busybox/ash_test/ash-misc/while*.tests`, `tests/busybox/ash_test/ash-misc/for*.tests`, `tests/busybox/ash_test/ash-parsing/group*.tests`, `tests/oil/oils-master/spec/if_.test.sh`, `tests/oil/oils-master/spec/case_.test.sh`, `tests/oil/oils-master/spec/loop.test.sh` | Includes nested loop break/continue and subshell cases in current corpora. |
| Function definition and invocation preserve positional/local scope behavior in tested cases | Verified | `tests/busybox/ash_test/ash-misc/func*.tests`, `tests/busybox/ash_test/ash-misc/source_argv_and_shift.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` (`Function def`), `tests/diff/cases/man-ash-function-scope.sh` | Positional/local scope behavior in non-interactive tested paths is now directly covered. |
| Special builtins (`eval`, `command`, `exec`, `set`, `readonly`, etc.) honor command semantics in tested paths | Partial | `tests/busybox/ash_test/ash-misc/eval*.tests`, `tests/busybox/ash_test/ash-misc/exec.tests`, `tests/busybox/ash_test/ash-vars/readonly*.tests`, `tests/busybox/ash_test/ash-getopts/*.tests`, `tests/oil/oils-master/spec/command_.test.sh`, `tests/diff/cases/man-ash-set.sh`, `tests/diff/cases/man-ash-env.sh`, `tests/diff/cases/man-ash-eval-exec.sh`, `tests/diff/cases/man-ash-alias.sh`, `tests/diff/cases/man-ash-getopts.sh`, `tests/diff/cases/man-ash-fc.sh`, `tests/diff/cases/man-ash-fc-editor-env.sh`, `tests/diff/cases/man-ash-fc-ranges.sh` | In-scope behavior is validated with differential evidence; full option-surface parity remains partial. |

## 2.10 Shell Grammar

| Requirement (normative intent) | Status | Evidence | Notes |
|---|---|---|---|
| Parser accepts valid command grammar forms for lists/pipelines/compound commands | Verified | `tests/busybox/ash_test/ash-parsing/*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` | Current parser pass set covers broad accepted grammar forms. |
| Parser rejects invalid grammar with non-success status and diagnostics | Covered | `tests/busybox/ash_test/ash-parsing/nodone1.tests`, `tests/busybox/ash_test/ash-parsing/nodone2.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` (`Invalid token`), `tests/diff/cases/man-ash-grammar-negative.sh`, `tests/regressions/run.sh` (`parser_*`) | Rejection status behavior is covered across corpora and local negative matrices; exact text parity remains implementation-specific. |
| Here-doc grammar attachment/order and multi-here-doc parsing follow shell grammar constraints | Verified | `tests/busybox/ash_test/ash-heredoc/heredoc*.tests`, `tests/oil/oils-master/spec/posix.test.sh` (`Multiple here docs on one line`) | Includes parser queueing/order-sensitive cases. |
| Case grammar variants (optional trailing `;;`, pattern alternation, oneline forms) parse correctly | Verified | `tests/busybox/ash_test/ash-misc/case1.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` (`Case without last dsemi`, `Case with 2 options`, oneline forms), `tests/oil/oils-master/spec/case_.test.sh` | Covers core POSIX case grammar forms in scope. |

### 2.9/2.10 ASDL Alignment Notes

| Runtime grammar area | mctash parser/LST node | OSH ASDL anchor | Current alignment |
|---|---|---|---|
| Simple command / assignment / redirects | `LstSimpleCommand`, `LstShAssignmentCommand`, `LstRedirect` | `command.Simple`, `assign_pair`, `redir` (from `src/syntax/osh/syntax.asdl`) | Aligned in current mapper path (`src/mctash/asdl_map.py`). |
| List / and-or / pipeline | `LstListNode`, `LstAndOr`, `LstPipeline` | `command.CommandList`, `command.AndOr`, `command.Pipeline` | Aligned; operator positions preserved where available. |
| Compound commands (`if/while/for/case`) | `LstIfCommand`, `LstWhileCommand`, `LstForCommand`, `LstCaseCommand` | `command.If`, `command.WhileUntil`, `command.ForEach`, `command.Case` | Aligned for ash scope and tested productions. |
| Group/subshell/function | `LstGroupCommand`, `LstSubshellCommand`, `LstFunctionDef` | `command.BraceGroup`, `command.Subshell`, `command.ShFunction` | Aligned; function form coverage remains ash-style in-scope. |
| Word parts / substitutions | `LstWord` and parts (`Param`, `Braced`, `CommandSub`, `ArithSub`, quote parts) | `word_t` variants and expression nodes in OSH ASDL | Aligned for tested word-expansion grammar surface. |

### 2.9/2.10 POSIX vs OSH-ASDL Tension Log

- No normative POSIX conflict currently blocks the ash-scope mapping for 2.9/2.10.
- Any future divergence (e.g., Bash-extension grammar admitted ahead of POSIX rows) should be recorded here and reflected in:
  - `docs/grammar-production-checklist.md`
  - `docs/gap-board.md`

## Open Gaps (Next "Shall" Expansion)

1. Refine grammar-production-level trace (nonterminal-by-nonterminal) for parser completeness reporting:
   - `docs/grammar-production-checklist.md`
   - `docs/gap-board.md`
2. Add per-requirement negative tests for diagnostics formatting and ambiguous parse errors.
3. Keep startup-option parity tracked in `docs/startup-option-matrix.md`; add requirement-level rows here only when they materially alter POSIX Chapter 2 behavior.
4. Keep `fc` differential parity tracked as an environment blocker where comparator `ash` lacks `fc`:
   - `docs/fc-comparator-blocker.md`
