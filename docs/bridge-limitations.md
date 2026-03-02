# Bridge Limitations (Milestone-2)

This file tracks intentionally deferred or partial items in the shell/Python bridge.

## Deferred

- Full typed shell arrays/associative arrays are deferred until Bash-compat mode is introduced.
  Current ash-target path remains scalar-only by design.
- Bridge/tie support for `array` and `assoc` is deferred with shell array/hash runtime support.
- Future enablement should be behind an explicit Bash-extension option (e.g. `set -o bash_ext` or equivalent).
- Any list/dict bridge behavior in ash mode is non-normative and should be rejected by runtime checks.

## Partial

- `sh.stack` frame model is available and includes function names, but does not yet expose a complete call-frame model equivalent to mature shells.

## In Progress

- End-to-end conformance gating: regressions + Oil subset are integrated and full BusyBox run-all passes locally, but runtime remains bounded by configured timeout.
