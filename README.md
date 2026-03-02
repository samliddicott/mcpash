# mctash

`mctash` is a Python 3 shell project targeting ash-compatible behavior with an OSH-ASDL-guided parser/runtime path.

## Local Conformance Commands

Run targeted regression checks:

```sh
make regressions
```

Run bridge-only conformance:

```sh
make bridge-conformance
```

Run differential ash vs mctash cases:

```sh
make diff-conformance
```

Run full BusyBox ash corpus:

```sh
make busybox-conformance
```

Run a reproducible local parity gate and emit a machine-readable summary:

```sh
make parity-summary
```

Default summary output: `docs/reports/parity-summary.json`

Validate summary contract for tooling:

```sh
make parity-summary-validate
```

Fast local mode (skip BusyBox step, mark as skipped in JSON):

```sh
PARITY_SKIP_BUSYBOX=1 make parity-summary-validate
```

Create/update a local performance baseline:

```sh
make perf-baseline
```

Compare current performance against saved baseline:

```sh
make perf-compare
```

Useful overrides:

```sh
PERF_RUNS=9 PERF_INCLUDE_BUSYBOX=1 make perf-baseline
PERF_MAX_REGRESSION=1.20 PERF_MIN_DELTA_MS=8 make perf-compare
```

Per-workload perf thresholds are defined in:

- `docs/reports/perf-thresholds.json`

Generate a natural-variation report (batch-to-batch median spread/CV):

```sh
make perf-variation
```

Variation tuning overrides:

```sh
PERF_VARIATION_BATCHES=10 PERF_VARIATION_RUNS_PER_BATCH=5 make perf-variation
```

Run strict race-stimulation regressions (fail on first mismatch, no tolerated failures):

```sh
make stress-race
```

Useful overrides:

```sh
RACE_REPEATS=200 RACE_UNSHARE_MODES=auto,off,fail make stress-race
RACE_FAIL_FAST=0 RACE_REPEATS=200 make stress-race
```

Note: fallback modes (`off`, `fail`) are useful for diagnostics and may expose current isolation bugs; any failure should be treated as actionable.

This runs focused checks for fragile semantics:

- `read` + mixed `IFS` edge behavior
- pipeline status/control-flow (`pipefail`, pipeline `exit`)
- redirection/exec error mapping (`126/127`, bad fd)

Run full local conformance gate:

```sh
make conformance-full
```

This runs, in order:

1. `make regressions`
2. BusyBox ash corpus (`src/tests/run_busybox_ash.sh run`)
3. Oil subset corpus (`src/tests/run_oil_subset.sh run ...`)

The full gate fails on baseline regressions.

Run a quick gate (fast smoke + parser coverage):

```sh
make conformance-quick
```

## Useful Overrides

You can override thresholds/timeouts per run:

```sh
RUN_TIMEOUT=1200 \
RUN_MODULE_TIMEOUT=1200 \
BUSYBOX_MIN_OK=357 BUSYBOX_MAX_FAIL=0 \
OIL_MIN_PASS=245 OIL_MAX_FAIL=0 \
make conformance-full
```

Known environment-specific BusyBox allowed-fail list can be adjusted:

```sh
BUSYBOX_ALLOWED_FAIL_FILES=ash-signals-sigquit_exec.tests.fail make conformance
```

BusyBox conformance now enforces allowlisted fail-file identity; if a different
`.fail` file appears, the gate fails even when fail-count thresholds still pass.

Known Oil fail pattern allowlist is also configurable:

```sh
OIL_ALLOWED_FAIL_PATTERNS='bash/dash/mksh run the last command is run in its own process' make conformance
```

Test harnesses set `MCTASH_TEST_MODE=1` to reduce nondeterminism in bridge diagnostics/import naming.

## Project Docs

- Plan: `docs/plan.md`
- ASDL adoption history: `docs/ASDL-adoption-history.md`
- Conformance matrix: `docs/conformance-matrix.md`
- Milestone-2 closure: `docs/milestone-2-closure-report.md`
- POSIX trace: `docs/posix-trace-table.md`
- POSIX shall-trace: `docs/posix-shall-trace.md`
