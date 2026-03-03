# Closure Board (To Zero)

Date: 2026-03-03
Mode: atomic items only (`open` -> `done`)

## Rules

- Every item has explicit pass criteria.
- An item is removed/marked `done` only when criteria pass.
- Scope cannot expand mid-item; any expansion becomes a new item.

## Items

| ID | Item | Status | Evidence / Gate |
|---|---|---|---|
| ASDL-001 | Remove global argv fallback in `command.Simple` | done | `src/mctash/runtime.py` (`_expand_asdl_simple_argv` now per-word native/legacy). |
| ASDL-002 | Remove legacy fallback in `ForEach explicit in` expansion | done | `src/mctash/runtime.py` (`command.ForEach` explicit-in uses per-word helper). |
| ASDL-003 | Native case-word/pattern expansion for safe forms only | done | `src/mctash/runtime.py` (`_asdl_word_can_expand_case_natively_safe` + native scalar expansion path). |
| ASDL-004 | Assignment RHS native path covers braced trim/replace/substr safe-literal args | done | `src/mctash/runtime.py` (`_asdl_rhs_assignment_can_expand_natively`). |
| ASDL-005 | Parser preserves exact source slices for compound assignment RHS | done | `src/mctash/parser.py`, `tests/diff/cases/bash-compat-parse-compound-assignment.sh`. |
| IDX-001 | Indexed subscript arithmetic eval parity (read) | done | `tests/diff/cases/bash-compat-subscript-eval-indexed*.sh`. |
| IDX-002 | Indexed subscript arithmetic eval parity (assign) | done | `tests/diff/cases/bash-compat-subscript-eval-indexed-assign.sh`. |
| IDX-003 | Indexed subscript arithmetic eval parity (unset) | done | `tests/diff/cases/bash-compat-subscript-eval-indexed-unset.sh`. |
| IDX-004 | Indexed invalid-subscript status parity | done | `tests/diff/cases/bash-compat-subscript-eval-indexed-errors.sh`. |
| ASSOC-001 | Assoc key string-mode parity for quoted/expanded keys | done | `tests/diff/cases/bash-compat-subscript-eval-assoc.sh`, `tests/diff/cases/bash-compat-subscript-eval-assoc-quoted.sh`. |
| PARAM-001 | Positional parameter operator matrix complete | done | `tests/diff/cases/bash-compat-param-positional-extended.sh`. |
| PARAM-002 | Collection operator matrix complete (array + assoc) | done | `tests/diff/cases/bash-compat-param-array-hash-ops.sh`, `tests/diff/cases/bash-compat-param-array-hash-extended.sh`, `tests/diff/cases/bash-compat-param-array-contexts.sh`. |
| PARAM-003 | Collection slicing semantics parity (`[@]:off:len`, `[*]:off:len`) | done | `tests/diff/cases/bash-compat-param-collection-slicing.sh`. |
| DOC-001 | Trace docs updated to link new atomic tests | done | `docs/posix-shall-trace.md`, `docs/gap-board.md` updated with indexed assign/unset and slicing case links. |
| GATE-001 | Full gate clean | done | `make diff-parity-matrix`, `make compat-posix-bash-strict`, `tests/regressions/run.sh` (all passing on HEAD). |

## Remaining Count

- Open: 0
- Done: 15
