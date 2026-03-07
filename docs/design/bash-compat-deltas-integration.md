# Bash COMPAT Delta Integration Design

Source:
- `https://tiswww.case.edu/php/chet/bash/COMPAT`

Companion specs:
- `docs/specs/bash-compat-deltas-requirements.tsv`
- `docs/specs/bash-compat-deltas-implementation-matrix.tsv`

## Intent
Use COMPAT deltas as:
1. feature requirements,
2. targeted comparator-test seeds,
3. design hints for ownership (`parser` vs `expand` vs `runtime`).

## Scope Policy
- `deferred_level_support`:
  - legacy compatibility levels not currently targeted for full emulation.
  - still tracked and testable as explicit behavior rows.
- `in_scope_now`:
  - current operational levels (50+ row family) tied to `BASH_COMPAT` handling now.

## Row Model
- IDs: `BCOMPAT.<level>.<index>`
- Rows are cumulative by level (as documented by Bash).
- Matrix status starts `partial` until a row has explicit comparator evidence.

## Next Execution Slice
1. Add focused comparator tests for selected rows:
   - `BCOMPAT.41.001` (`time` in POSIX mode),
   - `BCOMPAT.42.002` (single-quote behavior in `${...}` word),
   - `BCOMPAT.43.001` (word-expansion fatality model),
   - `BCOMPAT.50.001` (`RANDOM` sequence behavior under `BASH_COMPAT`).
2. Promote rows to `covered` only with row-level evidence.
3. Keep coverage reports split by:
   - baseline current behavior,
   - explicit `BASH_COMPAT` mode probes.
