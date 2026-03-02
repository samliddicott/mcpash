# Threaded Runtime Deviations (vs fork-first ash/dash model)

Date: 2026-02-28

This project intentionally uses a threaded execution model in places where traditional ash/dash shells use process forking.

## Why this exists

- Project direction requires thread-oriented execution semantics for the broader Python interop design.
- This introduces behavior differences from strictly process-isolated shells.

## Current model

- Background jobs and some subshell-like execution paths can run in threads.
- Signal/trap behavior has been aligned to pass BusyBox ash corpus, but internals differ.
- Runtime now uses per-thread subshell-depth tracking and thread-local job context.
- Background worker threads now attempt Linux `unshare(CLONE_FS|CLONE_FILES)` to isolate cwd/fd side effects from the parent thread.

## Pipeline execution model

- Behavioral target remains ash/POSIX-visible semantics from the running script.
- Implementation is hybrid:
  - External-only pipeline stages use OS pipes + subprocess children (fork/exec under `subprocess.Popen`).
  - Pipelines that require shell semantics (builtins/functions/compound stages) run through an in-process ASDL pipeline path with subshell-like stage isolation.
- This avoids unsafe low-level fork patterns in a multithreaded Python runtime while preserving tested shell-visible behavior.
- Memory guardrail:
  - BusyBox harness wrapper applies per-process virtual-memory limit (`ulimit -Sv`, default `MCTASH_MAX_VMEM_KB=262144`).
  - Policy: if limit trips, stop and investigate leak/regression before increasing the limit.

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

## Current tested guarantees

- Parent cwd remains stable while a background subshell performs `cd`:
  - `tests/diff/cases/man-ash-thread-cwd.sh`
- Parent cwd remains stable while a background pipeline performs `cd`:
  - `tests/diff/cases/man-ash-thread-pipeline-cwd.sh`
- Parent fd table does not retain background-opened fd entries from subshell `exec` redirections:
  - `tests/diff/cases/man-ash-thread-fd.sh`
- Parent fd table does not retain background-opened fd entries from pipeline-side `exec` redirections:
  - `tests/diff/cases/man-ash-thread-pipeline-fd.sh`
- Parent variable scope does not receive background subshell variable mutations:
  - `tests/diff/cases/man-ash-thread-vars.sh`

Runtime diagnostics knobs:

- `MCTASH_UNSHARE_MODE=off` disables Linux `unshare(CLONE_FS|CLONE_FILES)` in background worker threads.
- `MCTASH_UNSHARE_MODE=fail` forces the fallback diagnostic path (test hook).
- `MCTASH_THREAD_DIAG=1` emits one-time fallback diagnostics when unshare is disabled/unavailable/fails.

Process-substitution thread-edge regressions:

- `tests/regressions/run.sh`:
  - `process_subst_input_basic`
  - `process_subst_output_basic`
  - `process_subst_cwd_isolation`
  - `process_subst_fd_isolation`
  - `thread_combined_bg_pipeline_process_subst`
  - `thread_multi_job_concurrency_isolation`
  - `thread_unshare_forced_fail_diag`
  - `thread_high_load_concurrency_isolation`
  - `monitor_mode_noninteractive_diag`

## Operational policy

- Behavioral target remains ash/POSIX externally.
- When divergence is discovered:
  1. Reproduce with BusyBox ash test or dedicated regression.
  2. Check POSIX text + rationale + `man ash`.
  3. Prefer behavior-compatible fix first.
  4. If incompatibility is intrinsic to thread model, document it here and in conformance docs.

## Open work

- Expand thread-sensitive coverage to long-running mixed workloads (concurrent background jobs + repeated process substitutions).
- Add explicit failure-mode reporting for specific unshare errno classes where behavior differs materially.
- Add interactive/pty-backed monitor-mode behavior coverage beyond non-interactive diagnostics.
