# POSIX/Ash Alignment Report (2026-02-24)

## Scope

This is a focused conformance checkpoint for the current `mctash` runtime and parser, using:

- BusyBox `ash_test` corpus (primary ash-compat signal)
- Oil POSIX-relevant subset (secondary independent signal)
- POSIX Shell Command Language Issue 8 (2024), XCU Chapter 2
- POSIX rationale XCU C.2
- local `man ash` behavior expectations

## Evidence

### BusyBox ash corpus

Command:

```sh
RUN_TIMEOUT=1200 src/tests/run_busybox_ash.sh run
```

Result:

- `ok=357`
- `fail=0`
- `skip=0`

Interpretation:

- Current implementation matches the BusyBox ash corpus currently exercised by the harness, including `ash-z_slow/many_ifs.tests`.

### Oil subset corpus

Command:

```sh
src/tests/run_oil_subset.sh run smoke redirect word-split posix shell-grammar sh-options command-parsing loop if_ case_ var-op-strip var-op-test var-sub pipeline command_
```

Result:

- `total=372`
- `pass=244`
- `fail=1`
- `skip=127`

Single remaining fail:

- `pipeline.test.sh`: `bash/dash/mksh run the last command is run in its own process`
  - Expected by this Oil case: `line=hi` (OSH/lastpipe-like behavior)
  - Current ash-compatible behavior: `line=`
  - This is an intentional ash/dash-compatible semantic, not a regression.

## POSIX + man ash conformance posture

What we can now claim with evidence:

- Strong ash compatibility for this BusyBox corpus.
- Core POSIX shell grammar/expansion/redirection/control-flow behavior validated by combined corpora.

What is still not a formal claim yet:

- Full formal POSIX certification across all Chapter 2 corner cases.
- Full startup-option parity with all `man ash` flags/modes.
- Full interactive/job-control/editor-mode parity.

## ASDL path status

- Execution path remains: `Parser -> LST -> OSH-shaped ASDL mapping -> adapter -> runtime`.
- We are using OSH ASDL artifacts as the structural guide, while runtime still executes adapted internal nodes.
- This remains compatible with the milestone objective (ash parity first, native OSH node execution as follow-on refactor).

## Next recommended work

1. Write a strict requirement-to-test trace for POSIX Chapter 2 sections with explicit case links.
2. Expand startup option parity (`-o/+o`, selected single-letter flags in scope) and document out-of-scope options.
3. Add targeted regression tests for known sensitive areas:
   - `read` with mixed IFS whitespace/non-whitespace delimiters
   - pipeline status/control-flow interactions
   - `exec`/slash-path diagnostic code paths (`126/127`)
