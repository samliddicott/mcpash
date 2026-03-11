# Full Bash Coverage Baseline

Generated: 2026-03-11

## Goal

Establish a reproducible starting point for the full bash (default mode)
coverage milestone.

## Baseline Gates Run

1. `tests/compat/run_bash_category_bucket_matrix.sh`
   - Result: pass
   - Artifact: `docs/reports/bash-category-buckets-latest.md`
2. `STRICT=1 tests/compat/run_bash_builtin_matrix.sh`
   - Result: pass
   - Artifact: `docs/reports/bash-builtin-matrix-latest.md`
3. `tests/compat/run_bash_invocation_option_matrix.sh`
   - Result: pass

## Requirements Matrix Snapshot

Source: `docs/specs/bash-man-implementation-matrix.tsv`

- Total requirement rows: `422`
- `mctash_default=covered`: `422`
- `mctash_posix=covered`: `422`

## Initial Risk Notes

1. Matrix coverage currently reports complete row status, but this milestone
   treats that as a continuously verified claim, not a one-time declaration.
2. Upstream full-bash corpus differential still needs to be run as a milestone
   phase to detect undocumented gaps.
3. Ash/posix lanes remain required non-regression blockers while default bash
   coverage expands.

## Next Action

Proceed to Phase 2 in `docs/plans/013-full-bash-coverage.md`:

- tighten row-level strict case mapping and eliminate any non-strict probes.
