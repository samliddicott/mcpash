# Compile Backend Eligibility (Phases 1-3)

This file is the maintained list of compile eligibility rules and
fallback criteria.

## Phase 1 baseline

Phase 1 introduced:

- backend selection and conservative fallback (`interpreter` vs `compiled`)
- compile cache keyed by parsed node content
- debug fallback reason reporting

## Eligible ASDL shape (current)

Compiled mode currently accepts list items with:

1. `command.Sentence` list items that are not background (`&`).
2. `command.AndOr` with one or more pipeline children.
3. Pipeline nodes with one or more command stages.
4. Command stages in this supported set:
   - `command.Simple`
   - `command.Redirect`
   - `command.BraceGroup`
   - `command.If`
   - `command.WhileUntil`
   - `command.ControlFlow`
   - `command.ShAssignment`

Notes:

- Multi-stage pipelines are supported by delegating orchestration to existing
  runtime adapters from compiled dispatch.
- Redirect handling in compiled dispatch reuses existing fd-redirection helpers.
- Any unsupported node shape or active unsafe runtime context falls back to
  interpreter execution.

## Fallback reason catalog

These reason keys are emitted under `MCTASH_COMPILE_DEBUG=1`:

- `compile-disabled-by-config`
- `trap-active`
- `interactive-monitor-active`
- `item-not-dict`
- `sentence-background`
- `sentence-child-invalid`
- `unsupported-list-item:<type>`
- `andor-child-count`
- `pipeline-invalid`
- `pipeline-child-count`
- `pipeline-stage-invalid`
- `unsupported-command:<type>`
- `json-key-failed`
- `compiled-not-callable`
- `compile-failed`
- `compiled-runtime-error`

## Configuration

- `MCTASH_BACKEND=compiled|interpreter`
- `MCTASH_ENABLE_COMPILED=1|0`
- `MCTASH_COMPILE_DEBUG=1|0`
- `MCTASH_NAMESPACE=<name>` (optional cache-key namespace override)

If `MCTASH_BACKEND=compiled` and `MCTASH_ENABLE_COMPILED=0`, runtime forces
interpreter execution and logs `compile-disabled-by-config` when debug is on.
