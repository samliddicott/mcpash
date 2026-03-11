# Compile Backend Plan (Dual Runtime)

## Objective

Add a compile-to-Python execution backend that complements the existing threaded interpreter, while preserving current behavior and parity gates.

## Why Now

- POSIX matrix lane is currently closed.
- ASDL/LST path is stable enough to introduce a second backend without moving targets.
- We can add compiled coverage incrementally with strict fallback to interpreter.

## Non-Goals (initial tranche)

- No immediate replacement of threaded interpreter.
- No immediate optimization-only compiler work.
- No one-shot full interactive/job-control compile parity in tranche 1.

## Core Design

### Backend boundary

Introduce an execution backend interface used by runtime dispatch:

- `interpreter` backend (current default)
- `compiled` backend (opt-in initially)

Selection policy:

- per-script default backend
- per-node compile eligibility
- fallback on unsupported nodes/constructs to interpreter

### Compile unit and artifacts

- Input: ASDL command/list nodes (canonical parsed representation)
- Middle: small typed IR for shell control/data effects
- Output: Python function objects (code objects cached by source hash + mode key)

Initial compile output contract:

- returns shell status code
- receives runtime context object
- uses runtime APIs for side effects (env, fd, jobs, traps, subprocess)

### Safety model

- compile eligibility check is explicit and conservative
- any compile-time uncertainty => fallback to interpreter
- runtime exceptions in compiled path map to same shell diagnostics/status semantics

## Namespace and Mode Model (requested)

We will make namespace/mode explicit and first-class for both parse and execution.

### Namespaces

Support namespace keys such as:

- `bash`
- `bash-<version>` (e.g. `bash-5.0`, policy-gated)
- `ash`
- `sh`
- `posix`

### Resolution

Every callable/definition gets a namespace affinity:

- shell functions: tagged with namespace at definition time
- builtins: capability table by namespace
- compiled units: cache key includes namespace + compat level

Resolution order (draft policy):

1. exact current namespace
2. mapped compatibility namespace (e.g. `bash-5.0 -> bash`)
3. baseline namespace (`sh`/`posix`) when declared compatible

### Mixed-source operation

Allow mingling script sources with different dialect intents by explicit entry policy:

- file-level namespace default (from invocation mode / shebang / options)
- optional function-level namespace override annotation (future)
- call boundary preserves caller runtime state but resolves callee semantics by its namespace tag

## Name lookup / symbol semantics

Unify symbol lookup model used by both backends:

- variable scope stack and export visibility
- function table keyed by `(name, namespace)`
- builtin dispatch keyed by `(name, namespace)`
- command lookup rules remain mode-sensitive and shared

## Phased Plan

## Phase 1: Backend skeleton and guardrails

1. Add backend interface and dispatch hooks.
2. Add compile cache keyed by source+mode+namespace.
3. Add strict fallback with reason logging (`MCTASH_COMPILE_DEBUG=1`).
4. Add parity harness switch to run same tests in both backends.

Exit criteria:

- No behavior change in interpreter mode.
- Compiled mode executes no-op/minimal eligible nodes and falls back otherwise.

## Phase 2: Compile subset (core simple execution)

1. Compile simple command lists without redirection complexity.
2. Compile basic and/or and if/while control flow.
3. Delegate expansions/assignments to existing runtime APIs initially.
4. Keep here-doc/redirection/pipeline as fallback until explicit tranche.

Exit criteria:

- Target matrix subset passes identically in compiled mode.
- Fallback reasons are deterministic and documented.

## Phase 3: Data/control deepening

1. Add compiled redirection/pipeline orchestration via runtime adapters.
2. Add compiled assignment/expansion paths where semantics are already centralized.
3. Add trap/job-control boundary guards (compile where safe, fallback where not).

Exit criteria:

- Expanded parity subset in compiled mode with no new divergence rows.

## Phase 4: Namespace-aware compilation

1. Add namespace tags to function definitions and compiled artifacts.
2. Add mode/namespace-aware callable and builtin resolution.
3. Add mixed-source tests (ash+bash namespace coexistence).

Exit criteria:

- Mixed namespace cases deterministic and documented.

## Phase 4 Policy Note (Deferred)

Status: deferred until later milestone planning.

Rationale for deferral:

- We need a clearer product policy for what namespace separation is meant to
  achieve in user-facing behavior.
- Implicit per-function semantic switching (for example ash-mode `echo`
  behavior in one function and bash-mode `echo` behavior in another) risks
  surprising, hard-to-debug execution.

Current policy direction captured for later implementation:

1. Default to one active semantic lane per execution context (`ash/posix` or
   `bash`) for predictability.
2. Use namespace tags first for provenance, resolution, and compile-cache
   partitioning; do not silently alter builtin semantics based only on callee
   origin.
3. If cross-lane execution is needed, require explicit invocation boundaries
   (opt-in), not implicit behavior changes.

## Testing and Gates

For each phase:

- Run existing matrix in interpreter mode (control).
- Run selected matrix slice in compiled mode.
- Add dual-backend comparator report:
  - interpreter vs bash/ash comparator
  - compiled vs bash/ash comparator
  - interpreter vs compiled self-parity

## Deliverables

- `docs/design/compile-backend-architecture.md`
- `docs/design/namespace-resolution-model.md`
- backend toggles and harness docs in top-level README
- gap report for compiled-mode coverage vs interpreter-mode coverage

## Open Decisions

1. Namespace override syntax for per-function tagging (comment pragma vs keyword vs metadata file).
2. How broad `bash-<version>` support should be in milestone scope.
3. Whether compiled mode becomes default before milestone-2 close.
