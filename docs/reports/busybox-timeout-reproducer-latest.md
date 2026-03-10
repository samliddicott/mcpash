# BusyBox Timeout Reproducer

Generated: 2026-03-10 10:13:29Z

## Reproducer Settings

- Runner: `./src/tests/run_busybox_ash.sh run <module>`
- `RUN_TIMEOUT=25`
- `RUN_MODULE_TIMEOUT=25`
- `BUSYBOX_FAIL_FAST_ON_TIMEOUT=1`

## Modules That Timed Out

- `ash-misc` -> ash-misc
- `ash-parsing` -> ash-parsing
- `ash-signals` -> ash-signals
- `ash-vars` -> ash-vars
- `ash-z_slow` -> ash-z_slow

## Modules With Non-zero Exit

- `ash-arith`: rc=1
- `ash-glob`: rc=1
- `ash-heredoc`: rc=1
- `ash-misc`: rc=124
- `ash-parsing`: rc=124
- `ash-psubst`: rc=1
- `ash-quoting`: rc=1
- `ash-read`: rc=1
- `ash-signals`: rc=124
- `ash-vars`: rc=124
- `ash-z_slow`: rc=124

## Notes

- This is a bounded reproducer for harness triage, not a full conformance run.
- Full detailed run log: `/tmp/busybox-timeout-repro.log` (local temporary file).
