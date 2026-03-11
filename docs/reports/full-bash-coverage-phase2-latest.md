# Full Bash Coverage Phase 2 Report

Generated: 2026-03-11

## Phase 2 Goal

Tighten requirement traceability to strict row-level executable evidence.

## Changes Made

1. Added strict-case mapping file:
   - `docs/specs/bash-man-strict-case-map.tsv`
2. Added strict-case mapping validator:
   - `scripts/check_bash_matrix_strict_cases.py`
3. Added make target:
   - `make bash-strict-case-map-check`

## Validation

Command:

- `make bash-strict-case-map-check`

Result:

- pass
- total requirement rows: `422`
- mapped via explicit case/scenario IDs: `397`
- mapped via strict runner rows: `25`

## Notes

1. Added generator for strict mapping decomposition:
   - `scripts/generate_bash_strict_case_map.py`
2. Runner-only coverage was reduced by decomposing practical matrix runners into
   concrete scenario IDs (invocation/startup/interactive/job-control lanes).
3. Remaining runner rows are concentrated in:
   - option-surface rows not yet decomposed in invocation matrix,
   - meta matrix-requirement rows (`C12.MATRIX.*`) that are inherently
     runner/meta-gate assertions.
4. Probe runs against currently undecomposed invocation options indicate real
   implementation gaps still to close before those rows can move to strict
   scenario IDs (for example `--help`, `--version`, `-O/+O`, `--login`,
   `--noprofile`, `--norc`, `--restricted`, `--noediting`).
4. Interactive control-character rows retain deterministic strict lanes while
   keeping literal control-char PTY behavior informational where terminal
   translation is environment-dependent.

## Next Step

Continue Phase 2 by reducing remaining runner-mapped rows (`25`) where practical
(primarily invocation option decomposition), then proceed to Phase 3 upstream
corpus differential.
