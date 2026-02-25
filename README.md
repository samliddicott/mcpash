# mctash

`mctash` is a Python 3 shell project targeting ash-compatible behavior with an OSH-ASDL-guided parser/runtime path.

## Local Conformance Commands

Run targeted regression checks:

```sh
make regressions
```

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
- Conformance matrix: `docs/conformance-matrix.md`
- Milestone-2 closure: `docs/milestone-2-closure-report.md`
- POSIX trace: `docs/posix-trace-table.md`
- POSIX shall-trace: `docs/posix-shall-trace.md`
