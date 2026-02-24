# Conformance Matrix (2026-02-23)

This is a practical conformance snapshot, not a formal certification report.

Evidence used:

- BusyBox `ash_test` via `src/tests/run_busybox_ash.sh`
- POSIX Shell Command Language (Issue 8, 2024):  
  `https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/V3_chap02.html`
- POSIX rationale (XCU C.2):  
  `https://pubs.opengroup.org/onlinepubs/9699919799/xrat/V4_xcu_chap02.html`
- `man ash` (local `dash` man page)

Latest corpus result:

- BusyBox `ash_test`: `ok=343 fail=0 skip=0` within the configured timeout window.
- `ash-z_slow/many_ifs.tests` can exceed the harness timeout budget.

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
- Interactive/editor/job-control flags (`-i`, `-m`, `-V`, `-E`, etc.): `partial`/`not target` for this milestone.
- Startup CLI option parity with `ash` synopsis: `partial` (mctash CLI currently focuses on script execution + `--dump-lst`).
- Builtins exercised by BusyBox ash corpus: `implemented for tested semantics`.

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

## Next Conformance Work

1. Add a POSIX requirement-to-test trace table (section-by-section references to tests).
2. Add startup option parity (`-aCefnuvxIimqVEbp`, `-o/+o`) where in scope.
3. Run/select additional corpus slices from Oil POSIX spec tests for independent confirmation.
4. Continue reducing documented threaded-runtime deviations where behavior-compatible fixes exist.

Current trace table:

- `docs/posix-trace-table.md`
- Threaded-runtime deviations:
  - `docs/threaded-runtime-deviations.md`
