# POSIX "Shall" Trace (Selected High-Risk Areas)

Date: 2026-02-24

Scope:

- Requirement-level trace for selected normative areas in POSIX Shell Command Language (Issue 8, XCU Chapter 2).
- Focused on sections most likely to regress in shell implementations:
  - expansions
  - redirections / here-doc
  - exit status / diagnostic behavior
  - traps/signals

References:

- POSIX Shell Command Language (Issue 8): `https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/V3_chap02.html`
- POSIX rationale (XCU C.2): `https://pubs.opengroup.org/onlinepubs/9699919799/xrat/V4_xcu_chap02.html`
- BusyBox ash tests: `tests/busybox/ash_test`
- Oil subset tests: `tests/oil/oils-master/spec`

Legend:

- `Verified`: directly evidenced by automated tests listed.
- `Partial`: significant evidence exists but not full corner-case closure.
- `Gap`: not sufficiently evidenced yet.

## 2.6 Word Expansions

| Requirement (normative intent) | Status | Evidence | Notes |
|---|---|---|---|
| Parameter expansion supports unset/null-sensitive operators (`-`, `:-`, `+`, `:+`, `=`, `:=`, `?`, `:?`) | Verified | `tests/busybox/ash_test/ash-vars/param_expand_default.tests`, `tests/busybox/ash_test/ash-vars/param_expand_assign.tests`, `tests/busybox/ash_test/ash-vars/param_expand_indicate_error.tests`, `tests/oil/oils-master/spec/var-op-test.test.sh` | Dynamic assignment and error branches are exercised. |
| Prefix/suffix pattern removal (`#`, `##`, `%`, `%%`) behaves per shell pattern matching rules | Verified | `tests/busybox/ash_test/ash-vars/var-pattern-replacement-in-parameter-expansion-*.tests`, `tests/oil/oils-master/spec/var-op-strip.test.sh` | Includes shortest/longest and quoting-sensitive variants. |
| Command substitution result participates correctly in later expansion phases | Partial | `tests/busybox/ash_test/ash-psubst/tick*.tests`, `tests/oil/oils-master/spec/smoke.test.sh` (`command sub`) | Strong coverage, but exhaustive nested quoting matrices are still partial. |
| Field splitting uses `IFS` rules and preserves/elides fields appropriately | Verified | `tests/busybox/ash_test/ash-vars/var_wordsplit_ifs*.tests`, `tests/busybox/ash_test/ash-z_slow/many_ifs.tests`, `tests/oil/oils-master/spec/word-split.test.sh` | Includes hard edge cases for `read`/`IFS` interactions. |
| Pathname expansion (globbing) occurs after splitting and follows pattern semantics | Partial | `tests/busybox/ash_test/ash-glob/glob*.tests`, `tests/busybox/ash_test/ash-vars/param_glob.tests` | Covered for ash corpus patterns; formal full-space proof remains open. |

## 2.7 Redirection

| Requirement (normative intent) | Status | Evidence | Notes |
|---|---|---|---|
| Input/output redirections (`<`, `>`, `>>`) apply to command environment correctly | Verified | `tests/busybox/ash_test/ash-redir/redir*.tests`, `tests/oil/oils-master/spec/redirect.test.sh` | Includes builtin/external combinations and restore behavior. |
| IO-number redirections (`n>`, `n<`, `n>&m`, `n<&m`) work and reject invalid FD forms | Verified | `tests/busybox/ash_test/ash-redir/redir_to_bad_fd*.tests`, `tests/busybox/ash_test/ash-redir/redir_escapednum.tests`, `tests/oil/oils-master/spec/redirect.test.sh` (`<&`, `2>&1`) | Error paths validated in both corpora. |
| Here-doc delimiter quoting controls expansion; body capture is syntactically correct | Partial | `tests/busybox/ash_test/ash-heredoc/heredoc*.tests`, `tests/oil/oils-master/spec/posix.test.sh` (`Multiple here docs on one line`) | Wide coverage; remaining edge space is mostly undocumented ultra-corners. |
| Redirection failures produce non-success status and do not silently continue incorrectly | Verified | `tests/busybox/ash_test/ash-redir/redir_to_bad_fd.tests`, `tests/oil/oils-master/spec/command_.test.sh` (`Permission denied`, `Not a dir`) | Status/diagnostic mapping is now stable in tested paths. |

## 2.8 Exit Status and Errors

| Requirement (normative intent) | Status | Evidence | Notes |
|---|---|---|---|
| Command-not-found and non-executable failures map to shell-expected statuses (`127`/`126`) | Verified | `tests/busybox/ash_test/ash-misc/exitcode_ENOENT.tests`, `tests/busybox/ash_test/ash-misc/exitcode_EACCES.tests`, `tests/oil/oils-master/spec/command_.test.sh` | Slash-path and PATH lookup diagnostics were recently corrected. |
| Pipeline status follows shell option semantics (`pipefail` off/on) | Verified | `tests/busybox/ash_test/ash-misc/pipefail.tests`, `tests/oil/oils-master/spec/pipeline.test.sh` (`Exit code is last status`) | Oil includes one intentional ash-vs-OSH semantic difference on last-pipeline-process behavior. |
| `!` pipeline negation inverts status per shell grammar semantics | Verified | `tests/busybox/ash_test/ash-parsing/negate.tests`, `tests/oil/oils-master/spec/pipeline.test.sh` (`! turns non-zero into zero`, `! turns zero into 1`) | Negation is stable across simple and compound contexts. |

## 2.11 Signals, Traps, and Related Error Paths

| Requirement (normative intent) | Status | Evidence | Notes |
|---|---|---|---|
| `trap` installs and runs handlers for supported signals and EXIT where applicable | Partial | `tests/busybox/ash_test/ash-signals/signal*.tests`, `tests/busybox/ash_test/ash-signals/return_in_trap1.tests`, `tests/busybox/ash_test/ash-signals/save-ret.tests` | BusyBox signal suite passes; interactive-only behaviors are out of current scope. |
| Signal handling does not break command execution and wait/child behavior in tested cases | Verified | `tests/busybox/ash_test/ash-signals/reap1.tests`, `tests/busybox/ash_test/ash-signals/sigquit_exec.tests`, `tests/busybox/ash_test/ash-misc/wait*.tests` | Covers practical trap/wait integration paths. |

## 2.9 Shell Commands

| Requirement (normative intent) | Status | Evidence | Notes |
|---|---|---|---|
| Simple commands perform assignment prefix handling, command lookup, and argument execution in shell order | Verified | `tests/busybox/ash_test/ash-misc/assignment*.tests`, `tests/busybox/ash_test/ash-misc/command*.tests`, `tests/oil/oils-master/spec/command-parsing.test.sh` | Includes prefix assignments on normal and control-flow commands. |
| Lists and and/or chains (`;`, `&`, `&&`, `||`) execute with short-circuit semantics | Verified | `tests/busybox/ash_test/ash-misc/and-or.tests`, `tests/busybox/ash_test/ash-parsing/and_or_and_backgrounding.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` (`a && b || c`) | Backgrounding and chain precedence are exercised. |
| Compound commands (`if`, `case`, `while`, `until`, `for`, grouping, subshell) execute with correct control-flow behavior | Verified | `tests/busybox/ash_test/ash-misc/if_false_exitcode.tests`, `tests/busybox/ash_test/ash-misc/case1.tests`, `tests/busybox/ash_test/ash-misc/while*.tests`, `tests/busybox/ash_test/ash-misc/for*.tests`, `tests/busybox/ash_test/ash-parsing/group*.tests`, `tests/oil/oils-master/spec/if_.test.sh`, `tests/oil/oils-master/spec/case_.test.sh`, `tests/oil/oils-master/spec/loop.test.sh` | Includes nested loop break/continue and subshell cases in current corpora. |
| Function definition and invocation preserve positional/local scope behavior in tested cases | Partial | `tests/busybox/ash_test/ash-misc/func*.tests`, `tests/busybox/ash_test/ash-misc/source_argv_and_shift.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` (`Function def`) | Strong coverage for current scope; full interactive/debug corner behavior not claimed. |
| Special builtins (`eval`, `command`, `exec`, `set`, `readonly`, etc.) honor command semantics in tested paths | Partial | `tests/busybox/ash_test/ash-misc/eval*.tests`, `tests/busybox/ash_test/ash-misc/exec.tests`, `tests/busybox/ash_test/ash-vars/readonly*.tests`, `tests/busybox/ash_test/ash-getopts/*.tests`, `tests/oil/oils-master/spec/command_.test.sh` | In-scope behavior is validated; full option surface parity still being expanded. |

## 2.10 Shell Grammar

| Requirement (normative intent) | Status | Evidence | Notes |
|---|---|---|---|
| Parser accepts valid command grammar forms for lists/pipelines/compound commands | Verified | `tests/busybox/ash_test/ash-parsing/*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` | Current parser pass set covers broad accepted grammar forms. |
| Parser rejects invalid grammar with non-success status and diagnostics | Partial | `tests/busybox/ash_test/ash-parsing/nodone1.tests`, `tests/busybox/ash_test/ash-parsing/nodone2.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` (`Invalid token`) | Rejection behavior is covered; message text exactness is implementation-specific in some cases. |
| Here-doc grammar attachment/order and multi-here-doc parsing follow shell grammar constraints | Verified | `tests/busybox/ash_test/ash-heredoc/heredoc*.tests`, `tests/oil/oils-master/spec/posix.test.sh` (`Multiple here docs on one line`) | Includes parser queueing/order-sensitive cases. |
| Case grammar variants (optional trailing `;;`, pattern alternation, oneline forms) parse correctly | Verified | `tests/busybox/ash_test/ash-misc/case1.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` (`Case without last dsemi`, `Case with 2 options`, oneline forms), `tests/oil/oils-master/spec/case_.test.sh` | Covers core POSIX case grammar forms in scope. |

## Open Gaps (Next "Shall" Expansion)

1. Keep startup-option parity tracked in `docs/startup-option-matrix.md`; add requirement-level rows in this document only where they intersect POSIX Chapter 2 semantics.
2. Refine grammar-production-level trace (nonterminal-by-nonterminal) for parser completeness reporting:
   - `docs/grammar-production-checklist.md`
3. Add per-requirement negative tests for diagnostics formatting and ambiguous parse errors.
