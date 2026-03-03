# Closure Board A2: Zero Guarded Fallback

Date: 2026-03-03
Status: proposed
Goal: eliminate the remaining intentional guarded legacy fallbacks in ASDL execution paths.

## Scope

In scope:
- ASDL word/assignment/case expansion paths that still route to legacy fallback by guard.
- Native handling of process substitution in ASDL word expansion.
- Quote/escape-sensitive assignment and case-word behavior currently blocked by safety gates.

Out of scope (A2):
- interactive/job-control/editor parity (B)
- broader bash feature expansion beyond current operator surface (C)

## Rules

- Atomic items only (`open` -> `done`).
- No scope expansion inside an item; new scope becomes a new item.
- Every item needs explicit passing evidence.

## Items

| ID | Item | Status | Completion Criteria | Evidence Gate |
|---|---|---|---|---|
| A2-001 | Native process substitution in ASDL argv expansion | done | `word_part` expansion path can produce `<(...)` / `>(...)` results natively without per-word legacy fallback. | `tests/regressions/run.sh` (`process_subst_*`), `tests/diff/cases/man-ash-thread-pipeline-fd.sh`, `tests/diff/cases/man-ash-thread-pipeline-cwd.sh` |
| A2-002 | Remove quote/escape literal guard in ASDL argv safety path | done | `command.Simple` words with quote/escape-sensitive literals no longer require legacy path for correctness. | `tests/regressions/run.sh` (`asdl_argv_*`, `quoted argv guardrails`), `tests/diff/cases/man-ash-word-nesting.sh`, `tests/diff/cases/man-ash-word-nesting-deep.sh` |
| A2-003 | Native assignment-word quote-removal parity | done | Assignment RHS expansion with quotes/backslashes is native ASDL for in-scope forms; no fallback to `_expand_assignment_word(_asdl_word_to_text(...))` in ASDL assignment execution. | `tests/regressions/run.sh` (`asdl_exec_shassignment_*`), BusyBox `ash-vars` + `ash-quoting` modules |
| A2-004 | Native handling of special params in ASDL assignment context | done | ASDL assignment expansion correctly handles special params (`$@`, `$*`, `$1...`) where currently guarded. | New `tests/diff/cases/bash-compat-param-assignment-specials.sh` + regressions |
| A2-005 | Remove case-word fallback for quote/escape-sensitive pattern forms | done | Case value/pattern expansion stays native ASDL while preserving literal-vs-pattern semantics for quoted forms. | `tests/regressions/run.sh` (`asdl_exec_case_*`), `tests/diff/cases/man-ash-prefix-suffix.sh` |
| A2-006 | Eliminate remaining ASDL word fallback helper usage in simple argv path | open | `_expand_asdl_word_fields_or_legacy()` is removed or reduced to unreachable in normal ASDL command path. | grep check + `tests/regressions/run.sh` + `make diff-parity-matrix` |
| A2-007 | Add fallback-audit regression guard | open | Add regression script/check that fails if new guarded fallback branches are introduced in ASDL expansion path without explicit board item. | New regression case + CI command in docs |
| A2-008 | Full A2 gates pass | open | All A2-targeted tests and global parity gates pass after A2-001..A2-007. | `make diff-parity-matrix`, `make compat-posix-bash-strict`, `tests/regressions/run.sh` |

## Suggested Execution Order

1. A2-001
2. A2-003
3. A2-002
4. A2-005
5. A2-004
6. A2-006
7. A2-007
8. A2-008

## Remaining Count

- Open: 3
- Done: 5
