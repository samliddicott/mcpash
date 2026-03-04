# Bash POSIX Upstream Gap Report

Generated: 2026-03-04 07:03:14Z
Comparator baseline: GNU bash `--posix` (baserock mirror corpus, `bash-5.1-testing`)
Target: `mctash --posix`

## Lane Split

- Core lane: strict POSIX-focused files (gating)
- Info lane: extension-heavy file(s) used as drift signal only

## Summary

- core full parity: 0/8
- core failing rows: 8
- info full parity: 0/1

## Case Results

| Case | Lane | bash rc | mctash rc | stdout | stderr |
|---|---|---:|---:|---|---|
| `posix2.tests` | core | 2 | 6 | mismatch | mismatch |
| `posixexp.tests` | core | 2 | 2 | mismatch | mismatch |
| `posixexp2.tests` | core | 0 | 2 | mismatch | mismatch |
| `posixpat.tests` | core | 0 | 0 | mismatch | ok |
| `posixpipe.tests` | core | 0 | 2 | mismatch | mismatch |
| `ifs-posix.tests` | core | 0 | 124 | mismatch | mismatch |
| `comsub-posix.tests` | core | 0 | 2 | mismatch | mismatch |
| `set-e.tests` | core | 0 | 1 | mismatch | ok |
| `builtins.tests` | info | 2 | 1 | mismatch | mismatch |

## Artifacts

- Per-case outputs: `tests/bash/upstream/baserock-bash-5.1-testing/run-lanes/bash/` and `tests/bash/upstream/baserock-bash-5.1-testing/run-lanes/mctash/`
- Per-case diffs: `tests/bash/upstream/baserock-bash-5.1-testing/run-lanes/diff/`
