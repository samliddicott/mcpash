# Milestone 2 Wrap-Up (2026-03-03)

## Completed in this closure pass

- `read` matrix closure for declared comparator set:
  - `make read-matrix`
  - ash-family lane (`ash`, `dash`, optional `busybox ash` with documented option-surface skip)
  - bash lane with `bash --posix` and full bash-mode `read` options:
    - `-a -d -e -i -n -N -p -r -s -t -u`
- `read` extension added:
  - `shopt -s read_interruptible`
  - blocking `read` can return on incoming signal (`128+signal`, e.g. `130` for `INT`)
- `fc` comparator policy accepted for this milestone:
  - when comparator `ash` has no `fc`, use temporary bash comparator for `fc` differential checks.
- `ulimit` parity expansion for current ash target:
  - query/set/error/list coverage widened with safe test caps.
  - expanded flag surface in runtime and tests (`c d f l m n p s t v` + `H/S/a` behavior for this target).

## Deferred to next milestone

- Full interactive job-control closure (currently matrix harness exists; strict parity not yet enforced).
- Full trap universe closure including interactive/platform-specific edge space.
- Remaining POSIX trace/grammar rows still marked `partial`.

## Current validation

- `make diff-parity-matrix`: green (`ash lane rc=0`, `bash lane rc=0`)
- `make read-matrix`: green
- `make jobs-interactive-matrix`: green in informational mode (`STRICT=0`)
- `make trap-noninteractive-matrix`: green in informational mode (`STRICT=0`)
- `make trap-interactive-matrix`: green in informational mode (`STRICT=0`)
- `make trap-variant-matrix`: report generated at `docs/reports/trap-variant-matrix-latest.md`
