# Bash POSIX Doc Items 1-10 Probe

Source: `https://tiswww.case.edu/php/chet/bash/POSIX` (6.11.2)
Case: `tests/diff/cases/bash-posix-doc-001-010.sh`

## Result

- Comparator run status: mismatch (expected while gaps remain).
- Probe rows with parity mismatch:
  - Item 1 (`POSIXLY_CORRECT` set): bash=1, mctash=0
  - Item 2 (`ENV` startup behavior in nested interactive `--posix` probe): bash=1, mctash=0
  - Item 7 (`time -p` reserved-word/parser behavior): bash status 125, mctash status 0

## Passing in this tranche

- Item 3 (alias expansion in non-interactive)
- Item 4 (reserved-word context not alias-expanded)
- Item 5 (command-sub alias parse timing probe)
- Item 6 (`time` as simple command)
- Item 8 (`${...}` in double quotes with single-quote edge probe)
- Item 9 (redirection word does not pathname-expand in non-interactive mode)
- Item 10 (redirection word does not word-split)

## Evidence extract

- bash output: `tests/diff/logs/ash/bash-posix-doc-001-010.out`
- mctash output: `tests/diff/logs/mctash/bash-posix-doc-001-010.out`
- diff: `tests/diff/logs/diff/bash-posix-doc-001-010.out`
