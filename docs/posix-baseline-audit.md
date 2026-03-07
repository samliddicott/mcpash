# POSIX Baseline Audit (Before Next Iteration)

## Sources Used

- POSIX Shell Command Language (Issue 8, 2024):
  - https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/V3_chap02.html
- POSIX Shell Rationale (XCU C.2):
  - https://pubs.opengroup.org/onlinepubs/9699919799/xrat/V4_xcu_chap02.html
- Bash Reference Manual, "6.11 Bash and POSIX":
  - https://tiswww.case.edu/php/chet/bash/POSIX
- `man ash` (local: dash/ash manual)
- BusyBox `ash_test` corpus (executed via `src/tests/run_busybox_ash.sh`)

## Current Behavioral Baseline

Latest timed run snapshot:

- `ok=35`
- `fail=70`
- `skip=0`

(From `/tmp/mctash_iter2.log`, 90s window)

## POSIX-Focused Gap Map

Legend: `implemented`, `partial`, `missing`

- `2.2 Quoting`: `partial`
  - Single/double/backslash basics are present.
  - Missing/incorrect edge behavior across nested command substitution and here-doc interactions.

- `2.3 Token Recognition` + alias substitution: `partial`
  - Tokenization works for core operators and here-doc queueing.
  - Alias timing/context remains incomplete (`ash-alias/*` mostly failing).

- `2.4 Reserved Words`: `partial`
  - Core reserved words recognized.
  - Grammar-context handling is incomplete (notably `case`/pattern contexts, some compound forms).

- `2.5 Parameters and Variables`: `partial`
  - Basic variables and some special parameters work (`$?`, positional args baseline).
  - More special parameter and assignment-environment edge behavior still failing.

- `2.6 Word Expansions`: `partial`
  - Basic parameter expansion, command substitution, arithmetic expansion exist.
  - Field splitting/pathname expansion/quote-removal ordering is not yet fully POSIX-accurate (glob/arithmetic suites mostly fail).

- `2.7 Redirection`: `partial`
  - Core redirects and several here-doc cases pass.
  - Multiple here-doc/ordering/expansion edge cases still fail.

- `2.8 Exit Status and Errors`: `partial`
  - Several error-code paths are corrected (126/127 areas improving).
  - Script/line-qualified diagnostics and trap-related behavior remain incomplete.

- `2.9 Shell Commands` (simple/compound/functions): `partial`
  - `if/while/for/function` basic forms execute.
  - `case` and some `for` grammar variants still failing.

- `2.10 Shell Grammar`: `partial`
  - Handwritten recursive-descent parser handles a subset.
  - Not yet aligned to full POSIX grammar coverage.

- `2.13 Shell Execution Environment` + `2.15 Special Built-ins`: `partial`
  - Builtins coverage improved (`break/continue/command/exec/type` etc.).
  - `getopts`, trap semantics, and some special builtin edge rules are still missing.

## High-Leverage Fix Order (Next)

1. `case` grammar + runtime matching semantics.
2. `for` empty/variant grammar forms.
3. Error reporting format parity (`./script: line N: ...`) for command-not-found, EACCES, bad syntax/open failures.
4. Here-doc POSIX corner cases (quoted delimiters, expansion rules, newline/backslash interactions).
5. Expansion-order correctness (parameter/command/arithmetic -> splitting -> globbing -> quote removal).
6. `getopts`, traps, and exit-code semantics.

## ASDL/LST Alignment Audit (Key to Future Work)

Current state in repo:

- `src/syntax/pybash.asdl` is a **minimal local schema**, not OSH's full ASDL.
- `src/mctash/asdl_map.py` explicitly says **"partial mapping to Oil/OSH ASDL"**.
- Parser/runtime execute from local AST dataclasses, not generated OSH-ASDL typed nodes.

Conflicts vs the "OSH ASDL as foundation" goal:

1. Canonical schema mismatch
- Current canonical executable structure is local dataclasses + minimal local ASDL.
- OSH ASDL node space is only partially emulated in mapping output.

2. Parse result mismatch
- Word/command nodes are not yet fully represented as OSH-style typed nodes end-to-end.
- Some node paths still degrade to `command.NoOp` in mapping.

3. Losslessness mismatch
- LST includes useful positions, but not all token-level fidelity expected for full OSH-style lossless translation.

4. Feature coverage mismatch
- POSIX grammar coverage is incomplete while OSH-style ASDL expects richer command/word forms.

## Decision Needed (Approval)

I need your approval on one of these paths before deeper parser refactoring:

1. **Strict OSH-first (recommended)**
- Promote OSH-compatible ASDL node model to canonical internal representation.
- Keep current AST as temporary compatibility layer only.
- Parser emits LST + OSH-shaped command tree directly.
- Slower short-term, cleaner long-term.

2. **Dual-track transition**
- Keep current executable AST as primary.
- Expand `asdl_map.py` to full OSH parity in parallel.
- Migrate runtime once mapping reaches threshold.
- Faster immediate test progress, longer coexistence complexity.

3. **Ash-parity first, OSH-later**
- Focus only on BusyBox/POSIX compliance first.
- Delay OSH ASDL unification.
- Fastest to test gains, but highest future refactor risk.

My recommendation is option 1 unless you prefer short-term velocity over architecture convergence.
