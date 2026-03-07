# Job Control Runtime Model (C8.JOB.14-29)

## Scope
This note maps `JOB CONTROL` requirement rows `C8.JOB.14` through `C8.JOB.29` to runtime design responsibilities before implementation changes.

## Runtime Components
- `runtime._run_external` / pipeline launcher: process creation, fg/bg launch, wait behavior.
- Job table store: job id, jobspec metadata, state, process-group id, member pids.
- Jobspec resolver: `%n`, `%+`, `%-`, `%`, `%prefix`, `%?substr`.
- Interactive loop + signal handling: terminal-driven signals, prompt return path.
- Notification/reporting path: deferred/immediate job-status emission.
- `wait` builtin path: state-change vs termination semantics.

## Data Model (Target)
- `Job`:
  - `job_id: int`
  - `pgid: int | None`
  - `leader_pid: int | None`
  - `member_pids: list[int]`
  - `cmdline: str`
  - `state: running | stopped | done`
  - `current_flag: bool`
  - `previous_flag: bool`
- Indexes:
  - `job_id -> Job`
  - `pid -> job_id`
  - cached current/previous job ids

## Row Mapping
| Req | Requirement | Runtime owner | Design intent | Tests |
|---|---|---|---|---|
| `C8.JOB.14` | pipeline -> one job entry | pipeline launcher + job table | create one `Job` per launched pipeline | existing `man-bash-posix-10-jobs-fg-bg-interactive.sh`; add strict row case |
| `C8.JOB.15` | async launch banner `[job] pid` | background launch path | print job id + last pipeline pid | existing interactive jobs case; add strict banner case |
| `C8.JOB.16` | same pipeline shares one pgid/job | launcher + preexec | assign/track one pgid for pipeline | new `bash-man-jobcontrol-pgrp-pipeline.sh` |
| `C8.JOB.17` | fg pgrp receives keyboard SIGINT | tty + signal routing | route INTR to fg process group, not shell | `run_interactive_sigint_matrix.sh`, new foreground-signal case |
| `C8.JOB.18` | bg tty read -> SIGTTIN stop | kernel/tty interaction + state updates | observe stop and mark job `stopped` | new `bash-man-jobcontrol-sigttin.sh` |
| `C8.JOB.19` | bg tty write with tostop -> SIGTTOU stop | tty interaction + state updates | same as above for write path | new `bash-man-jobcontrol-sigttou.sh` |
| `C8.JOB.20` | `^Z` stops fg and returns prompt | interactive signal path + fg handoff | stop fg job, recover shell control | new `bash-man-jobcontrol-suspend-z.sh` |
| `C8.JOB.21` | `^Y` delayed suspend behavior | interactive signal path | delayed suspend observable on terminal read | new `bash-man-jobcontrol-suspend-y.sh` |
| `C8.JOB.22` | jobspec core forms | jobspec resolver | deterministic current/previous resolution | new `bash-man-jobcontrol-jobspec-core.sh` |
| `C8.JOB.23` | jobspec prefix/substring + ambiguity errors | jobspec resolver | bash-like match and error text class | new `bash-man-jobcontrol-jobspec-match.sh` |
| `C8.JOB.24` | `%jobspec` command forms map to fg/bg | parser/dispatcher + jobspec resolver | `%1` == `fg %1`, `%1 &` == `bg %1` | new `bash-man-jobcontrol-jobspec-command-forms.sh` |
| `C8.JOB.25` | deferred notifications vs `set -b` | notification queue + prompt boundary | default defer until prompt; immediate when notify enabled | existing monitor tests + new notify timing case |
| `C8.JOB.26` | `trap SIGCHLD` per child | SIGCHLD handling + trap dispatch | one trap evaluation per exiting child | existing trap matrix + new per-child count case |
| `C8.JOB.27` | exit warning once; second exit terminates stopped jobs | exit path + job table | first exit warns; second exits and terminates | new `bash-man-jobcontrol-exit-warn.sh` |
| `C8.JOB.28` | `wait` returns on state change (job-control on) | `wait` builtin | return on stop/continue transitions | new `bash-man-jobcontrol-wait-state-change.sh` |
| `C8.JOB.29` | `wait -f` waits for termination | `wait` builtin | block until done, ignoring mere state change | new `bash-man-jobcontrol-wait-f.sh` |

## Implementation Slices
1. **Core model slice**: `C8.JOB.14-16,22-24` (job table + jobspec resolver + pgid tracking).
2. **Foreground signal/TTY slice**: `C8.JOB.17,20,21` (fg pgrp handoff, interrupt/suspend parity).
3. **Notification/exit slice**: `C8.JOB.25,27` (deferred vs immediate notices; exit warnings).
4. **Wait/trap slice**: `C8.JOB.26,28,29` (`SIGCHLD` accounting and wait semantics split).
5. **TTY stop conditions**: `C8.JOB.18-19` (`SIGTTIN`/`SIGTTOU` behavior under PTY setup).

## Known Blockers / Risk
- Full parity for `C8.JOB.17` requires explicit foreground process-group control (`tcsetpgrp`) and robust restoration paths.
- `C8.JOB.18-19` may need tighter PTY harness control to deterministically trigger SIGTTIN/SIGTTOU.
- `C8.JOB.21` (`^Y`) is terminal-driver dependent and should be validated with strict comparator scope notes.

## Remaining Open Rows (Post-Tranche)
- `C8.JOB.17`: still partial (foreground process-group signal routing).
- `C8.JOB.18-19`: still partial (TTY stop semantics `SIGTTIN`/`SIGTTOU`).
- `C8.JOB.20-21`: still partial (suspend control chars and delayed suspend behavior).
- `C8.JOB.26`: covered (CHLD trap delivery and wait-status interruption behavior now parity-backed against bash comparator).
- `C8.JOB.27`: covered (checkjobs warning-once + second-exit stopped-job termination path is implemented and matrix-verified).
- `C8.JOB.28-29`: covered (`wait` now uses explicit state model for stop-transition return; `wait -f` remains termination-only).

## Progress Notes
- Implemented resolver support for jobspec core and match forms:
  - `%%`, `%+`, bare `%`, `%-`
  - `%name` prefix match
  - `%?text` substring match
- Implemented `%jobspec` and `%jobspec &` command-form dispatch hooks in list-item execution paths.
- Added comparator cases:
  - `tests/diff/cases/bash-man-jobcontrol-jobspec-core.sh`
  - `tests/diff/cases/bash-man-jobcontrol-jobspec-match.sh`
- `C8.JOB.24` is now parity-covered for shorthand dispatch (`%jobspec`/`%jobspec &`) including redirect-safe forms in non-interactive and PTY interactive lanes.
- `C8.JOB.16` is parity-covered at current runtime scope via interactive pipeline-to-single-job assertions (`run_jobs_interactive_matrix.sh`).
- Added `run_job_notify_matrix.sh` coverage for notification emission behavior (`C8.JOB.25`), while keeping precise deferred-vs-immediate timing semantics partial.
- Added and extended `run_job_exitwarn_matrix.sh` coverage for interactive `exit` warning/continue behavior and second-exit stopped-job termination (`C8.JOB.27`).
