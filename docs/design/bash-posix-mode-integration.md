# Bash POSIX-Mode Integration Design

Source:
- `https://tiswww.case.edu/php/chet/bash/POSIX`

Companion specs:
- `docs/specs/bash-posix-mode-requirements.tsv`
- `docs/specs/bash-posix-mode-implementation-matrix.tsv`

## Purpose
Use Bash 6.11.2 as:
1. a requirement inventory,
2. a test-planning inventory,
3. a design-hints inventory (where behavior should be implemented: parse, expansion, runtime, or startup mode handling).

## Numbering Model
The source contains two numbered lists.

- Primary list in 6.11.2: items `1..75`
- Additional section (“does not implement by default even when in POSIX mode”): numbering restarts at `1..3`

To avoid collisions:
- `BPOSIX.CORE.NNN` maps to 6.11.2 items 1..75
- `BPOSIX.EXTRA.NNN` maps to restarted items 1..3

## Encoding Guardrail
The page may be served with weak charset metadata on some paths.

Ingestion rule:
1. fetch with `wget`,
2. decode as UTF-8 first,
3. if mojibake markers are seen (e.g., `â€˜waitâ€™`), re-decode using `iconv` fallback and normalize quotes before parsing rows.

## How to Use Rows
For each `BPOSIX.*` row:
1. keep source trace (`source_section`, `source_group`, `source_item`),
2. assign comparator test case(s),
3. set matrix status by evidence:
   - `covered` only with executable row-level evidence,
   - otherwise `partial`.

## Early Slice (items 1..10)
Items 1..10 are a good starter tranche because they touch startup, parser, and redirection/expansion ordering with minimal interactive dependence.

Suggested implementation order:
1. startup/mode (`1`, `2`)
2. alias/parse timing (`3`, `4`, `5`)
3. `time` grammar (`6`, `7`)
4. parameter/quote and redirection expansion rules (`8`, `9`, `10`)

## Policy for EXTRA rows
`BPOSIX.EXTRA.*` rows represent behaviors Bash documents as not enabled by default in POSIX mode.

Current policy in matrix:
- keep tracked with explicit source anchors,
- default `mctash_posix=out_of_scope` until product policy chooses strict-default emulation for those rows.
