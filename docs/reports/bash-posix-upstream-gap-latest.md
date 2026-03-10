# Bash POSIX Upstream Gap Report

Generated: 2026-03-10 23:13:30Z
Comparator baseline: GNU bash `--posix` (baserock mirror corpus, `bash-5.1-testing`)
Target: `mctash --posix`

## Scope

- All listed upstream cases are now strict gating scope.

## Summary

- core full parity: 6/9
- core failing rows: 3
- info lane: removed (no non-gating carve-out)

## Case Results

| Case | Lane | bash rc | mctash rc | stdout | stderr |
|---|---|---:|---:|---|---|
| `posix2.tests` | core | 2 | 2 | ok | ok |
| `posixexp.tests` | core | 2 | 2 | mismatch | ok |
| `posixexp2.tests` | core | 0 | 0 | ok | ok |
| `posixpat.tests` | core | 0 | 0 | ok | ok |
| `posixpipe.tests` | core | 0 | 0 | ok | ok |
| `ifs-posix.tests` | core | 0 | 0 | ok | ok |
| `comsub-posix.tests` | core | 0 | 0 | ok | ok |
| `set-e.tests` | core | 0 | 0 | ok | mismatch |
| `builtins.tests` | core | 2 | 2 | mismatch | ok |

## Artifacts

- Per-case outputs: `tests/bash/upstream/baserock-bash-5.1-testing/run-lanes/bash/` and `tests/bash/upstream/baserock-bash-5.1-testing/run-lanes/mctash/`
- Per-case diffs: `tests/bash/upstream/baserock-bash-5.1-testing/run-lanes/diff/`
