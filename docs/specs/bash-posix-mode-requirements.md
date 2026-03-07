# Bash POSIX-Mode Requirements (6.11.2)

Source: `https://tiswww.case.edu/php/chet/bash/POSIX`

This inventory decomposes the entire 6.11.2 behavior list into row-level requirements.

Numbering note:
- `core-posix-mode`: source items `1..75`
- `additional-not-by-default`: source items restart at `1..3` in the section beginning with “There is additional POSIX behavior ...”.
- Rows are uniquely identified using separate namespaces:
  - `BPOSIX.CORE.NNN`
  - `BPOSIX.EXTRA.NNN`

Files:
- Requirements: `docs/specs/bash-posix-mode-requirements.tsv`
- Matrix: `docs/specs/bash-posix-mode-implementation-matrix.tsv`

Row counts:
- Core POSIX-mode changes: 75
- Additional non-default POSIX behaviors: 3
- Total: 78

Intended use:
1. Requirements trace to source item numbers.
2. Design ownership hints (`owner`, `phase`) guide implementation planning.
3. Matrix rows become executable by adding row-level comparator tests and promoting status from `partial`.
