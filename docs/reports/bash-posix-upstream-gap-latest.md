# Bash POSIX Upstream Gap Report

Generated: 2026-03-04 16:34:56Z
Comparator baseline: GNU bash `--posix` (baserock mirror corpus, `bash-5.1-testing`)
Target: `mctash --posix`

## Lane Split

- Core lane: strict POSIX-focused files (gating)
- Info lane: extension-heavy file(s) used as drift signal only

## Summary

- core full parity: 8/8
- core failing rows: 0
- info full parity: 0/1

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
| `builtins.tests` | info | 2 | 1 | mismatch | mismatch |

## Artifacts

- Per-case outputs: `tests/bash/upstream/baserock-bash-5.1-testing/run-lanes/bash/` and `tests/bash/upstream/baserock-bash-5.1-testing/run-lanes/mctash/`
- Per-case diffs: `tests/bash/upstream/baserock-bash-5.1-testing/run-lanes/diff/`
