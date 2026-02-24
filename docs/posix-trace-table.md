# POSIX Trace Table (Issue 8, XCU Chapter 2)

Date: 2026-02-24

References:

- POSIX Shell Command Language: `https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/V3_chap02.html`
- POSIX rationale (XCU C.2): `https://pubs.opengroup.org/onlinepubs/9699919799/xrat/V4_xcu_chap02.html`
- BusyBox ash corpus currently run by mctash: `tests/busybox/ash_test`
- Oil spec subset currently run by mctash: `tests/oil/oils-master/spec`

Latest run evidence:

- BusyBox ash corpus: `ok=357 fail=0 skip=0` (full run)
- Oil subset: `total=372 pass=244 fail=1 skip=127`
  - One intentional semantic difference in `pipeline.test.sh` (“last command in pipeline runs in its own process”) where ash/dash behavior is preserved.

Legend:

- `Covered`: exercised by current automated corpus with direct case evidence.
- `Partial`: broad evidence exists but not all normative corner cases are traced.
- `Gap`: not yet sufficiently evidenced for a formal claim.

## POSIX section mapping

| POSIX section | Status | BusyBox evidence | Oil evidence | Notes |
|---|---|---|---|---|
| `2.2 Quoting` | Covered (Partial) | `tests/busybox/ash_test/ash-quoting/squote_in_varexp.tests`, `tests/busybox/ash_test/ash-quoting/dollar_squote_bash1.tests`, `tests/busybox/ash_test/ash-parsing/quote4.tests` | `tests/oil/oils-master/spec/shell-grammar.test.sh` (`Command sub`, `Subshell on multiple lines`) | Strong practical coverage; deep nested corner proofs still partial. |
| `2.3 Token Recognition` | Covered (Partial) | `tests/busybox/ash_test/ash-parsing/comment1.tests`, `tests/busybox/ash_test/ash-parsing/escape5.tests`, `tests/busybox/ash_test/ash-alias/alias.tests` | `tests/oil/oils-master/spec/shell-grammar.test.sh` (`Invalid token`, redirect forms) | Lexer/parser behavior validated in both corpora. |
| `2.4 Reserved Words` | Covered (Partial) | `tests/busybox/ash_test/ash-parsing/groups_and_keywords1.tests`, `tests/busybox/ash_test/ash-misc/for_with_keywords.tests`, `tests/busybox/ash_test/ash-misc/elif2.tests` | `tests/oil/oils-master/spec/shell-grammar.test.sh` (`If`, `For loop`, `While loop`) | Reserved-word context handling is exercised across compound commands. |
| `2.5 Parameters and Variables` | Covered (Partial) | `tests/busybox/ash_test/ash-vars/var_posix1.tests`, `tests/busybox/ash_test/ash-vars/param_expand_default.tests`, `tests/busybox/ash_test/ash-vars/param_expand_assign.tests` | `tests/oil/oils-master/spec/var-op-test.test.sh` (`Default value`, `Assign default`, `Error when unset`) | Dynamic assignment, null/unset branches, and special params broadly covered. |
| `2.6 Word Expansions` | Covered (Partial) | `tests/busybox/ash_test/ash-vars/var_wordsplit_ifs5.tests`, `tests/busybox/ash_test/ash-glob/glob1.tests`, `tests/busybox/ash_test/ash-psubst/tick4.tests`, `tests/busybox/ash_test/ash-arith/arith.tests` | `tests/oil/oils-master/spec/word-split.test.sh`, `tests/oil/oils-master/spec/var-op-strip.test.sh`, `tests/oil/oils-master/spec/var-sub.test.sh` | Expansion pipeline is highly covered; still not a full normative proof. |
| `2.7 Redirection` | Covered (Partial) | `tests/busybox/ash_test/ash-redir/redir_to_bad_fd255.tests`, `tests/busybox/ash_test/ash-redir/redir_exec1.tests`, `tests/busybox/ash_test/ash-heredoc/heredoc_var_expand1.tests` | `tests/oil/oils-master/spec/redirect.test.sh` (`<&`, `2>&1`, `<>`, here-doc/redirect mixes) | IO-number redirects and here-doc behavior are strongly exercised. |
| `2.8 Exit Status and Errors` | Covered (Partial) | `tests/busybox/ash_test/ash-misc/exitcode_EACCES.tests`, `tests/busybox/ash_test/ash-misc/exitcode_ENOENT.tests`, `tests/busybox/ash_test/ash-misc/pipefail.tests` | `tests/oil/oils-master/spec/command_.test.sh` (`Permission denied`, `Not a dir`, `Name too long`) | Status mapping is covered; diagnostic formatting still implementation-specific in corners. |
| `2.9 Shell Commands` | Covered (Partial) | `tests/busybox/ash_test/ash-misc/compound.tests`, `tests/busybox/ash_test/ash-misc/func_compound1.tests`, `tests/busybox/ash_test/ash-misc/while_in_subshell.tests` | `tests/oil/oils-master/spec/if_.test.sh`, `tests/oil/oils-master/spec/case_.test.sh`, `tests/oil/oils-master/spec/loop.test.sh` | Simple + compound command execution paths are well covered. |
| `2.10 Shell Grammar` | Covered (Partial) | `tests/busybox/ash_test/ash-parsing/nodone1.tests`, `tests/busybox/ash_test/ash-parsing/noeol3.tests`, `tests/busybox/ash_test/ash-parsing/group2.tests` | `tests/oil/oils-master/spec/shell-grammar.test.sh` (38 passing cases in current subset run) | Grammar breadth is high; not a formal completeness proof. |
| `2.11 Signals and Errors` | Covered (Partial) | `tests/busybox/ash_test/ash-signals/signal9.tests`, `tests/busybox/ash_test/ash-signals/return_in_trap1.tests`, `tests/busybox/ash_test/ash-signals/sigquit_exec.tests` | N/A in current Oil subset selection | BusyBox signal/trap corpus passes. |
| `2.12 Shell Execution Environment` | Covered (Partial) | `tests/busybox/ash_test/ash-standalone/nofork_env.tests`, `tests/busybox/ash_test/ash-standalone/noexec_gets_no_env.tests`, `tests/busybox/ash_test/ash-misc/source_argv_and_shift.tests` | `tests/oil/oils-master/spec/command_.test.sh` (`External programs don't have _OVM in environment`) | Environment/exec behavior is covered for tested scenarios; threaded runtime divergence remains documented. |
| `2.13 Shell Variables` | Covered (Partial) | `tests/busybox/ash_test/ash-vars/readonly1.tests`, `tests/busybox/ash_test/ash-vars/unset.tests`, `tests/busybox/ash_test/ash-vars/var_LINENO3.tests` | `tests/oil/oils-master/spec/var-op-test.test.sh` (set/unset/null branches) | Variable lifecycle behavior is heavily exercised. |
| `2.14 Special Built-In Utilities` | Covered (Partial) | `tests/busybox/ash_test/ash-getopts/getopt_simple.tests`, `tests/busybox/ash_test/ash-misc/eval2.tests`, `tests/busybox/ash_test/ash-misc/command2.tests`, `tests/busybox/ash_test/ash-vars/readonly0.tests` | `tests/oil/oils-master/spec/sh-options.test.sh`, `tests/oil/oils-master/spec/command-parsing.test.sh` | Special builtins in scope are covered; full POSIX option surface remains partial. |
| `2.15 Shell Grammar Lexical Conventions` | Covered (Partial) | `tests/busybox/ash_test/ash-parsing/bkslash_newline4.tests`, `tests/busybox/ash_test/ash-parsing/comment2.tests`, `tests/busybox/ash_test/ash-quoting/bkslash_case2.tests` | `tests/oil/oils-master/spec/shell-grammar.test.sh` | Practical lexical convention behavior is covered by parser-focused suites. |

## Non-claim / remaining verification work

These are the main gaps before claiming strict formal POSIX conformance:

- Full startup-option parity and behavior matrix from `ash` man-page synopsis.
- Requirement-level trace expansion from section-level to normative “shall” granularity.
- Additional independent corpora for job-control and interactive mode semantics.
- Continued documentation/justification for threaded-runtime divergences from fork-first shells.

## Next verification actions

1. Expand this table from section-level to requirement-level (“shall” granularity) for high-risk areas:
   expansions, redirections, traps/signals, error diagnostics.
2. Add explicit case IDs or line anchors from Oil spec files where practical.
3. Keep this file updated in lockstep with parser/runtime changes and each conformance commit.

Requirement-level companion:

- `docs/posix-shall-trace.md`
