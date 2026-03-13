# Bash Default Upstream Gap Report

Generated: 2026-03-13 03:02:18Z
Comparator baseline: GNU bash default mode (baserock mirror corpus, `bash-5.1-testing`)
Target: `mctash` default mode (`BASH_COMPAT=50`)

## Summary

- core full parity: 0/1
- core failing rows: 1

## Case Results

| Case | bash rc | mctash rc | stdout | stderr |
|---|---:|---:|---|---|
| `array.tests` | 0 | 0 | mismatch | mismatch |

## Artifacts

- Per-case outputs: `tests/bash/upstream/baserock-bash-5.1-testing/run-default/bash/` and `tests/bash/upstream/baserock-bash-5.1-testing/run-default/mctash/`
- Per-case diffs: `tests/bash/upstream/baserock-bash-5.1-testing/run-default/diff/`
