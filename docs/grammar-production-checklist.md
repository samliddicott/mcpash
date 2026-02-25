# POSIX 2.10 Grammar Production Checklist

Date: 2026-02-25

Purpose:

- Track parser completeness against POSIX shell grammar at production-family level.
- Tie each production family to concrete parser entry points and test evidence.
- Identify remaining parser gaps for milestone planning.

References:

- POSIX Shell Command Language (Issue 8): `https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/V3_chap02.html`
- Parser implementation: `src/mctash/parser.py`
- BusyBox ash tests: `tests/busybox/ash_test`
- Oil shell grammar tests: `tests/oil/oils-master/spec/shell-grammar.test.sh`

Legend:

- `Covered`: parser has explicit production handling + passing evidence.
- `Partial`: parser handles common forms, but some productions/variants are not fully covered.
- `Gap`: missing or intentionally out of scope right now.

## Grammar Families

| POSIX grammar family (2.10) | Parser entry point(s) | Status | Test evidence | Notes |
|---|---|---|---|---|
| complete commands / command lists | `parse_next()`, `parse_list()`, `parse_compound_list()` | Covered | `tests/busybox/ash_test/ash-parsing/noeol*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` (`Simple command`, `a & b`, `a && b`) | Includes `;`, newline, and background separators used by current corpora. |
| and/or lists | `parse_and_or()` | Covered | `tests/busybox/ash_test/ash-misc/and-or.tests`, `tests/busybox/ash_test/ash-parsing/and_or_and_backgrounding.tests` | Short-circuit chain parsing and execution are exercised. |
| pipelines (including leading `!`) | `parse_pipeline()` | Covered | `tests/busybox/ash_test/ash-parsing/negate.tests`, `tests/oil/oils-master/spec/pipeline.test.sh` | Known semantic delta retained for last pipeline process behavior (ash-vs-OSH expectation). |
| simple command (assignments, words, redirects) | `parse_command()` | Covered | `tests/busybox/ash_test/ash-misc/assignment*.tests`, `tests/busybox/ash_test/ash-redir/redir*.tests`, `tests/oil/oils-master/spec/command-parsing.test.sh` | Prefix assignments and redirect attachment are covered. |
| redirection forms and here-doc tokens | `parse_command()` + heredoc queueing in parser | Covered | `tests/busybox/ash_test/ash-redir/*`, `tests/busybox/ash_test/ash-heredoc/*`, `tests/oil/oils-master/spec/redirect.test.sh` | Parser-level here-doc ordering is validated by multi-here-doc cases. |
| compound command: brace group | `parse_group()` | Covered | `tests/busybox/ash_test/ash-parsing/group*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` (`Brace group`) | Includes oneline and multiline forms. |
| compound command: subshell | `parse_subshell()` | Covered | `tests/busybox/ash_test/ash-misc/while_in_subshell.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` (`Subshell`) | Subshell parse path is stable in current suites. |
| for clause | `parse_for()` | Covered | `tests/busybox/ash_test/ash-misc/for*.tests`, `tests/oil/oils-master/spec/loop.test.sh` | Includes empty/explicit `in` patterns used in corpora. |
| case clause / case item list | `parse_case()` | Covered | `tests/busybox/ash_test/ash-misc/case1.tests`, `tests/oil/oils-master/spec/case_.test.sh`, `tests/oil/oils-master/spec/shell-grammar.test.sh` (`Case ...`) | Includes optional trailing `;;` variants covered by Oil grammar tests. |
| if / elif / else / fi | `parse_if()` | Covered | `tests/busybox/ash_test/ash-misc/elif*.tests`, `tests/oil/oils-master/spec/if_.test.sh` | Same-line and multiline `then` forms are exercised. |
| while / until | `parse_while()` | Covered | `tests/busybox/ash_test/ash-misc/while*.tests`, `tests/busybox/ash_test/ash-misc/until1.tests`, `tests/oil/oils-master/spec/loop.test.sh` | Includes loop condition/body parse combinations in current suites. |
| function definition command | `parse_function_def()` | Covered | `tests/busybox/ash_test/ash-misc/func*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` (`Function def`) | Function parse and body attachment are covered. |
| reserved-word contextualization | parser context + `parse_command()` dispatch | Partial | `tests/busybox/ash_test/ash-parsing/groups_and_keywords*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` | Common contexts are covered; exhaustive reserved-word ambiguity matrix remains open. |
| grammar rejection paths (invalid productions) | all parse entry points (error exits) | Partial | `tests/busybox/ash_test/ash-parsing/nodone*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` (`Invalid token`) | Rejections are covered; exact diagnostic text parity is not a strict claim yet. |

## Outstanding Parser-Checklist Work

1. Add a production-by-production sub-checklist for word-level grammar interactions (quotes, command substitution nesting, arithmetic contexts) with parse-location anchors.
2. Add explicit negative parse tests for ambiguous boundaries (reserved words vs literals in more contexts).
3. Add parser checklist links to ASDL mapping coverage (`research/parser/asdl_coverage_report.md`) so parse completeness and ASDL completeness advance together.
