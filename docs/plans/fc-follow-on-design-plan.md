# FC Follow-On Design / Implementation Plan

Status: closed for this cluster in current comparator scope.
Comparator policy: keep using `bash` for `fc` lanes until an `ash` comparator with `fc` is available.

## Objective

Move from row-closure parity to robust feature-model quality for `fc` and adjacent history/editor semantics.

## Status Snapshot (2026-03-09)

Completed:
- Editor process environment parity:
  - `fc` editor subprocess now runs with shell runtime env snapshot.
  - Covered by `man-ash-fc-editor-env`.
- History transaction model hardening:
  - replay execution runs through guarded execution path with recursion/depth guard.
  - prevents self-referential replay loops.
- Diagnostics normalization:
  - `fc` failures route through diagnostic keys (`usage`, `no history`, invalid editor, event-not-found, recursion guard).
- Strict matrix extension:
  - Added comparator-gated rows for:
    - empty-history matrix (`man-ash-fc-empty-history`)
    - `-e` override precedence (`man-ash-fc-e-override`)
    - reference precedence numeric-vs-prefix (`man-ash-fc-ref-precedence`)
- Interactive depth lane:
  - Added PTY interactive editor flow matrix (`run_fc_interactive_matrix.sh`) and wired into strict builtin matrix lane.

Deferred:
- Comparator broadening to `ash` for `fc` lanes is deferred until an ash comparator with `fc` exists.

## Exit Criteria

- Existing `fc` rows remain green.
- New strict `fc` extension tests remain green in bash comparator lane.
- Interactive `fc` editor flow remains green in PTY lane.
- `feature-gap-board` remains free of `fc` topic rows in current comparator scope.
