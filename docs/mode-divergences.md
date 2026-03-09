# Mode Divergences

This document records intentional behavior differences and alignment policies
between mctash runtime lanes.

Lanes:

- `bash` lane: invoked as `bash`/`mctash`/`ptash` or with `MCTASH_MODE=bash`
- `posix` lane: invoked as `sh`/`ash`/`dash` or with `--posix` / `MCTASH_MODE=posix`

## Current policy rows

### `BPOSIX.EXTRA.001` (multibyte `IFS` splitting)

- Policy: follow bash behavior in both lanes (multibyte-aware splitting),
  not strict byte-wise POSIX interpretation.
- Tracking:
  - `docs/specs/bash-posix-mode-implementation-matrix.tsv` row `BPOSIX.EXTRA.001`
  - test `tests/diff/cases/bash-posix-doc-extra-001.sh`

### `BPOSIX.EXTRA.003` (`echo` + `xpg_echo`)

- Policy: follow bash `--posix` behavior in both lanes for this row.
- Runtime effect:
  - when `xpg_echo` is enabled, `echo` uses bash-compatible escape handling
    in both `bash` and `posix` lanes.
- Tracking:
  - `docs/specs/bash-posix-mode-implementation-matrix.tsv` row `BPOSIX.EXTRA.003`
  - test `tests/diff/cases/bash-posix-doc-extra-003.sh`

## Notes

- This file is for human-readable mode policy and deliberate divergence/alignment
  decisions.
- Requirement-level source of truth remains in:
  - `docs/specs/bash-posix-mode-requirements.tsv`
  - `docs/specs/bash-posix-mode-implementation-matrix.tsv`

## Footnotes

- `[interactive-transcript-depth]`:
  - "Normalized interactive assertions" means tests assert semantic markers
    (state/result fields) instead of exact full PTY transcript bytes.
  - A "deep byte-for-byte transcript" lane would capture and compare full
    terminal streams (prompt timing, control chars, line discipline effects,
    signal races, and ordering) against comparator shells.
  - We use normalized assertions in standard gates for determinism; deep
    transcript parity can be added as an additional strict lane.
