# ASDL Backlog Slices

Date: 2026-02-25

Purpose:

- Turn ASDL coverage gaps into small implementation slices with test evidence.
- Keep ash-parity priorities first, while preserving OSH-ASDL alignment.

Primary input:

- `research/parser/asdl_coverage_report.md`

## Slice Strategy

1. Prefer slices that improve ash/POSIX behavior directly.
2. Keep each slice small enough for one implementation commit + one test commit.
3. Update `research/parser/asdl_coverage.py` implemented sets only when behavior is evidenced by tests.

## Current Slice Board

| Slice | ASDL area | Status | Evidence | Notes |
|---|---|---|---|---|
| S1 | `assign_op` (`Equal`, `PlusEqual`) | Done | `tests/regressions/run.sh` (`assign_plus_equal`), BusyBox assignment suite | Coverage report now marks both variants implemented. |
| S2 | `command.DoGroup` alignment | Done | `tests/busybox/ash_test/ash-misc/while*.tests`, `tests/oil/oils-master/spec/loop.test.sh`, `tests/oil/oils-master/spec/shell-grammar.test.sh` | Loop bodies now map through explicit `command.DoGroup` in ASDL mapping and adapter path. |
| S3 | `redir_param.HereWord` decision | Planned | N/A | Likely out of ash scope (`<<<`), but should be explicitly documented as deferred/out-of-scope. |
| S4 | arithmetic-expression variant mapping (`arith_expr.*`) | In Progress | `tests/regressions/run.sh` (`asdl_arith_expr_mapping`), `tests/busybox/ash_test/ash-arith/*.tests` | ASDL dump now emits structured nodes for core variants (`Word`, `VarSub`, `Unary`, `Binary`, `BinaryAssign`); remaining exotic forms still pending. |
| S5 | boolean-expression variants (`bool_expr.*`) | Planned | `tests/busybox/ash_test/ash-quoting/*`, parsing tests | Depends on whether `[[ ... ]]` and extended tests remain in milestone scope. |
| S6 | guarded native `case` value/pattern expansion subset | Done | `tests/regressions/run.sh` (`asdl_exec_case_native_word_expansion`), BusyBox `ash-quoting`, `ash-parsing` | Includes safe literal/single-quoted/simple-var/braced-var subset with legacy fallback for risky forms. |
| S7 | guarded native redirect target expansion subset | Done | `tests/regressions/run.sh` (`bad_subst_redir_target_errors`), BusyBox `ash-vars`, `ash-psubst` | Redirect ASDL now carries `target_word`; process-subst and error parity preserved by fallback gates. |
| S8 | guarded native `argv` simple/braced var scalar subset | Done | `tests/regressions/run.sh` (`asdl_argv_simple_var_*`, `asdl_argv_braced_*`), BusyBox `ash-vars`, `ash-quoting` | Runtime safety gates avoid IFS/glob-sensitive and empty/unset drifts. |
| S9 | guarded native assignment rhs single-quoted widening | Done | `tests/regressions/run.sh` assignment rows, BusyBox `ash-vars` | Safe literal checker now accepts single-quoted parts in guarded rhs subset. |

## Next Slice

- Next ASDL-native work queue:
  1. double-quoted `argv` subset under strict parity guards
  2. broader `case` braced-operator subset with explicit evidence rows
  3. map remaining runtime `RuntimeError` catch points through unified status helper
