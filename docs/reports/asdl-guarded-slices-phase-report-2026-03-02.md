# ASDL Guarded Slices Phase Report (2026-03-02)

## Scope

This report covers the guarded-slice execution phase focused on ASDL-native word expansion coverage while preserving ash-visible behavior.

## Completed In This Phase

1. Guarded native `argv` widening:
   - safe unquoted `$name` subset
   - safe unquoted `${name...}` subset
   - preserved fallback for risky split/glob/process-substitution forms

2. Guarded native `case` widening:
   - value/pattern safe subset coverage (with fallback retained)

3. Guarded native redirect target path:
   - ASDL `target_word` metadata used for native-safe redirection expansion
   - process-substitution compatibility preserved

4. Guarded native assignment-rhs widening:
   - single-quoted-safe literal support in guarded rhs subset

5. Runtime error-status consistency:
   - additional ASDL simple-command execution catch points now route through unified status mapping helper for behavioral parity (`bad substitution`/`unbound` => status 2)

6. Regression evidence expansion:
   - added/updated argv guardrail rows (split/scalar/quoted semantics)
   - retained bad-substitution behavior checks across command/for/case/redirection contexts

## Key Fix During Stabilization

An ASDL-native argv guard initially allowed a mixed quoted+glob process-substitution shape (`"$d"/*.out`) onto native path, which disabled expected pathname expansion in that mixed case and broke stress rows.

Resolution:

- keep such mixed process-subst/glob words on legacy argv path via stricter guard.
- parity restored in both regression and BusyBox parity modules.

## Validation Evidence

Executed after final guarded updates:

- `PYTHONPATH=src tests/regressions/run.sh` (pass)
- `src/tests/run_busybox_ash.sh run ash-quoting ash-vars ash-parsing ash-psubst` (pass, `ok=137 fail=0 skip=0`)

## Current State

- Guarded ASDL-native coverage has expanded without changing expected ash behavior for validated corpora.
- Legacy fallback remains intentionally active for high-risk expansion shapes not yet parity-proven.
- Remaining work is now primarily controlled widening of those fallback regions with test evidence per slice.
