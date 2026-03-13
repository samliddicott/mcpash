# 014 - ASDL Native Execution Closure

## Objective

Close the remaining non-ASDL execution lanes and legacy text-expansion fallbacks so shell execution is ASDL-native end-to-end.

## Current State

- Parser/eval loop is ASDL-first:
  - `Runtime._eval_source(...)` maps `last_lst_item -> ASDL -> _exec_asdl_list_item(...)`.
  - `Runtime._run_source(...)` does the same for sourced files.
- Remaining legacy lanes still exist:
  - Legacy AST execution entrypoint: `Runtime.run(script)` -> `_exec_list(...)`.
  - Legacy AST function storage/execution fallback: `self.functions` / `_run_function(...)` fallback.
  - Legacy text-word parser in expansion paths: `_legacy_word_to_expansion_fields(...)` and callers.

## Guardrails Added

- `MCTASH_STRICT_ASDL=1`:
  - disables `Runtime.run(Script)` legacy AST entrypoint.
  - disables legacy AST-only function body execution.
- runtime counters:
  - `runtime.run.ast_script`
  - `function.ast_body`

These counters let us measure any remaining runtime dependence before removing paths.

## Closure Plan

1. Deprecate AST runtime entrypoints
   - Keep strict mode available by default for CI lane.
   - Add tests that strict mode rejects legacy entrypoints with stable diagnostics.

2. Eliminate AST function-body fallback
   - Ensure all function definitions are stored/executed from `functions_asdl`.
   - Remove dual-store assumptions from introspection paths after coverage passes.

3. Burn down legacy word parsing usage
   - Inventory all `_legacy_word_to_expansion_fields(...)` callsites.
   - For each callsite, replace with ASDL-native structured expansion path.
   - Keep any temporary fallback behind explicit feature flags and tracked row IDs.

4. Final removal phase
   - Remove `Runtime.run(Script)` AST execution path.
   - Remove `self.functions` AST storage lane.
   - Remove legacy parser imports only after gates prove clean.

## Exit Criteria

- No runtime hits in legacy counters across standard parity gates.
- `MCTASH_STRICT_ASDL=1` passes all core gates used for CI.
- No `Runtime.run(Script)` or AST function fallback path reachable in normal shell execution.
