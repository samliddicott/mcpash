# Implementation Review Plan

## Philosophy

Implement by coherent feature groups, not by test-file clusters.

Priority policy:

1. Existing partially-implemented features (close semantic gaps first).
2. Existing covered-but-fragile behavior (hardening).
3. New surface features.

Selection scoring for feature groups:

- parity impact (POSIX/bash mismatch severity),
- usage frequency,
- cross-cutting leverage,
- risk/complexity,
- evidence quality (strict comparator tests available).

## Current Ordered Worklist

1. Startup mode semantics (`runtime:startup`, `builtin:set` baseline rows)
- `BPOSIX.CORE.001`, `BPOSIX.CORE.002`, `BPOSIX.CORE.063`, `BPOSIX.CORE.064`.
- Goal: correct POSIX mode identity/startup behavior first.

2. Job/signal lifecycle (`runtime:job-control`, `builtin:wait`, `builtin:trap`)
- `BPOSIX.CORE.022..026`, `BPOSIX.CORE.067..069`, `BPOSIX.CORE.074..075`.

3. `test` + locale correctness
- `BPOSIX.CORE.065`, `BPOSIX.CORE.066`, `BCOMPAT.52.001`.

4. `unset` semantics
- `BPOSIX.CORE.072`, `BPOSIX.CORE.073`, `BCOMPAT.51.001`.

5. Expansion/quoting compatibility edges
- `BCOMPAT.41.002`, `BCOMPAT.42.001`, `BCOMPAT.42.002`, `BPOSIX.CORE.014`.

6. `fc` feature cluster
- `BPOSIX.CORE.053..056`, `BPOSIX.EXTRA.002`.

7. `type`/`command` PATH classification cleanup
- `BPOSIX.CORE.018`, `BPOSIX.CORE.031`, `BPOSIX.CORE.070`.

## Execution Loop

For each feature group:

1. validate targeted row tests,
2. design/runtime change as one coherent slice,
3. rerun targeted comparator tests,
4. commit,
5. update matrix/notes only after evidence.

Primary artifacts:

- `docs/specs/feature-gap-board.md`
- `docs/specs/feature-index.md`
- `docs/specs/*implementation-matrix.tsv`
