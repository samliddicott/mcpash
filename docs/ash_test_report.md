# Ash Test Report

Date: 2026-02-21

## Command
```
scripts/run-ash-test.sh
```

## Result
Exit status: 0

Output:
```
✔ Demotest_smoke
```

## Notes
- Current harness only runs the demo module in `tests/ash-demo`.
- Parser/lexer now handle command substitutions inside quoted words and function
  definitions of the form `name() { ... }`.
- Assignment-only commands now preserve command substitution status for `$?`
  and avoid field splitting during assignment expansion.
