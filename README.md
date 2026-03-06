# mctash

`mctash` is a Python 3 shell project targeting ash-compatible behavior with an OSH-ASDL-guided parser/runtime path.

## Standard Development Cycle

For any new `man bash` section work, follow this cycle:

1. Decompose section text into atomic requirement rows.
2. Add matching implementation-matrix rows with explicit test IDs.
3. Write an implementation design model mapping rows to runtime ownership/state.
4. Implement by subsystem slices, then re-run matrix gates and close rows.

Project skill for this cycle:

- `docs/skills/bash-man-section-decomposition/SKILL.md`

Current example design artifact:

- `docs/design/job-control-runtime-model.md`

## Startup Mode Selection

Mode precedence is:

1. explicit startup flags (`--posix`, `--bash`)
2. invocation name (`sh`/`ash`/`dash` => POSIX mode, `mctash`/`ptash`/`bash` => bash mode)
3. `MCTASH_MODE=posix|bash`
4. default: bash mode

In bash mode, `BASH_COMPAT` is auto-initialized to `50` if unset.

For `python -m mctash` testing, `MCTASH_ARG0` can simulate invocation names.

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

Run dual-lane parity matrix and produce bash-gap report:

```sh
make diff-parity-matrix
```

Report output:
- `docs/reports/bash-gap-latest.md`

For bash-baseline differential cases, you can mirror compat settings across both shells:

```sh
PARITY_BASH_COMPAT=50 PARITY_MIRROR_POSIX=1 make diff-conformance
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

Run strict bridge stress checks:

```sh
make stress-bridge
```

Run POSIX/`BASH_COMPAT` compatibility matrix (Bash reference + mctash progress):

```sh
make compat-posix-bash
```

Strict mode (Bash parity checks enabled for the gated compatibility slice):

```sh
make compat-posix-bash-strict
```

Choose compatibility level under test:

```sh
PARITY_COMPAT=50 make compat-posix-bash-strict
```

Run bash-man-page-driven POSIX parity matrix (`bash --posix` baseline):

```sh
make bash-posix-man-matrix
```

Report output:
- `docs/reports/bash-posix-man-matrix-latest.md`

Run builtin-focused parity matrix lanes (core + bash-compat):

```sh
make bash-builtin-matrix
```

Strict mode also runs PTY interactive completion/readline checks:

```sh
STRICT=1 make bash-builtin-matrix
```

Report output:
- `docs/reports/bash-builtin-matrix-latest.md`

Run interactive completion/readline matrix directly:

```sh
make completion-interactive-matrix
```

Run upstream bash POSIX-core matrix lanes (core strict + info lane):

```sh
make bash-posix-upstream-matrix
```

Report output:
- `docs/reports/bash-posix-upstream-gap-latest.md`

Run the cross-baseline semantic matrix (ash POSIX, bash POSIX, bash full, mctash POSIX, mctash bash):

```sh
make semantic-matrix
```

Report output:
- `docs/reports/semantic-matrix-latest.md`

This is the canonical behavior matrix for new parity work; older lane-specific matrices remain useful as feeder corpora/harnesses.

By default, heavy upstream-corpus rows (`@upstream:*`) are skipped to keep iteration fast.
Enable them explicitly:

```sh
RUN_UPSTREAM_ROWS=1 make semantic-matrix
```

To run a single row while debugging:

```sh
ROW_FILTER='upstream-set-e' RUN_UPSTREAM_ROWS=1 make semantic-matrix
```

Fetch upstream GNU bash tests metadata (Savannah) for corpus planning:

```sh
make bash-tests-fetch
```

Pin or refresh fetch cache:

```sh
BASH_UPSTREAM_REF=master make bash-tests-fetch
FORCE_REFRESH=1 make bash-tests-fetch
```

Fetched metadata location:
- `tests/bash/upstream/`

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
- Bridge examples (ash mode): `docs/bridge-examples-ash-mode.md`
- POSIX trace: `docs/posix-trace-table.md`
- POSIX shall-trace: `docs/posix-shall-trace.md`
