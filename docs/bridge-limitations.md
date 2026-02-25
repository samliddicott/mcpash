# Bridge Limitations (Milestone-2)

This file tracks intentionally deferred or partial items in the shell/Python bridge.

## Deferred

- Shared variable process-level visibility (`shared` across true subshell/process boundaries) is not implemented yet.
- Full typed shell arrays/associative arrays are not implemented as first-class shell variables; bridge type conversion for those is partial.
- Full `PYTHON` command-line shell-syntax integration for inline pipeline terminator forms (e.g. placing `|` on the `END_PYTHON` line) is not supported.

## Partial

- Tie type support includes `scalar`, `integer`, `array`, `assoc`, but non-scalar shell-side representation remains string-based.
- `sh.stack` frame model is available and includes function names, but does not yet expose a complete call-frame model equivalent to mature shells.

## In Progress

- End-to-end conformance gating: regressions + Oil subset are integrated; full BusyBox run-all remains timeout-bounded in local runs.
