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
- mapped via explicit case IDs: `368`
- mapped via strict runner rows: `54`

## Notes

1. Runner-mapped rows are explicit and per-requirement (`runner:<runner>#<req_id>`).
2. Interactive control-character rows retain deterministic strict lanes while
   keeping literal control-char PTY behavior informational where terminal
   translation is environment-dependent.

## Next Step

Continue Phase 2 by reducing runner-mapped rows (`54`) into additional direct
case IDs where practical, then proceed to Phase 3 upstream corpus differential.
