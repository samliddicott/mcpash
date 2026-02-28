# Testing Policy

## Intent

Performance tuning and race-stimulation serve different goals and must not be conflated.

- Performance checks (`make perf-baseline`, `make perf-compare`) are for runtime regression detection only.
- Correctness checks (`make regressions`, `make diff-conformance`, BusyBox/Oil gates) are strict functional gates.
- Race-stimulation checks (`make stress-race`) are strict correctness checks run repeatedly to surface rare interleavings.

## Strictness Rules

- A single functional mismatch is a failure.
- Repetition is used to increase race detection probability, not to justify ignoring failures.
- No "pass percentage" threshold is allowed for correctness/race suites.
- Any intermittent failure is treated as a bug and must be investigated.

## Current Race-Stimulation Scope

`tests/stress/race.sh` repeatedly exercises threaded isolation invariants:

- parent CWD isolation
- parent FD isolation
- concurrent pipeline/process-substitution stability
- mixed high-load threaded command execution stability

The suite fails fast on first mismatch and logs the failing mode/iteration.

Default mode is `auto`. Additional unshare modes (`off`, `fail`) can be enabled for exploratory fault-finding and are expected to reveal fallback-path bugs until closed.
