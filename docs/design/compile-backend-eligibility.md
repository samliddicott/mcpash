# Compile Backend Eligibility (Phase 1)

This file is the maintained list of phase-1 compile eligibility rules and
fallback criteria.

## Eligible ASDL shape

Phase 1 compiles only ASDL list items that are:

1. `command.AndOr` list items with no logical operators.
2. A single pipeline.
3. Non-negated pipeline.
4. Single-stage pipeline.
5. Single simple command.
6. No command-local assignments (`more_env`) and no redirections.
7. Word list present and every word part literal/single-quoted only.

Anything outside that shape falls back to interpreter mode.

## Fallback reason catalog

These reason keys are emitted under `MCTASH_COMPILE_DEBUG=1` and are treated
as stable diagnostics for phase-1 scope:

- `compile-disabled-by-config`
- `item-not-dict`
- `sentence-background`
- `sentence-child-invalid`
- `unsupported-list-item:<type>`
- `andor-has-ops`
- `andor-child-count`
- `pipeline-invalid`
- `pipeline-negated`
- `pipeline-child-count`
- `simple-not-eligible`
- `json-key-failed`
- `compiled-not-callable`
- `compile-failed`
- `compiled-runtime-error`

## Configuration

- `MCTASH_BACKEND=compiled|interpreter`
- `MCTASH_ENABLE_COMPILED=1|0`
- `MCTASH_COMPILE_DEBUG=1|0`

If `MCTASH_BACKEND=compiled` and `MCTASH_ENABLE_COMPILED=0`, runtime forces
interpreter execution and logs `compile-disabled-by-config` when debug is on.
