# FC Comparator Blocker

Date: 2026-02-28

Problem:

- The current `ash` binary used by differential runs does not provide `fc` (`fc: not found`).
- Because differential testing compares `ash` and `mctash`, this blocks direct parity checks for:
  - `fc -e` editor workflow
  - richer history editing/re-exec semantics beyond simple list/replay smoke paths

Observed evidence:

- `tests/diff/cases/man-ash-fc.sh` uses an availability guard because `fc` is missing in comparator ash.
- `ash -c 'fc -e : -l -1'` exits with command-not-found in this environment.

Interim strategy:

1. Keep `fc` differential case guarded so full suite remains green.
2. Add non-differential `mctash` self-tests for `fc` behavior where comparator evidence is unavailable.
   - Implemented in `tests/regressions/run.sh`:
     - `fc_list_last_two`
     - `fc_list_reverse`
     - `fc_substitute_and_reexec`
     - `fc_editor_flag_acceptance`
     - `fc_invalid_reference_status`
3. If an ash build with `fc` is introduced, unguard and promote `fc` matrix to full differential parity.

Exit criteria for removing blocker:

- Comparator shell supports `fc`.
- Differential cases cover list/reverse/substitute/editor paths with stable expected behavior.
