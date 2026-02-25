# Conformance Matrix (2026-02-24)

This is a practical conformance snapshot, not a formal certification report.

Evidence used:

- BusyBox `ash_test` via `src/tests/run_busybox_ash.sh`
- POSIX Shell Command Language (Issue 8, 2024):  
  `https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/V3_chap02.html`
- POSIX rationale (XCU C.2):  
  `https://pubs.opengroup.org/onlinepubs/9699919799/xrat/V4_xcu_chap02.html`
- `man ash` (local `dash` man page)

Latest corpus result:

- BusyBox `ash_test`: `ok=357 fail=0 skip=0` (full run including `ash-z_slow/many_ifs.tests`).
- Oil subset corpus (via `src/tests/run_oil_subset.sh`):
  - Expanded suite (`smoke`, `redirect`, `word-split`, `posix`,
    `shell-grammar`, `sh-options`, `command-parsing`, `loop`, `if_`, `case_`,
    `var-op-strip`, `var-op-test`, `var-sub`):
    `pass=244 fail=1 skip=127` when including `pipeline` and `command_`.
  - Remaining fail is an intentional semantic difference for last-pipeline-process
    behavior (`pipeline.test.sh` expects OSH/lastpipe-like `line=hi`; ash/dash behavior is `line=`).
  - Skips are from unsupported/non-portable directives in the lightweight
    subset runner, not known semantic failures in these slices.
  - In this runner, `## status: 99` is treated as an expected non-zero failure
    sentinel used by some Oil grammar tests.

## Overall

- Parser/AST path: **OSH-ASDL-shaped intermediate is active** (`LST -> OSH-shaped ASDL -> adapter -> runtime`).
- Ash behavior parity: **high for BusyBox ash_test corpus**.
- Full POSIX + full `ash` man-page parity claim: **not yet**.

## POSIX Shell Language (XCU Chapter 2)

- `2.2 Quoting`: `validated in corpus`, but not exhaustively proven for all nested edge cases.
- `2.3 Token recognition / operators`: `validated in corpus`.
- `2.4 Reserved words`: `validated in corpus`.
- `2.5 Parameters / variables`: `validated in corpus`; formal completeness still pending.
- `2.6 Expansions`: `validated in corpus` for major paths (parameter, command, arithmetic, splitting, glob); not formally complete.
- `2.7 Redirection`: `validated in corpus` including here-doc and IO-number cases covered by BusyBox tests.
- `2.8 Exit status / errors`: `partial` for full diagnostic text and all corner exit-path rules.
- `2.9 Shell commands (compound/simple/functions)`: `validated in corpus`.
- `2.10 Grammar`: `partial` for formal completeness proof, even though tested corpus passes.
- `2.11 Job control`: `partial` (threaded runtime model differs from traditional process/job-control internals).
- `2.14 Special builtins`: `partial` as a strict POSIX conformance statement.

## `man ash` Facilities & Options

`man ash` synopsis lists startup flags such as `-aCefnuvxIimqVEbp`, `+...`, `-o/+o`.

Current mctash status:

- Runtime `set` options currently used by tests: `implemented` (`-e`, `-f`, `-n`, `-u`, `-v`, `-x`, `pipefail`).
- Startup option parsing: `partial` but improved for non-interactive paths (`-/+` letter flags, `-o/+o name` for supported names and `pipefail`).
- `set -o` / `set +o` listing behavior: `implemented` for in-scope option names.
- Interactive/editor/job-control flags (`-i`, `-m`, `-V`, `-E`, etc.): `partial`/`not target` for this milestone.
- Startup CLI option parity with `ash` synopsis: `partial` (mctash CLI currently focuses on script execution + `--dump-lst`).
- Builtins exercised by BusyBox ash corpus: `implemented for tested semantics`.

In-scope option parity right now:

- non-interactive startup option parsing (`-`/`+` single-letter flags in implemented set)
- `-o`/`+o` with supported names
- `set -o` status listing and `set +o` re-creatable listing
- includes ash-style `nolog` and `debug` names (plus mctash `pipefail`)

Explicitly out-of-scope for current milestone:

- full interactive/editor UX parity
- full job-control parity
- complete startup flag matrix beyond currently implemented and tested options

## OSH ASDL Foundation

- Present and wired in execution path:
  - `src/syntax/osh/syntax.asdl`
  - `src/syntax/osh/types.asdl`
  - `src/syntax/osh/runtime.asdl`
  - `src/syntax/osh/value.asdl`
- Current architecture:
  - `Parser -> LST -> src/mctash/asdl_map.py -> src/mctash/osh_adapter.py -> src/mctash/runtime.py`
- Remaining gap to full native OSH node execution:
  - runtime still executes adapted internal AST, not generated typed OSH nodes directly.

## What This Means

- We can credibly claim: **Python 3 ash-compatible shell behavior for the current BusyBox ash corpus**.
- We should not yet claim: **full formal POSIX conformance** or **complete `man ash` facility/option parity**.
- Threaded-runtime deltas from traditional fork-first ash/dash are tracked in:
  - `docs/threaded-runtime-deviations.md`
- Startup option parity matrix is tracked in:
  - `docs/startup-option-matrix.md`

## Next Conformance Work

1. Add a POSIX requirement-to-test trace table (section-by-section references to tests).
2. Add startup option parity (`-aCefnuvxIimqVEbp`, `-o/+o`) where in scope.
3. Run/select additional corpus slices from Oil POSIX spec tests for independent confirmation.
4. Continue reducing documented threaded-runtime deviations where behavior-compatible fixes exist.

Current trace table:

- `docs/posix-trace-table.md`
- Threaded-runtime deviations:
  - `docs/threaded-runtime-deviations.md`
