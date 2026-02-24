# POSIX Trace Table (Issue 8, XCU Chapter 2)

Date: 2026-02-24

References:

- POSIX Shell Command Language: `https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/V3_chap02.html`
- POSIX rationale (XCU C.2): `https://pubs.opengroup.org/onlinepubs/9699919799/xrat/V4_xcu_chap02.html`
- BusyBox ash corpus currently run by mctash: `tests/busybox/ash_test`

Latest run evidence (configured timeout window):

- `ok=343 fail=0 skip=0` (functional failures in covered modules: none)
- `ash-z_slow/many_ifs.tests` may exceed timeout budget depending on run timeout.

Legend:

- `Covered`: exercised by current automated corpus.
- `Partial`: some behavior covered, not a full normative proof.
- `Gap`: known not fully covered/verified yet.

## POSIX section mapping

| POSIX section | Status | Primary test modules/files | Notes |
|---|---|---|---|
| `2.2 Quoting` | Covered (Partial) | `ash-quoting/*`, `ash-parsing/quote*.tests` | Broadly exercised, but not exhaustive for all deep nesting combinations. |
| `2.3 Token Recognition` | Covered (Partial) | `ash-parsing/*`, `ash-alias/*` | Lexer/parser behavior covered via grammar and alias tests. |
| `2.4 Reserved Words` | Covered (Partial) | `ash-parsing/groups_and_keywords*.tests`, `ash-misc/if*`, `ash-misc/for*`, `ash-misc/while*` | Core reserved-word contexts covered. |
| `2.5 Parameters and Variables` | Covered (Partial) | `ash-vars/*`, `ash-misc/assignment*.tests` | Special parameters and parameter ops exercised heavily. |
| `2.6 Word Expansions` | Covered (Partial) | `ash-vars/*`, `ash-glob/*`, `ash-psubst/*`, `ash-arith/*`, `ash-quoting/*` | Expansion order coverage is strong in corpus; not yet formally complete against spec text. |
| `2.7 Redirection` | Covered (Partial) | `ash-redir/*`, `ash-heredoc/*` | Includes IO-number redirects and here-doc variants used by BusyBox ash tests. |
| `2.8 Exit Status and Errors` | Covered (Partial) | `ash-misc/exitcode*.tests`, `ash-signals/*` | Return code paths broadly tested; diagnostic text still implementation-specific in some corners. |
| `2.9 Shell Commands` | Covered (Partial) | `ash-misc/*`, `ash-parsing/*`, `ash-signals/*` | Simple/compound commands and function execution covered by corpus. |
| `2.10 Shell Grammar` | Covered (Partial) | `ash-parsing/*`, plus all module parse/exec | Effective grammar coverage is broad, but not a formal grammar-completeness proof. |
| `2.11 Signals and Errors` | Covered (Partial) | `ash-signals/*` | Signal/trap behavior now passing BusyBox signal suite. |
| `2.12 Shell Execution Environment` | Covered (Partial) | `ash-misc/*`, `ash-signals/*`, `ash-standalone/*` | Environment/process behavior covered for tested scenarios; threaded runtime remains a design divergence from fork-first shells. |
| `2.13 Shell Variables` | Covered (Partial) | `ash-vars/*` | Major variable behaviors covered. |
| `2.14 Special Built-In Utilities` | Covered (Partial) | `ash-misc/*`, `ash-vars/*`, `ash-signals/*`, `ash-getopts/*` | Tested builtins pass corpus behavior; full POSIX option-surface parity still tracked separately. |
| `2.15 Shell Grammar Lexical Conventions` | Covered (Partial) | `ash-parsing/*`, `ash-quoting/*` | Practical coverage present through parser and quoting suites. |

## Non-claim / remaining verification work

These are the main gaps before claiming strict formal POSIX conformance:

- Full startup-option parity and behavior matrix from `ash` man-page synopsis.
- Independent cross-validation with Oil POSIX spec subset (in addition to BusyBox ash corpus).
- Explicit trace rows for every normative “shall” that is implementation-relevant.
- Documented and justified divergences due to threaded runtime model vs classic fork/job-control internals.

## Next verification actions

1. Add Oil POSIX subset harness and cross-link each new test group back to this table.
2. Expand this table from section-level to requirement-level (“shall” granularity) for high-risk areas:
   expansions, redirections, traps/signals, error diagnostics.
3. Keep this file updated in lockstep with parser/runtime changes.
