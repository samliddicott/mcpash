# Differential Ash Parity Testing

We now have a harness that treats `/bin/ash` as the authoritative oracle and compares `mctash` side-by-side for every scripted scenario. The goal is to **capture every example from the `man ash` builtin list or POSIX shell grammar, run it in both shells, and fail if the outputs/status diverge**. That lets us generate the missing tests you asked for: each time we add a case, the harness runs `ash` first and uses its `stdout`/`stderr`/status as the baseline.

## What to cover
- Consult `man ash`, especially the **SHELL BUILTIN COMMANDS** section, plus the **COMMAND EXECUTION**/`set`/`test` descriptions. Each builtin (e.g. `set`, `test`, `getopts`, `read`, `ulimit`, `umask`, `jobs`, `fg`, `bg`, etc.) should have a directory under `tests/diff/cases` with scripts that exercise the key usages listed there (errors, quoting, option forms, redirections, env interactions).
- For POSIX-level requirements, refer to the **Command Language (Shell Syntax)** chapters in `pubs.opengroup.org` (POSIX.1-2017 / 2024) to enumerate the grammar/feature combinations we must replicate. That gives us a systematic list of “must-pass” scenarios for expansions, assignments, control structures, and builtins.
- Tag each new scenario with the relevant section (man page or POSIX paragraph) so the gap reports can tie back to the specification.

## How to add a case
1. Drop a script under `tests/diff/cases` (e.g. `set-listing.sh`). Use a real `ash` shebang or run via `ash`/`mctash` directly.
2. Prefer deterministic output: avoid random data. When environment values are required (like `PATH`), keep them stable with `export` at the top of the script so both shells see the same inputs.
3. Run the harness:

```
./tests/diff/run.sh --case set-listing
```

The script runs `ash` first, then `mctash`, saves their outputs under `tests/diff/logs`, and diff(1) compares them. Any mismatch fails fast. Use `--generate` to overwrite the `logs/expected` snapshot if you need to record ash’s current output for manual inspection.

## Harness internals
- `tests/diff/run.sh` (executable) drives every `*.sh` file under `tests/diff/cases` by invoking both shells; it captures `stdout/stderr`/exit codes, writes logs under `tests/diff/logs/{ash,mctash,diff}`, and optionally records the ash output via `--generate`.
- You can filter the run with `--case NAME` or swap in alternate shells via the `ASH_BIN`/`MCTASH_CMD` environment variables.
- Add a descriptive log entry when a divergence is detected so we can trace it back to the spec sentence you are exercising.

## Next steps
1. Add cases for each builtin and option sequence described in `man ash` (use subsection identifiers as labels).
2. Expand to POSIX grammar points (compound commands, parameter expansion, quoting, redirections).
3. Iterate: fix `mctash` until `tests/diff/run.sh --case ...` passes, then commit the new case plus relevant runtime change.
