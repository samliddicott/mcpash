# 010: Job-Control Focused Tranche

## Scope
Drive closure of remaining job-control rows except `C8.JOB.13`:
- `C8.JOB.17-21`
- `C8.JOB.25-29`

## Strategy
- Build explicit state/event model first.
- Then close rows by policy consumers (`wait`, `trap CHLD`, `exit/checkjobs`, TTY semantics).
- Keep each change commit-sized and comparator-backed.

## Work Phases

1. State/Event Backbone
- Add explicit per-job state map (`running/stopped/done`).
- Add transition/event queue helpers.
- Route launch/completion/kill transitions through helpers.
- No row status promotion in this phase.

2. Wait Semantics
- Implement state-change behavior for `wait`.
- Implement termination-only behavior for `wait -f`.
- Add dedicated strict comparator cases.
- Target rows: `C8.JOB.28`, `C8.JOB.29`.

3. Exit Warning Depth
- Implement second-exit semantics under `checkjobs`.
- Extend interactive exit harness.
- Target row: `C8.JOB.27`.

4. CHLD Trap Delivery
- Event-driven per-child trap dispatch with re-entry guard.
- Add deterministic trap-count comparator case.
- Target row: `C8.JOB.26`.

5. TTY Stop/Suspend
- Add PTY comparator cases for `SIGTTIN`, `SIGTTOU`, `^Z`, `^Y`.
- Implement required state transitions.
- Target rows: `C8.JOB.18-21`.

6. Foreground Process-Group Routing
- Add pgid handoff/restoration path (`tcsetpgrp` when available).
- Extend interactive SIGINT matrix to process-group assertions.
- Target row: `C8.JOB.17`.

## Success Criteria
- Every targeted row has strict comparator evidence.
- Matrix status updates are evidence-backed.
- No changes to `C8.JOB.13` in this tranche.
