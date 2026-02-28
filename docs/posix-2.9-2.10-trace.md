# POSIX 2.9/2.10 Requirement Trace (Command + Grammar)

Date: 2026-02-28

Purpose:

- Provide a strict, reviewable map from POSIX 2.9/2.10 requirement families to executable tests.
- Keep ASDL alignment visible while grounding each row in at least one concrete differential case.

References:

- POSIX Shell Command Language (Issue 8): `https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/V3_chap02.html`
- POSIX rationale (XCU C.2): `https://pubs.opengroup.org/onlinepubs/9699919799/xrat/V4_xcu_chap02.html`
- OSH ASDL anchors: `src/syntax/osh/syntax.asdl`
- Parser/LST mapper: `src/mctash/parser.py`, `src/mctash/asdl_map.py`

Legend:

- `Verified`: covered by corpus + differential evidence listed.
- `Partial`: exercised, but additional corner matrices still needed.

## 2.9 Shell Commands

| POSIX 2.9 requirement family | ASDL anchor | Status | Differential evidence | Corpus evidence |
|---|---|---|---|---|
| Simple command ordering (assignments, words, redirs, command lookup) | `command.Simple`, `assign_pair`, `redir` | Verified | `tests/diff/cases/man-ash-prefix-suffix.sh`, `tests/diff/cases/man-ash-set.sh`, `tests/diff/cases/man-ash-redir.sh` | `tests/busybox/ash_test/ash-misc/assignment*.tests`, `tests/oil/oils-master/spec/command-parsing.test.sh` |
| Lists and and/or short-circuit semantics | `command.CommandList`, `command.AndOr` | Verified | `tests/diff/cases/man-ash-logic.sh` | `tests/busybox/ash_test/ash-misc/and-or.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` |
| Pipelines and negation (`!`) | `command.Pipeline` | Verified | `tests/diff/cases/man-ash-logic.sh` | `tests/busybox/ash_test/ash-parsing/negate.tests`, `tests/oil/oils-master/spec/pipeline.test.sh` |
| Compound commands (`if`, `case`, loops, group/subshell) | `command.If`, `command.Case`, `command.WhileUntil`, `command.ForEach`, `command.BraceGroup`, `command.Subshell` | Verified | `tests/diff/cases/man-ash-logic.sh`, `tests/diff/cases/man-ash-grammar-reserved.sh` | `tests/busybox/ash_test/ash-misc/if*.tests`, `tests/busybox/ash_test/ash-misc/case1.tests`, `tests/busybox/ash_test/ash-misc/while*.tests`, `tests/oil/oils-master/spec/if_.test.sh`, `tests/oil/oils-master/spec/case_.test.sh`, `tests/oil/oils-master/spec/loop.test.sh` |
| Function definitions and call semantics | `command.ShFunction` | Verified | `tests/diff/cases/man-ash-function-scope.sh`, `tests/diff/cases/man-ash-type.sh` | `tests/busybox/ash_test/ash-misc/func*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` |
| Special builtins integrated into command semantics | `command.Simple` (builtin dispatch path) | Partial | `tests/diff/cases/man-ash-set.sh`, `tests/diff/cases/man-ash-env.sh`, `tests/diff/cases/man-ash-eval-exec.sh`, `tests/diff/cases/man-ash-getopts.sh`, `tests/diff/cases/man-ash-type-options.sh` | `tests/busybox/ash_test/ash-misc/eval*.tests`, `tests/busybox/ash_test/ash-misc/exec.tests`, `tests/busybox/ash_test/ash-getopts/*.tests` |

## 2.10 Shell Grammar

| POSIX 2.10 requirement family | Parser/LST path | ASDL anchor | Status | Differential evidence | Corpus evidence |
|---|---|---|---|---|---|
| Valid top-level grammar acceptance (complete commands, separators) | `parse_next()`, `parse_list()`, `LstListNode` | `command.CommandList` | Verified | `tests/diff/cases/man-ash-logic.sh` | `tests/busybox/ash_test/ash-parsing/noeol*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` |
| Reserved-word contextual recognition | parser context + `parse_command()` | command-node family selected by keyword | Verified | `tests/diff/cases/man-ash-grammar-reserved.sh` | `tests/busybox/ash_test/ash-parsing/groups_and_keywords*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` |
| Prefix/suffix interleave (`cmd_prefix`, `cmd_suffix`) | `parse_command()` -> `LstSimpleCommand` | `command.Simple` fields | Verified | `tests/diff/cases/man-ash-prefix-suffix.sh`, `tests/diff/cases/man-ash-redir.sh` | `tests/busybox/ash_test/ash-redir/redir_exec*.tests`, `tests/oil/oils-master/spec/command-parsing.test.sh` |
| IO-number redirections and heredoc attachment order | `parse_command()` + heredoc queue | `redir` variants | Verified | `tests/diff/cases/man-ash-redir.sh`, `tests/diff/cases/man-ash-heredoc-edges.sh` | `tests/busybox/ash_test/ash-redir/redir_to_bad_fd*.tests`, `tests/busybox/ash_test/ash-heredoc/heredoc*.tests`, `tests/oil/oils-master/spec/redirect.test.sh` |
| Invalid grammar rejection (non-zero status, no unintended execution) | parse error exits | N/A (rejected pre-AST) | Verified | `tests/diff/cases/man-ash-grammar-negative.sh` | `tests/busybox/ash_test/ash-parsing/nodone*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` |
| Deep word/substitution grammar nesting | `word_parser.py`, `expand.py` | `word_t` family | Partial | `tests/diff/cases/man-ash-word-nesting.sh`, `tests/diff/cases/man-ash-word-nesting-deep.sh` | `tests/busybox/ash_test/ash-quoting/*.tests`, `tests/oil/oils-master/spec/shell-grammar.test.sh` |

## POSIX vs ASDL Conflict Register

- No current normative conflict blocks ash-scope 2.9/2.10 mapping.
- If parser behavior must diverge from POSIX text to preserve OSH ASDL shape, add an explicit row here with:
  - requirement citation,
  - ASDL node constraint,
  - chosen behavior,
  - required approval state.
