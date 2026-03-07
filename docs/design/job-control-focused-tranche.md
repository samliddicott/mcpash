# Focused Tranche: Job-Control State/Event Model

## Goal
Close remaining `C8.JOB.*` rows (except `C8.JOB.13`) by moving from ad-hoc job bookkeeping to an explicit state/event model.

## Why
Recent implementation/testing showed that incremental hooks are not enough for:
- foreground signal routing (`C8.JOB.17`)
- tty stop semantics (`C8.JOB.18-19`)
- suspend behavior (`C8.JOB.20-21`)
- CHLD/wait semantics (`C8.JOB.26,28,29`)

## Model

### Job State
- `running`
- `stopped`
- `done`

### Job Events
- `spawned`
- `stopped(sig)`
- `continued`
- `exited(status)`
- `signaled(sig)`

### Invariants
- Exactly one authoritative state per job id.
- `wait` behavior reads state/events, not thread liveness alone.
- Trap dispatch consumes queued child events; no trap recursion/re-entry.
- Notification emission is driven by state transition + policy (`set -b` or prompt boundary).

## Runtime Ownership
- Job state/event store: `Runtime` job-control helpers.
- State transitions: background launch path, kill/bg/fg operations, child completion path.
- Policy consumers:
  - `jobs`
  - `wait` / `wait -f`
  - exit warning logic (`checkjobs`)
  - trap dispatch (`CHLD`)
  - interactive notify path

## Slice Order
1. **State/Event backbone**
   - Add explicit `job_state` + `job_events` store and transition helpers.
   - No behavior claims yet; keep parity stable.
2. **Wait semantics (`C8.JOB.28/29`)**
   - `wait` returns on state change.
   - `wait -f` waits for terminal states only.
3. **Exit/checkjobs depth (`C8.JOB.27`)**
   - Warning + second-exit semantics from state store.
4. **CHLD trap semantics (`C8.JOB.26`)**
   - One trap event per child transition without recursion.
5. **TTY stop/suspend semantics (`C8.JOB.18-21`)**
   - PTY-driven state transitions and comparator gating.
6. **Foreground signal routing (`C8.JOB.17`)**
   - Process-group handoff (`tcsetpgrp`) and robust restore path.

## Evidence Gate
- For each slice:
  - add/extend strict comparator tests first,
  - implement smallest coherent runtime change,
  - run strict matrix,
  - update matrix status and design deltas.

## Explicit Non-Goal In This Tranche
- Do not work `C8.JOB.13` in this sequence.
