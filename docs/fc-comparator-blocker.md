# FC Comparator Blocker

Date: 2026-03-03

Problem:

- The current `ash` comparator used for ash-lane parity does not provide `fc` (`fc: not found`).
- Direct ash-vs-mctash `fc` parity is therefore unavailable for editor/history workflows.

Observed evidence:

- `ash -c 'fc -e : -l -1'` exits with command-not-found in this environment.
- Differential `fc` coverage now runs against bash baseline:
  - `tests/diff/cases/man-ash-fc.sh`
  - `tests/diff/cases/man-ash-fc-editor-env.sh`
  - `tests/diff/cases/man-ash-fc-ranges.sh`

Interim strategy:

1. Keep ash-lane parity free of `fc` requirements (comparator limitation).
2. Add non-differential `mctash` self-tests for `fc` behavior where comparator evidence is unavailable.
   - Implemented in `tests/regressions/run.sh`:
     - `fc_list_last_two`
     - `fc_list_reverse`
     - `fc_substitute_and_reexec`
     - `fc_editor_flag_acceptance`
     - `fc_invalid_reference_status`
3. Continue bash-baseline differential coverage for editor/range/list/substitute surface.
4. If an ash build with `fc` is introduced, add ash-lane parity for the same matrix.

Exit criteria for removing blocker:

- Comparator ash shell supports `fc`.
- Existing differential matrix passes in ash lane for list/reverse/substitute/editor paths.
