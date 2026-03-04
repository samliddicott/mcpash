# Bash POSIX Upstream Gap Report

Generated: 2026-03-04 05:47:32Z
Comparator baseline: GNU bash `--posix` (baserock mirror corpus, `bash-5.1-testing`)
Target: `mctash --posix`

## Scope

- Source mirror: `https://git.baserock.org/cgit/delta/bash.git/tree/tests?h=bash-5.1-testing`
- TLS note: mirror certificate is expired; fetch used `wget --no-check-certificate`
- Corpus locally fetched: full `tests/` file list from mirror tree index
- Cases executed in this run: 9
- Runner safety limits: `timeout -k 5 45` per case; `MCTASH_MAX_VMEM_KB=786432` on mctash lane

## Summary

- full parity cases: 0/9
- exit-status mismatches: 7
- stdout mismatches: 9
- stderr mismatches: 7

## Case Results

| Case | bash rc | mctash rc | stdout | stderr |
|---|---:|---:|---|---|
| `posix2.tests` | 2 | 6 | mismatch | mismatch |
| `posixexp.tests` | 2 | 2 | mismatch | mismatch |
| `posixexp2.tests` | 0 | 2 | mismatch | mismatch |
| `posixpat.tests` | 0 | 0 | mismatch | ok |
| `posixpipe.tests` | 0 | 2 | mismatch | mismatch |
| `ifs-posix.tests` | 0 | 124 | mismatch | mismatch |
| `comsub-posix.tests` | 0 | 2 | mismatch | mismatch |
| `set-e.tests` | 0 | 1 | mismatch | ok |
| `builtins.tests` | 2 | 1 | mismatch | mismatch |

## First Mismatches To Triage

- `posix2.tests`: rc 2/6, stdout=diff, stderr=diff
- `posixexp.tests`: rc 2/2, stdout=diff, stderr=diff
- `posixexp2.tests`: rc 0/2, stdout=diff, stderr=diff
- `posixpat.tests`: rc 0/0, stdout=diff, stderr=ok
- `posixpipe.tests`: rc 0/2, stdout=diff, stderr=diff
- `ifs-posix.tests`: rc 0/124, stdout=diff, stderr=diff
- `comsub-posix.tests`: rc 0/2, stdout=diff, stderr=diff
- `set-e.tests`: rc 0/1, stdout=diff, stderr=ok
- `builtins.tests`: rc 2/1, stdout=diff, stderr=diff

## Artifacts

- Per-case outputs: `tests/bash/upstream/baserock-bash-5.1-testing/run2/bash/` and `tests/bash/upstream/baserock-bash-5.1-testing/run2/mctash/`
- Per-case diffs: `tests/bash/upstream/baserock-bash-5.1-testing/run2/diff/`
