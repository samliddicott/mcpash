# Bash Man-Page Requirements Inventory

Source of truth: `docs/specs/bash-man-requirements.tsv`.

This inventory is intentionally explicit: one requirement row per feature with no grouped `etc` placeholders.

## Category Counts

- Category 1: 78 requirements
- Category 2: 28 requirements
- Category 3: 31 requirements
- Category 4: 21 requirements
- Category 5: 61 requirements
- Category 6: 79 requirements
- Category 7: 10 requirements
- Category 8: 12 requirements
- Category 9: 7 requirements
- Category 10: 6 requirements
- Category 11: 58 requirements
- Category 12: 7 requirements

## Subcategory Counts

- Category 1 `invocation.long-option`: 14
- Category 1 `invocation.set-o-option`: 27
- Category 1 `invocation.set-short-option`: 19
- Category 1 `invocation.short-option`: 12
- Category 1 `invocation.startup-files`: 6
- Category 2 `grammar.core`: 28
- Category 3 `expansion`: 31
- Category 4 `redirection`: 21
- Category 5 `builtin.command`: 61
- Category 6 `variables.bash-extension`: 53
- Category 6 `variables.posix-core`: 17
- Category 6 `variables.special-parameters`: 9
- Category 7 `interactive`: 10
- Category 8 `jobs-signals`: 12
- Category 9 `compatibility`: 7
- Category 10 `state-model`: 6
- Category 11 `mode-framework`: 5
- Category 11 `shopt-option-surface`: 53
- Category 12 `requirements-matrix`: 7

## Fields

- `req_id`: stable requirement identifier.
- `category`: category number from the Bash feature categorization.
- `subcategory`: narrower functional lane.
- `feature_type`: `option`, `builtin`, `grammar`, `expansion`, `redirection`, `variable`, `interactive`, `behavior`, or `meta`.
- `feature`: exact surface/feature text from the requirement decomposition.
- `posix_mode_status`: `present`, `changed`, `extension`, or `n/a`.
- `bash_man_section`: section mapping in `man bash` used for traceability.
- `notes`: concise implementation/comparator guidance.

## Next Use

- Add status/evidence columns in a matrix companion (implemented/partial/missing + test case IDs).
- Gate every row with at least one executable test case before marking complete.
- Companion matrix now exists at `docs/specs/bash-man-implementation-matrix.tsv` (summary: `docs/specs/bash-man-implementation-matrix.md`).
