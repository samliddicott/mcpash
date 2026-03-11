# Full Bash Coverage Plan

Date: 2026-03-11

## Objective

Reach and maintain high-confidence GNU bash parity in default (non-`--posix`)
mode while preserving existing ash/posix parity lanes.

## Scope

In scope:

- Bash default-mode behavior parity (options, builtins, expansion, interactive,
  jobs/signals, variables/state).
- Row-level requirement coverage from `docs/specs/bash-man-requirements.tsv`
  and `docs/specs/bash-man-implementation-matrix.tsv`.
- Upstream corpus comparison where available (fetched on demand, not vendored).

Out of scope for this plan:

- Reopening Phase 4 namespace semantic switching policy from
  `docs/plans/012-compile-backend-dual-runtime.md` (currently deferred).
- Localization depth beyond existing diagnostic-key/i18n framework.

## Baseline

Current matrix documents show full row coverage, but this milestone treats that
as a claim to continuously verify via strict gates and upstream corpora.

## Phases

### Phase 1: Baseline + Gate Contract (started)

1. Run and record baseline gates for default bash coverage:
   - `tests/compat/run_bash_category_bucket_matrix.sh`
   - `STRICT=1 tests/compat/run_bash_builtin_matrix.sh`
   - `tests/compat/run_bash_invocation_option_matrix.sh`
2. Generate a single baseline report with:
   - gate pass/fail,
   - matrix row counts,
   - known-risk notes.
3. Define milestone gate contract:
   - all baseline gates must stay green,
   - ash/posix gates remain non-regression blockers.

Exit criteria:

- Baseline report committed.
- Phase-1 gate contract documented and reproducible.

### Phase 2: Requirement Trace Tightening

1. Re-check every bash-man requirement row for explicit case IDs.
2. Convert any scaffold/probe cases into strict assertions.
3. Add missing dedicated cases for rows lacking hard assertions.

Exit criteria:

- No requirement row without at least one strict executable case ID.

Progress (2026-03-11):

- Implemented strict-case mapping and gate:
  - `docs/specs/bash-man-strict-case-map.tsv`
  - `scripts/generate_bash_strict_case_map.py`
  - `scripts/check_bash_matrix_strict_cases.py`
  - `make bash-strict-case-map-check`
- Current mapping coverage:
  - 422/422 rows mapped
  - 397 mapped via direct case/scenario IDs
  - 25 mapped via strict runner row IDs

### Phase 3: Upstream Bash Corpus Differential

1. Fetch upstream bash tests on demand into ignored workspace area.
2. Run selected/default-mode compatible subsets against:
   - comparator `bash`,
   - target `mctash` default mode.
3. Produce mismatch report grouped by feature cluster.

Exit criteria:

- Fresh upstream differential gap report committed.
- Every mismatch mapped to a matrix row or new requirement row.

### Phase 4: Implementation Clusters (Feature-First)

Prioritize by impact:

1. Expansion/quoting edge clusters.
2. Builtin option/error universes.
3. Interactive/readline/completion depth.
4. Jobs/traps/signal edge semantics.
5. Variable/state semantics and special-parameter edges.

Rules:

- Implement cluster-by-cluster (not row-by-row patching).
- Keep ash/posix and compiled/interpreter non-regression checks active.

Exit criteria:

- Cluster gaps reduced to zero or explicitly deferred with policy notes.

### Phase 5: Closure + Ongoing Guardrails

1. Run full gate stack and produce closure report.
2. Update gap board and feature index to reflect final status.
3. Keep recurring gates for drift detection.

Exit criteria:

- Full-bash closure report committed.
- Ongoing gate commands documented in top-level workflow.

## Gate Stack (target state)

Required green set:

1. `tests/compat/run_bash_category_bucket_matrix.sh`
2. `STRICT=1 tests/compat/run_bash_builtin_matrix.sh`
3. `tests/compat/run_bash_invocation_option_matrix.sh`
4. `tests/compat/run_bash_posix_man_matrix.sh`
5. `tests/compat/run_bash_posix_upstream_matrix.sh`
6. `tests/diff/run_backend_self_parity.sh` (selected strict set)

Non-regression blockers:

1. `tests/regressions/run.sh`
2. BusyBox ash modules and conformance lane used in current release process.
