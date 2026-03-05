# Bash Man Requirements Implementation Matrix

Source inventory: `docs/specs/bash-man-requirements.tsv`

Matrix file: `docs/specs/bash-man-implementation-matrix.tsv`

Total requirements: 398
- Rows with test/harness IDs: 398/398
- Unknown rows: 0 (all rows now classified as covered/partial/missing/out_of_scope).

## Status Counts

### mctash default lane
- covered: 229
- partial: 168
- missing: 1
- unknown: 0

### mctash --posix lane
- covered: 215
- partial: 168
- missing: 1
- out_of_scope: 14
- unknown: 0

## Category Summary

- Category 1: total=78, fully covered=11, remaining(partial/missing)=67, posix out_of_scope=0
- Category 2: total=28, fully covered=28, remaining(partial/missing)=0, posix out_of_scope=0
- Category 3: total=31, fully covered=16, remaining(partial/missing)=15, posix out_of_scope=0
- Category 4: total=21, fully covered=15, remaining(partial/missing)=6, posix out_of_scope=0
- Category 5: total=61, fully covered=61, remaining(partial/missing)=0, posix out_of_scope=0
- Category 6: total=79, fully covered=9, remaining(partial/missing)=70, posix out_of_scope=0
- Category 7: total=10, fully covered=10, remaining(partial/missing)=0, posix out_of_scope=10
- Category 8: total=12, fully covered=12, remaining(partial/missing)=0, posix out_of_scope=4
- Category 9: total=7, fully covered=7, remaining(partial/missing)=0, posix out_of_scope=0
- Category 10: total=6, fully covered=0, remaining(partial/missing)=6, posix out_of_scope=0
- Category 11: total=58, fully covered=53, remaining(partial/missing)=5, posix out_of_scope=0
- Category 12: total=7, fully covered=7, remaining(partial/missing)=0, posix out_of_scope=0

## Notes

- This matrix is now fully classified; remaining work is represented by `partial` and `missing` rows.
- `partial` rows are implementation/evidence gaps where linked comparator runs currently fail or timeout; they require either implementation fixes or narrower row-specific tests.
- See `docs/reports/bash-compliance-remaining-work-latest.md` for the detailed remaining-work list.
