# Bash POSIX Upstream Gap Report

Generated: 2026-03-10 13:51:42Z
Comparator baseline: GNU bash `--posix` (baserock mirror corpus, `bash-5.1-testing`)
Target: `mctash --posix`

## Scope

- All listed upstream cases are now strict gating scope.

## Summary

- core full parity: 9/9
- core failing rows: 0
- info lane: removed (no non-gating carve-out)

## Case Results

| Case | Lane | bash rc | mctash rc | stdout | stderr |
|---|---|---:|---:|---|---|
| `posix2.tests` | core | 2 | 2 | ok | ok |
| `posixexp.tests` | core | 2 | 2 | ok | ok |
| `posixexp2.tests` | core | 0 | 0 | ok | ok |
| `posixpat.tests` | core | 0 | 0 | ok | ok |
| `posixpipe.tests` | core | 0 | 0 | ok | ok |
| `ifs-posix.tests` | core | 0 | 0 | ok | ok |
| `comsub-posix.tests` | core | 0 | 0 | ok | ok |
| `set-e.tests` | core | 0 | 0 | ok | ok |
| `builtins.tests` | core | 2 | 2 | ok | ok |

## Artifacts

- Per-case outputs: `tests/bash/upstream/baserock-bash-5.1-testing/run-lanes/bash/` and `tests/bash/upstream/baserock-bash-5.1-testing/run-lanes/mctash/`
- Per-case diffs: `tests/bash/upstream/baserock-bash-5.1-testing/run-lanes/diff/`
