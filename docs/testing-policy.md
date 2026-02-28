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

By default the test run is fail-fast (`RACE_FAIL_FAST=1`): the test run exits on first mismatch and logs mode/iteration.

Optional diagnostic mode (`RACE_FAIL_FAST=0`) continues running to report pass/fail counts, but still exits non-zero if any failure occurred.

Default mode is `auto`. Additional unshare modes (`off`, `fail`) can be enabled for exploratory fault-finding and are expected to reveal fallback-path bugs until closed.

## Parity Summary Contract

- `make parity-summary` produces `docs/reports/parity-summary.json`.
- `make parity-summary-validate` enforces a stable JSON contract for tooling and report consumers.
- Schema source: `docs/reports/parity-summary.schema.json`.
- For fast local checks, `PARITY_SKIP_BUSYBOX=1 make parity-summary-validate` runs bridge+diff steps and marks BusyBox as skipped in the summary.
