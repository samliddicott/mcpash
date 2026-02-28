# POSIX 2.10 Grammar Production Checklist

Date: 2026-02-28

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
| reserved-word contextualization | parser context + `parse_command()` dispatch | Covered | `tests/busybox/ash_test/ash-parsing/groups_and_keywords*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh`, `tests/diff/cases/man-ash-grammar-reserved.sh`, `tests/regressions/run.sh` (`reserved_word_*`) | Core ambiguity contexts now have both corpus and local evidence. |
| grammar rejection paths (invalid productions) | all parse entry points (error exits) | Covered | `tests/busybox/ash_test/ash-parsing/nodone*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` (`Invalid token`), `tests/diff/cases/man-ash-grammar-negative.sh`, `tests/regressions/run.sh` (`parser_*`) | Status-based rejection behavior is covered in corpora and local differential/regression suites. |

## POSIX 2.10 Production-to-Test Mapping

This section is the concrete closure board for grammar productions we rely on for ash parity.

| POSIX production (2.10 family) | Parser path(s) | Status | Primary evidence | Differential anchor |
|---|---|---|---|---|
| `program` / complete command stream | `parse_next()`, `parse_list()` | Covered | `tests/busybox/ash_test/ash-parsing/noeol*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` | `tests/diff/cases/man-ash-logic.sh` |
| `complete_command` / separators (`;`, `&`, newline) | `parse_list()`, `parse_compound_list()` | Covered | `tests/busybox/ash_test/ash-parsing/and_or_and_backgrounding.tests` | `tests/diff/cases/man-ash-logic.sh` |
| `and_or` lists (`&&`, `||`) | `parse_and_or()` | Covered | `tests/busybox/ash_test/ash-misc/and-or.tests` | `tests/diff/cases/man-ash-logic.sh` |
| `pipeline` with optional leading `!` | `parse_pipeline()` | Covered | `tests/busybox/ash_test/ash-parsing/negate.tests`, `tests/oil/oils-master/spec/pipeline.test.sh` | `tests/diff/cases/man-ash-logic.sh` |
| `simple_command` (assignment words, words, redirects) | `parse_command()` | Covered | `tests/busybox/ash_test/ash-misc/assignment*.tests`, `tests/busybox/ash_test/ash-redir/redir*.tests` | `tests/diff/cases/man-ash-set.sh`, `tests/diff/cases/man-ash-redir.sh` |
| `cmd_prefix`/`cmd_suffix` redirect+word interleave | `parse_command()` | Covered | `tests/busybox/ash_test/ash-redir/redir_exec*.tests`, `tests/oil/oils-master/spec/command-parsing.test.sh`, `tests/diff/cases/man-ash-prefix-suffix.sh` | `tests/diff/cases/man-ash-redir.sh`, `tests/diff/cases/man-ash-prefix-suffix.sh` |
| `redirect_list` and IO-number redirects | `parse_command()` + redir parser | Covered | `tests/busybox/ash_test/ash-redir/redir_to_bad_fd*.tests`, `tests/oil/oils-master/spec/redirect.test.sh` | `tests/diff/cases/man-ash-redir.sh` |
| `io_here` and heredoc attachment/order | heredoc queueing in parser | Covered | `tests/busybox/ash_test/ash-heredoc/heredoc*.tests`, `tests/oil/oils-master/spec/posix.test.sh` (`Multiple here docs on one line`) | `tests/diff/cases/man-ash-redir.sh` |
| `compound_command` brace group | `parse_group()` | Covered | `tests/busybox/ash_test/ash-parsing/group*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` | `tests/diff/cases/man-ash-logic.sh` |
| `subshell` | `parse_subshell()` | Covered | `tests/busybox/ash_test/ash-misc/while_in_subshell.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` | `tests/diff/cases/man-ash-logic.sh` |
| `for_clause` | `parse_for()` | Covered | `tests/busybox/ash_test/ash-misc/for*.tests`, `tests/oil/oils-master/spec/loop.test.sh` | `tests/diff/cases/man-ash-logic.sh` |
| `case_clause` / `case_item_ns` | `parse_case()` | Covered | `tests/busybox/ash_test/ash-misc/case1.tests`, `tests/oil/oils-master/spec/case_.test.sh` | `tests/diff/cases/man-ash-logic.sh` |
| `if_clause` / `elif` / `else` | `parse_if()` | Covered | `tests/busybox/ash_test/ash-misc/elif*.tests`, `tests/oil/oils-master/spec/if_.test.sh` | `tests/diff/cases/man-ash-logic.sh` |
| `while_clause` / `until_clause` | `parse_while()` | Covered | `tests/busybox/ash_test/ash-misc/while*.tests`, `tests/busybox/ash_test/ash-misc/until1.tests`, `tests/oil/oils-master/spec/loop.test.sh` | `tests/diff/cases/man-ash-logic.sh` |
| `function_definition` | `parse_function_def()` | Covered | `tests/busybox/ash_test/ash-misc/func*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` (`Function def`) | `tests/diff/cases/man-ash-type.sh` |
| reserved word disambiguation by parser context | parser context + command dispatch | Covered | `tests/busybox/ash_test/ash-parsing/groups_and_keywords*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh`, `tests/diff/cases/man-ash-grammar-reserved.sh`, `tests/regressions/run.sh` (`reserved_word_*`) | `tests/diff/cases/man-ash-logic.sh`, `tests/diff/cases/man-ash-grammar-reserved.sh` |
| invalid productions are rejected safely | all parse entry points | Covered | `tests/busybox/ash_test/ash-parsing/nodone*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` (`Invalid token`), `tests/diff/cases/man-ash-grammar-negative.sh`, `tests/regressions/run.sh` (`parser_*`) | `tests/diff/cases/man-ash-redir.sh`, `tests/diff/cases/man-ash-grammar-negative.sh` |

## Production Gaps to Close Next

1. Expand negative parse coverage with additional operator/terminator permutations beyond current matrix.
2. Add stricter diagnostic-text parity checks where behaviorally safe across ash variants.
3. Continue parser checklist linking to ASDL coverage outputs for incremental completion reporting.

## Partial-Row Closure Map

Each `Partial` row now has an explicit next artifact target.

| Partial row | Current evidence | Next test artifact (explicit) | Target status |
|---|---|---|---|
| Grammar families: `reserved-word contextualization` | `tests/busybox/ash_test/ash-parsing/groups_and_keywords*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` | Completed: `tests/regressions/run.sh` reserved-word rows + `tests/diff/cases/man-ash-grammar-reserved.sh` | Covered |
| Grammar families: `grammar rejection paths` | `tests/busybox/ash_test/ash-parsing/nodone*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` | Completed: `tests/diff/cases/man-ash-grammar-negative.sh` + `tests/regressions/run.sh` parser rows | Covered |
| Production map: `cmd_prefix/cmd_suffix` interleave | `tests/busybox/ash_test/ash-redir/redir_exec*.tests`, `tests/oil/oils-master/spec/command-parsing.test.sh` | Completed: `tests/diff/cases/man-ash-prefix-suffix.sh` matrix | Covered |
| Production map: `reserved word disambiguation by parser context` | busybox/oil parsing suites + `tests/diff/cases/man-ash-logic.sh` | Completed: `tests/regressions/run.sh` + `tests/diff/cases/man-ash-grammar-reserved.sh` | Covered |
| Production map: `invalid productions are rejected safely` | busybox/oil rejection suites + `tests/diff/cases/man-ash-redir.sh` | Completed: `tests/diff/cases/man-ash-grammar-negative.sh` status matrix | Covered |
| Word sub-checklist: braced parameter operators | busybox/oil var-op suites | Completed: `tests/diff/cases/man-ash-var-ops.sh` (core operator matrix) | Partial |
| Word sub-checklist: deep nested quote/substitution combinations | busybox/oil quoting suites | Completed: `tests/diff/cases/man-ash-word-nesting.sh` (nested quote/subst matrix) | Partial |

Execution order for closure:

1. `man-ash-prefix-suffix.sh`
2. `man-ash-grammar-negative.sh`
3. `man-ash-grammar-reserved.sh`
4. `man-ash-var-ops.sh`
5. `man-ash-word-nesting.sh`

## Outstanding Parser-Checklist Work

1. Expand the word-level sub-checklist above to include explicit parser/expander line anchors and negative-case rows.
2. Extend explicit negative parse tests for ambiguous boundaries (reserved words vs literals) beyond the current local regression set.
3. Extend parser checklist links from ASDL mapping coverage into per-variant action items.

ASDL linkback automation status:

- `research/parser/asdl_coverage.py` now emits checklist links in `research/parser/asdl_coverage_report.md`.

## Word-Level Grammar Sub-Checklist

Word parsing is split across:

- `src/mctash/word_parser.py` (LST-oriented word structure parser)
- `src/mctash/expand.py` (`parse_word_parts()` and expansion-time parsing)

| Word-level grammar area | Primary function(s) | Code anchors | Status | Positive evidence | Negative-case evidence | Notes |
|---|---|---|---|---|---|---|
| single quotes, double quotes, escaped characters | `word_parser._parse_parts()`, `expand.parse_word_parts()` | `src/mctash/word_parser.py:73`, `src/mctash/word_parser.py:163`, `src/mctash/expand.py:37` | Covered | `tests/busybox/ash_test/ash-parsing/quote*.tests`, `tests/busybox/ash_test/ash-quoting/squote_*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` (`Command with args`) | `tests/busybox/ash_test/ash-parsing/noeol3.tests` (unterminated quote rejection) | Core quote tokenization and preservation behavior are exercised. |
| parameter expansion tokens (`$x`, `$1`, `${...}` basic forms) | `word_parser._parse_param()`, `word_parser._parse_braced_var()`, `expand._parse_dollar()` | `src/mctash/word_parser.py:29`, `src/mctash/word_parser.py:278`, `src/mctash/expand.py:247`, `src/mctash/runtime.py:2213` | Covered | `tests/busybox/ash_test/ash-vars/param_expand_*.tests`, `tests/oil/oils-master/spec/var-op-test.test.sh`, `tests/oil/oils-master/spec/var-sub.test.sh` | `tests/busybox/ash_test/ash-vars/param_expand_indicate_error.tests` | Includes unset/null operators and error branches in execution path. |
| braced parameter operators (`:-`, `:=`, `:+`, `:?`, `#`, `##`, `%`, `%%`, substring) | `word_parser._split_braced_var()`, `expand._split_braced()`, `runtime._expand_braced_param()` | `src/mctash/word_parser.py:294`, `src/mctash/expand.py:501`, `src/mctash/runtime.py:2242` | Partial | `tests/busybox/ash_test/ash-vars/var-pattern-replacement-in-parameter-expansion-*.tests`, `tests/oil/oils-master/spec/var-op-strip.test.sh`, `tests/oil/oils-master/spec/var-op-test.test.sh`, `tests/diff/cases/man-ash-var-ops.sh` | `tests/busybox/ash_test/ash-vars/var_bash_repl_unterminated.tests`, `tests/busybox/ash_test/ash-vars/param_expand_bash_substring.tests` | Core operator matrix is covered; exhaustive exotic combinations still partial. |
| command substitution `$()` and backticks | `word_parser._parse_command_sub()`, `expand._parse_dollar()` / backtick parsing | `src/mctash/word_parser.py:232`, `src/mctash/expand.py:247` | Covered | `tests/busybox/ash_test/ash-psubst/tick*.tests`, `tests/oil/oils-master/spec/smoke.test.sh` (`command sub`) | `tests/busybox/ash_test/ash-misc/nulltick1.tests` | Includes nested/common command-sub forms used in suites. |
| arithmetic substitution `$((...))` | `word_parser._parse_arith_sub()`, `expand._parse_dollar()` | `src/mctash/word_parser.py:257`, `src/mctash/expand.py:247` | Covered | `tests/busybox/ash_test/ash-arith/*.tests`, `tests/oil/oils-master/spec/posix.test.sh` (`Arithmetic expansion`) | `tests/busybox/ash_test/ash-quoting/negative_arith.tests` | Arithmetic expression surfaces are broadly exercised. |
| quote-aware field splitting and glob handoff | `expand.parse_word_parts()`, `expand.expand_word()` | `src/mctash/expand.py:37`, `src/mctash/expand.py:553` | Covered | `tests/busybox/ash_test/ash-vars/var_wordsplit_ifs*.tests`, `tests/busybox/ash_test/ash-glob/glob*.tests`, `tests/oil/oils-master/spec/word-split.test.sh` | `tests/busybox/ash_test/ash-z_slow/many_ifs.tests` | Includes `IFS` and quote-preservation interactions in regression suite. |
| deep nested quote/substitution combinations | both paths above | `src/mctash/word_parser.py:73`, `src/mctash/word_parser.py:232`, `src/mctash/expand.py:553` | Partial | `tests/busybox/ash_test/ash-quoting/*`, `tests/oil/oils-master/spec/shell-grammar.test.sh`, `tests/diff/cases/man-ash-word-nesting.sh` | `tests/busybox/ash_test/ash-parsing/groups_and_keywords2.tests` | Strong practical coverage, but no exhaustive combinatorial matrix yet. |
