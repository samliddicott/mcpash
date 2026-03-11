# Compile Backend Architecture (Phases 1-3)

## Goal

Run ASDL list items through either:

- interpreter backend (existing behavior), or
- compiled backend (Python code object + cached callable).

Compiled mode is conservative and falls back to interpreter on any unsupported
shape or runtime-unsafe context.

## Execution Flow

1. Parse script to ASDL list items.
2. Runtime dispatches each list item via `_exec_asdl_list_item`.
3. If backend is `compiled`, runtime checks eligibility and cache.
4. On cache miss, runtime generates and compiles a tiny Python wrapper that
   calls `_exec_compiled_list_item`.
5. Compiled dispatcher executes supported nodes directly through runtime
   command/pipeline helpers.
6. Any compile/build/runtime error falls back to interpreter path.

## Cache Model

Compiled cache key:

- namespace key (`MCTASH_NAMESPACE` override, else mode-derived), and
- SHA-256 digest of canonical ASDL JSON.

This prevents accidental cache collisions across mode/compat namespaces.

## Scope by Phase

- Phase 1: backend boundary + conservative fallback + cache + debug reasons.
- Phase 2: compile-dispatch for list/control-flow (`AndOr`, `If`, `WhileUntil`,
  `BraceGroup`) with equivalent status/errexit/trap integration.
- Phase 3: compiled redirect handling and delegated multi-stage pipeline
  orchestration via existing pipeline adapters.

## Safety Guards

Compiled dispatch is disabled when:

- trap handler execution is active, or
- interactive monitor mode is active.

In both cases runtime emits fallback reasons under `MCTASH_COMPILE_DEBUG=1` and
uses interpreter execution.
