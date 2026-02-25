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
make conformance
```

This runs, in order:

1. `make regressions`
2. BusyBox ash corpus (`src/tests/run_busybox_ash.sh run`)
3. Oil subset corpus (`src/tests/run_oil_subset.sh run ...`)

The gate fails on baseline regressions.

## Useful Overrides

You can override thresholds/timeouts per run:

```sh
RUN_TIMEOUT=1200 \
BUSYBOX_MIN_OK=357 BUSYBOX_MAX_FAIL=0 \
OIL_MIN_PASS=244 OIL_MAX_FAIL=1 \
make conformance
```

Known environment-specific BusyBox allowed-fail list can be adjusted:

```sh
BUSYBOX_ALLOWED_FAIL_FILES=ash-signals-sigquit_exec.tests.fail make conformance
```

Known Oil fail pattern allowlist is also configurable:

```sh
OIL_ALLOWED_FAIL_PATTERNS='bash/dash/mksh run the last command is run in its own process' make conformance
```

## Project Docs

- Plan: `docs/plan.md`
- Conformance matrix: `docs/conformance-matrix.md`
- POSIX trace: `docs/posix-trace-table.md`
- POSIX shall-trace: `docs/posix-shall-trace.md`
