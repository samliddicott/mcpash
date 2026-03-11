# Namespace Resolution Model (Compile Cache)

## Purpose

Compiled artifacts must not be reused across incompatible semantic modes.
Namespace keying isolates compiled cache entries by lane.

## Namespace Key Derivation

Runtime derives a compile namespace key in this order:

1. `MCTASH_NAMESPACE` (explicit override, if set)
2. mode-derived default:
   - `ash` for `MCTASH_MODE=ash|posix` without `BASH_COMPAT`
   - `bash-<level>` when `BASH_COMPAT` is set or `MCTASH_MODE=bash`
   - `sh` fallback

## Where It Is Used

- compile cache key: `(namespace_key, asdl_digest)`

## Rationale

- avoids semantic bleed between ash and bash lanes
- preserves determinism when toggling mode/compat in long-lived runtimes
- gives an explicit escape hatch (`MCTASH_NAMESPACE`) for experiments and
  mixed-source workflows
