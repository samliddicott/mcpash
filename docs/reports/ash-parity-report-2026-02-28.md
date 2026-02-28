# Ash Parity Report (2026-02-28)

## Scope

This report records the current parity status of `mctash` against the BusyBox ash test corpus and the local differential man-page cases.

## Commands Run

### Differential cases

```bash
tests/diff/run.sh
```

Result:

- pass (no mismatches reported)

### BusyBox ash corpus (full)

```bash
RUN_MODULE_TIMEOUT=180 src/tests/run_busybox_ash.sh run
```

Result summary:

- `ok=357`
- `fail=0`
- `skip=0`

## Significant Fixes Included In This Pass

- `fc` differential coverage switched to `bash --posix` baseline where ash lacks `fc`.
- Script-mode history capture improved so `fc` behavior has usable history outside pure REPL paths.
- Globbing/escaping fixes for BusyBox `ash-glob` parity (including escaped slash display behavior).
- Here-doc and `type` wording alignment (`is a function` compatibility surface).
- `read` improvements:
  - default no-name target `REPLY`
  - support for `-n`, `-d`, `-t`
  - timeout-zero readiness behavior used by corpus
- Readonly `unset` non-interactive failure behavior aligned for BusyBox `readonly0` expectations.

## Current Conclusion

For the currently integrated test corpora in this repository:

- `mctash` passes all checked differential man-page cases.
- `mctash` passes the full BusyBox ash test run used by the local harness.

This is a strong ash-parity milestone for the implemented scope.
