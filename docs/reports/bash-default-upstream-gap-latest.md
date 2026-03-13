# Bash Default Upstream Gap Report

Generated: 2026-03-13 22:37:42Z
Comparator baseline: GNU bash default mode (baserock mirror corpus, `bash-5.1-testing`)
Target: `mctash` default mode (`BASH_COMPAT=50`)

## Summary

- core full parity: 6/14
- core failing rows: 8

## Case Results

| Case | bash rc | mctash rc | stdout | stderr |
|---|---:|---:|---|---|
| `alias.tests` | 0 | 0 | ok | ok |
| `appendop.tests` | 0 | 0 | ok | ok |
| `arith.tests` | 1 | 1 | ok | ok |
| `array.tests` | 0 | 0 | mismatch | mismatch |
| `assoc.tests` | 1 | 1 | ok | ok |
| `builtins.tests` | 2 | 2 | mismatch | mismatch |
| `case.tests` | 0 | 0 | ok | ok |
| `comsub.tests` | 0 | 0 | ok | ok |
| `cond.tests` | 0 | 127 | mismatch | mismatch |
| `coproc.tests` | 0 | 124 | mismatch | mismatch |
| `errors.tests` | 2 | 127 | mismatch | mismatch |
| `exp.tests` | 0 | 0 | mismatch | mismatch |
| `exportfunc.tests` | 0 | 2 | mismatch | mismatch |
| `extglob.tests` | 0 | 0 | mismatch | ok |

## Artifacts

- Per-case outputs: `tests/bash/upstream/baserock-bash-5.1-testing/run-default/bash/` and `tests/bash/upstream/baserock-bash-5.1-testing/run-default/mctash/`
- Per-case diffs: `tests/bash/upstream/baserock-bash-5.1-testing/run-default/diff/`
