# Bridge Limitations (Milestone-2)

This file tracks intentionally deferred or partial items in the shell/Python bridge.

## Deferred

- In ash/POSIX mode, typed shell arrays/associative arrays remain out of scope.
- In ash/POSIX mode, bridge/tie support for `array` and `assoc` remains rejected by runtime checks.
- Bash-compat mode (`BASH_COMPAT` set) now enables initial list/dict projection and tie `array`/`assoc` behavior.
- Full bash-level array/hash semantics are still in progress; current support is a compatibility slice, not complete parity.

## Partial

- `sh.stack` frame model is available and includes function names, but does not yet expose a complete call-frame model equivalent to mature shells.

## In Progress

- End-to-end conformance gating: regressions + Oil subset are integrated and full BusyBox run-all passes locally, but runtime remains bounded by configured timeout.
