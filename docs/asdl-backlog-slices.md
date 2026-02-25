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
| S2 | `command.DoGroup` alignment | Planned | `tests/busybox/ash_test/ash-misc/while*.tests`, `tests/oil/oils-master/spec/loop.test.sh` | Parser/runtime already handle loop groups; next step is explicit ASDL mapping alignment. |
| S3 | `redir_param.HereWord` decision | Planned | N/A | Likely out of ash scope (`<<<`), but should be explicitly documented as deferred/out-of-scope. |
| S4 | arithmetic-expression variant mapping (`arith_expr.*`) | Planned | `tests/busybox/ash_test/ash-arith/*.tests` | Runtime behavior exists for many arithmetic forms; ASDL coverage/mapping remains coarse. |
| S5 | boolean-expression variants (`bool_expr.*`) | Planned | `tests/busybox/ash_test/ash-quoting/*`, parsing tests | Depends on whether `[[ ... ]]` and extended tests remain in milestone scope. |

## Next Slice

- Execute S2 (`command.DoGroup` mapping alignment) with:
  1. mapping changes
  2. targeted tests
  3. coverage report update
