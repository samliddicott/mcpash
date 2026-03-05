# Final Bash Closure Checklist

Date: 2026-03-05

Purpose:

- Define objective go/no-go criteria for declaring "full bash support" in this project scope.
- Separate implementation closure from confidence/hardening closure.

## Scope Definition

"Full bash support" here means:

- Every requirement row in `docs/specs/bash-man-implementation-matrix.tsv` is `covered` for default mode.
- `--posix` lane has no `missing`/`partial` rows.
- Any `out_of_scope` rows are explicitly documented as intentional scope exclusions.

Current state snapshot:

- Matrix rows: 398
- Default lane: covered=398 partial=0 missing=0
- Posix lane: covered=384 partial=0 missing=0 out_of_scope=14

Current `--posix` out-of-scope rows (interactive-only):

- `C7.INT.01`..`C7.INT.10`
- `C8.JOB.03`, `C8.JOB.07`, `C8.JOB.11`, `C8.JOB.12`

## Gate A: Functional Closure (Required)

Pass all:

1. `make bash-posix-man-matrix`
2. `make bash-builtin-matrix`
3. `make category-buckets-matrix`
4. `make startup-mode-matrix`
5. `make semantic-matrix`
6. `make read-matrix`
7. `make diff-parity-matrix`

Acceptance:

- All commands above exit 0.
- Reports regenerate without introducing `partial`/`missing` rows in the implementation matrix.

## Gate B: Upstream Differential Confidence (Required)

Pass:

1. `make bash-tests-fetch`
2. `make bash-posix-upstream-matrix`

Acceptance:

- Upstream matrix run completes within harness limits.
- `docs/reports/bash-posix-upstream-gap-latest.md` has no newly regressed rows relative to previous accepted baseline.
- Any skipped/timeout case is explicitly listed with rationale.

## Gate C: Interactive and Signal Confidence (Required)

Pass strict comparators:

1. `STRICT=1 make jobs-interactive-matrix`
2. `STRICT=1 make trap-noninteractive-matrix`
3. `STRICT=1 make trap-interactive-matrix`
4. `make trap-variant-matrix`
5. `make completion-interactive-matrix`
6. `make interactive-ux-matrix`

Acceptance:

- Strict runs pass.
- Variant report records comparator scope and platform assumptions.

## Gate D: Resource and Stability Safety (Required)

Pass:

1. `make regressions`
2. `make stress-race`
3. `make stress-bridge`
4. `make perf-variation`

Acceptance:

- No OOM/rogue growth under configured memory caps.
- No flaky/fail-open behavior; failures are hard failures.
- Perf report updates are attached and reviewed for regressions.

## Gate E: Documentation Closure (Required)

Update and verify:

1. `docs/specs/bash-man-implementation-matrix.tsv`
2. `docs/specs/bash-man-implementation-matrix.md`
3. `docs/reports/bash-compliance-remaining-work-latest.md`
4. `docs/reports/bash-posix-partials-latest.md`
5. `docs/gap-board.md`
6. `README.md` test target section

Acceptance:

- Docs reflect actual gate outcomes of the current commit.
- No stale "partial/missing" statements remain if matrix is fully covered.
- Any intentional exclusions are clearly tagged as policy, not unknown gap.

## Gate F: Release Readiness (Recommended)

1. Add CI jobs mirroring Gates A-C on each PR and on main.
2. Freeze comparator versions used in reports (bash/ash versions).
3. Record one release-candidate baseline commit and retain associated reports.

## Sign-off Template

For release notes / milestone closure:

- Baseline commit: `<sha>`
- Matrix status: `default 398/398 covered`, `posix 384 covered + 14 out_of_scope`
- Gates A-F: `PASS/FAIL`
- Known exclusions: `<list>`
- Next milestone focus: `<text>`

