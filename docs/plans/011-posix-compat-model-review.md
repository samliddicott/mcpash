# POSIX/COMPAT Model Review Plan

## Scope

This pass is model-first, not test-first.

Source documents driving this pass:

- `https://tiswww.case.edu/php/chet/bash/POSIX`
- `https://tiswww.case.edu/php/chet/bash/COMPAT`

Primary goal:

- Reconcile runtime/parser design with those two sources across existing code paths.
- Only after that, return to matrix/test gap closure.

## Review Method

For each model cluster:

1. Read requirement rows from:
   - `docs/specs/bash-posix-mode-implementation-matrix.tsv`
   - `docs/specs/bash-compat-deltas-implementation-matrix.tsv`
2. Review current implementation structure in `src/mctash/runtime.py` (and parser/ASDL mapping as needed).
3. Produce model notes:
   - current model,
   - source-required behavior,
   - design delta,
   - compatibility switch behavior (default vs `--posix` vs `BASH_COMPAT`).
4. Implement design-coherent changes per cluster (not row-by-row patching).
5. Then run and update matrix evidence.

## Cluster Order (Model Review)

1. Startup and mode initialization model
- Source focus: POSIX items `1`, `2`.
- Current known mismatches:
  - `BPOSIX.CORE.001` (`POSIXLY_CORRECT`)
  - `BPOSIX.CORE.002` (`ENV` startup flow in POSIX mode)
- Code focal areas:
  - startup/invocation path in `src/mctash/runtime.py`
  - mode seeding and environment setup

2. Command resolution and classification model
- Source focus: POSIX items `18`, `20`, `21`, `70` + COMPAT command deltas.
- Code focal areas:
  - builtin/function/external precedence
  - command hash lifecycle and `checkhash`
  - `command`, `type`, `hash` builtins
- Objective:
  - one coherent lookup model shared by execution and reporting builtins.

3. Parser/dispatch model for `time` in POSIX mode
- Source focus: POSIX items `6`, `7`; COMPAT `41.001`.
- Current known mismatch:
  - `BPOSIX.CORE.007` (`time -p` handling/status)
- Objective:
  - explicit parser/runtime contract for reserved-word vs command behavior.

4. Fatal-error and special-builtin control-flow model
- Source focus: POSIX items `32..40`, `72`.
- Objective:
  - unify non-interactive fatal-exit semantics in one control path.

5. COMPAT expression-expansion model (multi-evaluation and quoting eras)
- Source focus: COMPAT `41.x`, `42.x`, `43.x`, `51.x`, `52.001`.
- Objective:
  - centralize compatibility-era behavior switches by feature family.

## Deliverables Before Matrix Gap Pass

- Design notes added/updated for each reviewed cluster.
- Runtime/parser changes applied by cluster.
- Explicit mode-switch policy documented for each affected cluster:
  - default bash mode,
  - `--posix`,
  - `BASH_COMPAT` level gates.

## Exit to Matrix/Test Phase

When clusters 1-5 have model review + implementation pass complete:

1. Re-run matrix gates.
2. Convert remaining scaffold rows to strict row assertions.
3. Continue gap closure in test/matrix mode.

## Status

Model/design phase complete on 2026-03-09:

- Pass 1: `docs/design/posix-compat-model-review-pass-1.md`
- Pass 2: `docs/design/posix-compat-model-review-pass-2.md`
