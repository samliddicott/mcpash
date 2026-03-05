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
- Rows with at least one test/harness ID: 398
- Rows still lacking test/harness ID: 0

## Current Counts

### mctash default lane

- covered: 68
- partial: 1
- missing: 9
- out_of_scope: 0
- unknown: 320

### mctash --posix lane

- covered: 68
- partial: 1
- missing: 9
- out_of_scope: 14
- unknown: 306

## Test-ID Attachment Coverage by Category

- Category 1: 78/78 rows have test/harness IDs
- Category 2: 28/28 rows have test/harness IDs
- Category 3: 31/31 rows have test/harness IDs
- Category 4: 21/21 rows have test/harness IDs
- Category 5: 61/61 rows have test/harness IDs
- Category 6: 79/79 rows have test/harness IDs
- Category 7: 10/10 rows have test/harness IDs
- Category 8: 12/12 rows have test/harness IDs
- Category 9: 7/7 rows have test/harness IDs
- Category 10: 6/6 rows have test/harness IDs
- Category 11: 58/58 rows have test/harness IDs
- Category 12: 7/7 rows have test/harness IDs

## Evidence Seeding Policy

- Category 5 builtin rows are seeded from `tests/compat/bash_posix_man_coverage.tsv` (row-level case IDs where available).
- Non-builtin categories currently use category-scope evidence mapping where direct row-level IDs are not yet isolated; these rows are marked in `notes` as needing narrowing.
- Known direct gaps are explicitly tagged as `missing` (for example `-D`, `--dump-strings`, `$"..."`, and `<<<`).

## Next Step

- Narrow category-scope evidence into strict row-level case IDs and add missing case files where no direct evidence exists.
