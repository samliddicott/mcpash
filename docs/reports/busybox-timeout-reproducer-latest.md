# BusyBox Timeout Reproducer

Generated: 2026-03-10 10:46:48Z

## Reproducer Settings

- Runner: `./src/tests/run_busybox_ash.sh run <module>`
- `RUN_TIMEOUT=5`
- `RUN_MODULE_TIMEOUT=5`
- `BUSYBOX_FAIL_FAST_ON_TIMEOUT=1`

## Modules That Timed Out

- `ash-arith` -> ash-arith
- `ash-heredoc` -> ash-heredoc
- `ash-misc` -> ash-misc
- `ash-parsing` -> ash-parsing
- `ash-psubst` -> ash-psubst
- `ash-quoting` -> ash-quoting
- `ash-read` -> ash-read
- `ash-redir` -> ash-redir
- `ash-signals` -> ash-signals
- `ash-vars` -> ash-vars
- `ash-z_slow` -> ash-z_slow

## Modules With Non-zero Exit

- `ash-arith`: rc=124
- `ash-glob`: rc=1
- `ash-heredoc`: rc=124
- `ash-misc`: rc=124
- `ash-parsing`: rc=124
- `ash-psubst`: rc=124
- `ash-quoting`: rc=124
- `ash-read`: rc=124
- `ash-redir`: rc=124
- `ash-signals`: rc=124
- `ash-vars`: rc=124
- `ash-z_slow`: rc=124

## Notes

- This is a bounded reproducer for harness triage, not a full conformance run.
- Full detailed run log: `/tmp/busybox-timeout-repro.log` (local temporary file).
