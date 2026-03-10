# Bash Compliance Remaining Work List

Generated: 2026-03-10

Evidence sources:

- `tests/compat/run_bash_invocation_option_matrix.sh`
- `tests/compat/run_bash_posix_man_matrix.sh`
- `tests/compat/run_bash_posix_upstream_matrix.sh`
- `STRICT=1 tests/compat/run_bash_builtin_matrix.sh`
- `tests/diff/run_parity_matrix.sh`

## Summary

Total remaining items: 8

- Known behavior mismatches: 8
- Known-unknown/completeness risks tracked in this board: 0

## Remaining Items

1. `bash-compat-param-array-hash-extended`: stdout mismatch (`diff-parity-matrix`, bash lane)
2. `bash-compat-param-array-hash-extended`: stderr mismatch (`diff-parity-matrix`, bash lane)
3. `bash-compat-param-array-hash-ops`: stdout mismatch (`diff-parity-matrix`, bash lane)
4. `bash-compat-param-array-hash-ops`: stderr mismatch (`diff-parity-matrix`, bash lane)
5. `bash-compat-param-contexts`: stdout mismatch (`diff-parity-matrix`, bash lane)
6. `bash-compat-param-contexts`: stderr mismatch (`diff-parity-matrix`, bash lane)
7. `bash-compat-subscript-eval-assoc-quoted`: stdout mismatch (`diff-parity-matrix`, bash lane)
8. `bash-compat-subscript-eval-assoc-quoted`: stderr mismatch (`diff-parity-matrix`, bash lane)

Upstream POSIX core lane currently also reports 3 failing rows (separate upstream corpus lane):

- `posixexp.tests` stdout mismatch
- `set-e.tests` stderr mismatch
- `builtins.tests` stdout mismatch

## Notes

- Compliance status should continue to be asserted from executable gates, not static matrix labels alone.
