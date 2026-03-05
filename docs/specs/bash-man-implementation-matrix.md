# Bash Man Requirements Implementation Matrix

Source inventory: `docs/specs/bash-man-requirements.tsv`

Matrix file: `docs/specs/bash-man-implementation-matrix.tsv`

Status meanings:

- `covered`: implemented and tied to explicit test case(s).
- `partial`: implemented surface exists but behavior/options not complete.
- `missing`: not implemented.
- `out_of_scope`: intentionally excluded from that lane (typically posix-only lane for interactive-only items).
- `unknown`: not yet decomposed to requirement-level evidence.

Total requirements: 398

## Current Counts

### mctash default lane

- covered: 60
- partial: 1
- missing: 9
- out_of_scope: 0
- unknown: 328

### mctash --posix lane

- covered: 60
- partial: 1
- missing: 9
- out_of_scope: 14
- unknown: 314

## Seeded Evidence Sources

- `tests/compat/bash_posix_man_coverage.tsv` for Category 5 builtin rows.
- Manually seeded known gaps: `-D`, `--dump-strings`, `--dump-po-strings`, `--verbose`, `-s` trailing-arg semantics, `select`, `coproc`, `brace expansion`, `$"..."`, and `<<<` here-string.

## Next Step

- Expand `unknown` rows into concrete differential cases and fill `tests` for each requirement row.
