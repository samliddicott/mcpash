# FC Follow-On Design / Implementation Plan

Status: core `fc` POSIX+extra rows (`53/54/55/56` and `EXTRA.002`) are now comparator-green against `bash`.
Comparator policy: keep using `bash` for `fc` lanes until an `ash` comparator with `fc` is available.

## Objective

Move from row-closure parity to robust feature-model quality for `fc` and adjacent history/editor semantics.

## Remaining Feature Cluster Work

1. Editor process environment parity
- Current gap: `fc` editor invocation uses host process environment, not shell runtime env snapshot.
- Design: invoke editor with `env=dict(self.env)` (+ stable PATH rules).
- Benefit: matches shell-visible `EDITOR`/exported vars semantics, reduces surprising editor behavior.

2. History transaction model for `fc`
- Current behavior: replay lines are appended as executed; recursion edge-cases can still surface on self-referential ranges.
- Design:
  - introduce explicit selection phase (`resolve refs -> immutable command list`),
  - edit phase,
  - execution phase with guarded append policy.
- Benefit: prevents accidental self-recursive `fc` replay loops and clarifies state transitions.

3. Diagnostics normalization for `fc`
- Current status: status parity is covered, message text parity is mixed.
- Design:
  - route all `fc` diagnostics through diagnostic keys,
  - keep comparator-aware semantic assertions for test gates.
- Benefit: stable error behavior + future i18n friendliness.

4. Strict `fc` feature matrix extension
- Add new dedicated cases for:
  - empty-history no-op/failure matrix per mode,
  - reference resolution precedence (numeric vs prefix),
  - explicit `-e` override over `FCEDIT`/`EDITOR` with deterministic marker editors.
- Benefit: protects implementation model from regressions without overfitting to incidental output text.

## Suggested Implementation Order

1. Editor env propagation in runtime (`_run_fc` editor subprocess env).
2. Selection/edit/execute phase refactor with loop-guard for self-referential replay.
3. Diagnostic-key routing for `fc` parse/arg errors.
4. Add strict extension tests and update matrix rows/notes.

## Exit Criteria

- Existing `fc` rows remain green.
- New strict `fc` extension tests green in bash comparator lane.
- No recursion failures when `fc` edits/replays commands that include `fc` tokens.
- `feature-gap-board` remains free of `fc` topic rows.

