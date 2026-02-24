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

## Open Gaps (Next "Shall" Expansion)

1. Expand to full `2.9`/`2.10` requirement rows (grammar production-level trace).
2. Add requirement rows for startup option semantics from `man ash` synopsis where in milestone scope.
3. Add per-requirement negative tests for diagnostics formatting and ambiguous parse errors.
