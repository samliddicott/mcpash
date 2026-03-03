# POSIX and `BASH_COMPAT` Mode Policy

Date: 2026-03-03

## Goal

Define how `--posix` and `BASH_COMPAT` interact for mctash as we add Bash-compat features without regressing ash/POSIX behavior.

## Observed Bash Baseline

Local probe against GNU Bash 5.1.16 shows:

- `bash --posix` keeps POSIX mode enabled.
- `declare -a` still works in `--posix` mode.
- `declare -A` still works in `--posix` mode.
- `BASH_COMPAT` accepts numeric compatibility levels matching supported versions (e.g. `50`, `51` on Bash 5.1).
- `BASH_COMPAT` does not disable array facilities in `--posix` mode.

This means Bash allows extension behavior to coexist with POSIX mode for some features.

## mctash Policy

1. `--posix` remains the default correctness anchor for ash/POSIX behavior.
2. `BASH_COMPAT` becomes the explicit extension gate selector.
3. In `--posix` mode, Bash-compat features MAY be enabled only when `BASH_COMPAT` is set to a supported level and feature gate allows it.
4. Feature enablement is per-feature, not global all-or-nothing.
5. Unsupported or invalid `BASH_COMPAT` values should produce clear diagnostics and fall back to no extension enablement.

Current startup defaults:
- Default invocation mode is bash-mode.
- In bash-mode, `BASH_COMPAT` is auto-set to `50` when unset.
- Invocation names `sh`/`ash`/`dash` force POSIX mode.
- Invocation names `mctash`/`ptash`/`bash` force bash-mode.

## Initial Feature-Gate Plan

Near-term staged behavior:

- Stage A: parse and expose `BASH_COMPAT`; no feature behavior changes.
- Stage B: gate `declare -a` under compat policy.
- Stage C: gate `declare -A` when associative runtime support is available.
- Stage D: gate bridge list/dict and tie `array`/`assoc` on the same policy.

## Current Status

- Stage A in progress:
  - `--posix` startup option is parsed and applied.
  - `-o posix` is accepted in startup option parsing/listing.
  - `BASH_COMPAT` is currently passed through as environment-visible input for upcoming feature gates.
- Stage B partial:
  - `declare -a NAME` is gated by `BASH_COMPAT` and now succeeds when compat is set (e.g. `BASH_COMPAT=50`), including under `--posix`.
  - without `BASH_COMPAT`, `declare -a` fails with explicit diagnostics.
- Stage C partial:
  - `declare -A NAME` is now minimally accepted under `BASH_COMPAT` (attribute-level declaration only).
  - without `BASH_COMPAT`, `declare -A` fails with explicit diagnostics.
  - full associative variable semantics remain pending.

## Test Strategy

- Add matrix tests that run both Bash and mctash for:
  - plain mode
  - `--posix`
  - `--posix` + `BASH_COMPAT`
- Keep initial mctash checks non-gating (soft mode) while implementation lands.
- Enable strict parity mode once each feature gate is implemented.

Current harness status:
- `make compat-posix-bash` runs the reference/progress matrix.
- `make compat-posix-bash-strict` enables strict Bash-vs-mctash parity checks for the gated declaration/indexed/assoc slice, with mirrored `BASH_COMPAT` and `--posix`.
