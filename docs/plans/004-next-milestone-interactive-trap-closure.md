# 004 - Next Milestone: Interactive Jobs + Trap Closure

## Goal

Close remaining interactive/job-control and trap partials with strict, repeatable parity gates.

## Scope

1. Interactive jobs strict closure
- Promote `tests/compat/run_jobs_interactive_matrix.sh` from informational to strict parity.
- Resolve current marker differences (e.g. `jobs -p` visibility path).
- Add multi-job and pipeline interactive scenarios.

2. Trap strict closure
- Promote non-interactive and interactive trap matrices to strict parity.
- Extend signal set where portable; document per-platform exclusions explicitly.
- Add ordering/interaction checks around `wait`, pipelines, and blocking builtins.

3. Variant report integration
- Keep `tests/compat/run_trap_variant_matrix.sh` as capability and drift detector.
- Link report deltas to actionable case additions.

4. POSIX trace completion pass
- Convert remaining partial rows in `docs/posix-shall-trace.md` where evidence now exists.
- Keep only intentionally deferred rows partial, with explicit rationale.

## Exit criteria

- `STRICT=1 make jobs-interactive-matrix` passes.
- `STRICT=1 make trap-noninteractive-matrix` passes.
- `STRICT=1 make trap-interactive-matrix` passes for declared platform scope.
- `make trap-variant-matrix` stable and documented.
- `docs/gap-board.md` and `docs/posix-shall-trace.md` updated with final status and evidence links.
