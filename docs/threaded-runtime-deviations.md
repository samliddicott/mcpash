# Threaded Runtime Deviations (vs fork-first ash/dash model)

Date: 2026-02-24

This project intentionally uses a threaded execution model in places where traditional ash/dash shells use process forking.

## Why this exists

- Project direction requires thread-oriented execution semantics for the broader Python interop design.
- This introduces behavior differences from strictly process-isolated shells.

## Current model

- Background jobs and some subshell-like execution paths can run in threads.
- Signal/trap behavior has been aligned to pass BusyBox ash corpus, but internals differ.
- Runtime now uses per-thread subshell-depth tracking and thread-local job context.

## Known deviation classes

1. Process/job-control internals
- Traditional shells rely on process groups and kernel job control primitives.
- Thread-first behavior cannot be identical for all edge cases, especially interactive job control.

2. Environment isolation boundaries
- Fork-based shells get copy-on-write process state naturally.
- Thread-based execution requires explicit snapshot/copy rules to avoid shared-state bleed.

3. Signal delivery model
- Kernel signal delivery targets processes/threads, not shell-language job abstractions.
- Mapping to shell-visible behavior requires adapter logic; some rare edge cases may still differ.

4. FD/CWD lifetime semantics
- Process isolation gives implicit per-process FD/CWD state.
- Thread model requires explicit handling to avoid cross-thread side effects.

## Operational policy

- Behavioral target remains ash/POSIX externally.
- When divergence is discovered:
  1. Reproduce with BusyBox ash test or dedicated regression.
  2. Check POSIX text + rationale + `man ash`.
  3. Prefer behavior-compatible fix first.
  4. If incompatibility is intrinsic to thread model, document it here and in conformance docs.

## Open work

- Add explicit per-thread CWD strategy.
- Add stronger per-thread FD ownership/restoration rules.
- Add dedicated tests for threaded-vs-fork-sensitive scenarios.
