# FC Runtime Model

## Scope

This note defines `fc` behavior for mctash with `bash` as comparator for parity evidence.

Rows in scope:

- `BPOSIX.CORE.053`
- `BPOSIX.CORE.054`
- `BPOSIX.CORE.055`
- `BPOSIX.CORE.056`
- `BPOSIX.EXTRA.002`

## Mode Model

`fc` has three runtime modes:

1. `list`
- Trigger: `-l`.
- Action: print selected history entries.
- Constraints: no modified-marker (`*`) decoration in listing output for POSIX row 53.

2. `edit`
- Trigger: default mode, or `-e editor`.
- Action: write selected command range to temp file, invoke editor command, re-read file, execute resulting lines.
- Editor selection precedence:
  1. explicit `-e`
  2. `FCEDIT` (if set and non-empty)
  3. `EDITOR` (if set and non-empty)
  4. default `ed`

3. `subst`
- Trigger: `-s`.
- Action: optional `old=new` substitution over selected command and immediate execution.

## Address/Range Model

Reference resolution supports:

- numeric history references,
- negative offsets (`-1`, `-2`, ...),
- prefix search fallback.

Default reference is the previous non-`fc` entry.

## Argument Validation Invariants

1. `fc` extra args in non-substitution usage are treated per comparator behavior for this lane (current bash comparator acceptance/rejection reflected by test outcomes).
2. `fc -s` with too many operands fails and emits diagnostic text (row 56).
3. No-history behavior:
- `list`/`edit` surfaces follow comparator permissiveness,
- `-e -`/`subst` keep strict failure semantics where comparator requires them.

## State + Side Effects

Inputs:

- `self._history`
- env vars: `FCEDIT`, `EDITOR`

Outputs:

- stdout listing or replayed commands,
- stderr diagnostics for invalid argument surfaces,
- history append of replayed commands.

Temporary file lifecycle:

- temp file created for edit mode,
- editor invoked with temp path,
- file re-read then removed.

## Comparator Evidence

Primary row tests:

- `tests/diff/cases/bash-posix-doc-053.sh`
- `tests/diff/cases/bash-posix-doc-054.sh`
- `tests/diff/cases/bash-posix-doc-055.sh`
- `tests/diff/cases/bash-posix-doc-056.sh`
- `tests/diff/cases/bash-posix-doc-extra-002.sh`

Additional `fc` behavior matrix tests:

- `tests/diff/cases/man-ash-fc.sh`
- `tests/diff/cases/man-ash-fc-editor-env.sh`
- `tests/diff/cases/man-ash-fc-ranges.sh`
- `tests/diff/cases/man-ash-fc-edit-reexec.sh`

