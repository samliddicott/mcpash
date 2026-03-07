# Bash POSIX Doc Matrix

Generated: 2026-03-07 16:10:03Z

Source: https://tiswww.case.edu/php/chet/bash/POSIX (6.11.2)

## Tranche Summary (Items 1..10)

- covered rows: 7
- partial rows: 3
- executed case files: 1
- diff runner exit code: 1
- mismatch lines: 1

## Executed Cases

- bash-posix-doc-001-010.sh

## Partial Rows in Tranche

- BPOSIX.CORE.001 (item 1): Comparator probe mismatch: mctash --posix currently does not set POSIXLY_CORRECT automatically. Evidence: tests/diff/cases/bash-posix-doc-001-010.sh; Source: bash/POSIX 6.11.2 item 1.
- BPOSIX.CORE.002 (item 2): Comparator probe mismatch: nested interactive --posix startup did not source ENV under current mctash path. Evidence: tests/diff/cases/bash-posix-doc-001-010.sh; Source: bash/POSIX 6.11.2 item 2.
- BPOSIX.CORE.007 (item 7): Comparator probe mismatch: `time -p` status diverges (bash --posix=125 vs mctash --posix=0 in probe). Evidence: tests/diff/cases/bash-posix-doc-001-010.sh; Source: bash/POSIX 6.11.2 item 7.

## Mismatch Extract

- 1:bash-posix-doc-001-010: stdout mismatch
