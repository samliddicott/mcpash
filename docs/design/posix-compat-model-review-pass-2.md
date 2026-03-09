# POSIX/COMPAT Model Review Pass 2

Date: 2026-03-09

This pass completes model/design coverage for the remaining clusters from:

- `docs/plans/011-posix-compat-model-review.md`

## Cluster B: Command Resolution and Classification

Goal:
- Move toward one coherent command-classification path shared across execution and reporting builtins.

Applied structure:
- Added reusable command classification helpers in `src/mctash/runtime.py`:
  - `_iter_path_candidates()`
  - `_classify_command_name()`
- Refactored these paths to consume shared classification:
  - `_resolve_external_path()`
  - `_resolve_external_nonexec_path()`
  - `_run_command_builtin()`
  - `_run_type()`
  - `_run_hash()`
  - `_find_in_path()`

Design impact:
- Reduces duplicated lookup logic and drift between `command`, `type`, `hash`, and external execution path discovery.
- Keeps POSIX-mode behavior distinct where needed (e.g. `command -v` non-exec handling policy).

## Cluster D: Fatal/Special-Builtin Control-Flow Model

Goal:
- Centralize policy helpers instead of ad hoc in-method conditionals.

Applied structure:
- Added shared runtime policy helpers:
  - `_is_noninteractive()`
  - `_special_builtin_fatal_status()` (policy anchor for follow-on closure)
- Switched existing checks to helper where touched (e.g. `unset` readonly fatal branch).
- Updated EXIT trap behavior:
  - `_run_exit_trap()` now runs trap action under `_suppress_errexit()`
  - preserves pre-trap script status unless trap explicitly exits.

Design impact:
- Prevents accidental `set -e` fatal propagation from EXIT trap housekeeping commands.
- Creates explicit policy hooks for POSIX 2.8/2.9 closure without row-by-row special-casing.

## Cluster E: COMPAT Era Switch Consolidation

Goal:
- Replace scattered raw `self._bash_compat_level` checks with centralized compatibility predicates.

Applied structure:
- Added compat helpers:
  - `_compat_level()`
  - `_compat_enabled()`
  - `_compat_at_most()`
- Converted representative call-sites in this pass:
  - `read` option-gating checks (`-a/-n/-N/-d/-t/-u/-s/-e/-i`)
  - `unset` assoc-array `[@]` compat<=51 branch
  - `_bash_feature_enabled()` now uses `_compat_level()`

Design impact:
- Improves readability and reduces future regression risk for compat-gated behavior.
- Establishes consistent compatibility control points for upcoming COMPAT row closure.

## Cluster A: Startup/Mode Residual

Status in model phase:
- Startup/mode structure previously reviewed in pass 1.
- No additional structural changes required in this pass.
- Matrix refresh/de-duplication of stale partial notes is intentionally deferred to matrix-gap phase.

## Model Phase Completion State

Model/design phase is complete for clusters A–E:

- A: startup/mode reviewed and baseline-confirmed.
- B: command resolution model refactored to shared classifier.
- C: `time` POSIX dispatch contract implemented (pass 1).
- D: fatal/special-builtin policy hooks and EXIT trap errexit guard added.
- E: compatibility predicate consolidation started with shared helpers and key call-sites.

Next phase (separate):
- test/matrix gap closure and strict row assertion conversion.
