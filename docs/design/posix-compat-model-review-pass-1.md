# POSIX/COMPAT Model Review Pass 1

Date: 2026-03-09
Scope: model/design review against:

- `https://tiswww.case.edu/php/chet/bash/POSIX`
- `https://tiswww.case.edu/php/chet/bash/COMPAT`

This pass is implementation-structure review first. Matrix status updates are deferred to the later test/matrix phase.

## Cluster A: Startup + Mode Initialization

Relevant source rows:

- POSIX core items `1`, `2` (`BPOSIX.CORE.001`, `BPOSIX.CORE.002`)

Primary code areas:

- `src/mctash/main.py`
  - `_resolve_invocation_mode`
  - `_apply_invocation_mode`
  - `_source_startup_files`
  - option parse/apply path in `main()`
- `src/mctash/runtime.py`
  - runtime env seed from `os.environ`

Current model:

- Invocation mode chosen by explicit option/name/env override.
- POSIX mode sets `MCTASH_MODE=posix`, sets `POSIXLY_CORRECT=y`, and sets startup `posix` option.
- Startup file model:
  - POSIX interactive: source `ENV`
  - bash interactive: source `~/.bashrc`
  - bash non-interactive: source `BASH_ENV`

Review note:

- Targeted comparator run for rows `001` and `002` is currently green in focused lane; matrix notes still show partial and should be refreshed in the matrix phase.

## Cluster B: Command Resolution + Classification

Relevant source rows:

- POSIX items `18`, `20`, `21`, `70`
- COMPAT command-related deltas (`31/32/40/50/51` command rows)

Primary code areas:

- `src/mctash/runtime.py`
  - command execution dispatch (`_exec_simple_asdl` / simple command path)
  - lookup and reporting builtins (`command`, `type`, `hash`)
  - command hash state (`self._cmd_hash`)

Current model risk:

- Resolution, cache, and reporting logic is distributed.
- Need a single shared lookup model object/function used by:
  - execution path,
  - `command -v/-V`,
  - `type`,
  - `hash` insert/refresh behavior.

## Cluster C: `time` Parse/Dispatch Contract

Relevant source rows:

- POSIX items `6`, `7`
- COMPAT `41.001`

Primary code areas:

- parser reserved-word path + runtime handling of `time`.

Current known mismatch:

- `BPOSIX.CORE.007` still mismatches (`time -p` lane).

Model requirement:

- Explicitly define when `time` is a reserved word vs plain command in POSIX mode.
- Ensure status/diagnostic behavior is mode-consistent.

Applied in this pass:

- Added POSIX-mode dispatch gate so `time` with next token beginning `-` is not dispatched as shell builtin timing and instead follows utility-command lookup path.
- Focused comparator run for `bash-posix-doc-007` is now green.

## Cluster D: Fatal Error + Special Builtin Exit Policy

Relevant source rows:

- POSIX items `32..40`, `72`, `73`

Primary code areas:

- `src/mctash/main.py` top-level non-interactive control flow.
- `src/mctash/runtime.py` fatal-error signaling and special-builtin handling.

Current model risk:

- Exit/fatal behavior decisions are spread across parse/runtime call sites.
- Need one centralized fatal-policy gate that accepts:
  - error class,
  - special builtin context,
  - mode (`posix` / default),
  - interactive vs non-interactive.

## Cluster E: COMPAT Era Switching Model

Relevant source rows:

- COMPAT rows `41.x`, `42.x`, `43.x`, `44.x`, `50.x`, `51.x`, `52.x`

Primary code areas:

- expansion engine and parser behaviors gated on `BASH_COMPAT`.

Current model risk:

- Partial, row-local switches can drift.
- Need grouped feature-switch modules by family:
  - quoting/brace rules,
  - arithmetic/subscript multi-eval behavior,
  - command parsing compatibility toggles,
  - builtin behavior deltas.

## Implementation Order (Model-First)

1. Cluster C (`time`) — smallest hard mismatch with clear parser/runtime boundary.
2. Cluster B (command resolution) — high leverage for many POSIX/COMPAT rows.
3. Cluster D (fatal policy) — closes many non-interactive semantics rows coherently.
4. Cluster E (compat switch consolidation) — reduce future regression surface.
5. Cluster A matrix refresh + any residual startup adjustments.

## Transition to Matrix/Test Phase

After model updates above:

1. Re-run full matrix lanes.
2. Update stale row notes/status.
3. Convert remaining scaffold rows to strict assertions cluster-by-cluster.
