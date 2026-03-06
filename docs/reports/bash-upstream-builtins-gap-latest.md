# Bash Upstream Builtins Gap Report

Date: 2026-03-06

Source corpus:

- `tests/bash/upstream/baserock-bash-5.1-testing/tests/builtins.tests`

Comparator mode used for this report:

- `bash --posix` with `BASH_COMPAT=50`
- `mctash --posix` with `BASH_COMPAT=50`

Current result:

- bash rc: `2`
- mctash rc: `2`
- stdout diff lines: `160`
- stderr diff lines: `13`

Artifacts:

- `tests/bash/upstream/baserock-bash-5.1-testing/run-lanes/diff/builtins.tests.out.diff`
- `tests/bash/upstream/baserock-bash-5.1-testing/run-lanes/diff/builtins.tests.err.diff`

Implemented in this tranche:

- arithmetic-command parsing now disambiguates `((...))` vs nested grouping better and handles empty `(( ))` form without syntax abort.
- alias expansion now preserves syntax-sensitive aliases earlier in parse and supports variable expansion for runtime alias words.
- `umask` gained symbolic assignment support for `who=perms` forms used by upstream builtins coverage.
- `export`/`export -n` now tracks explicit export attribute state (used by `declare -p` rendering).
- source/dot diagnostics in bash-style mode now emit `. : name: file not found` form for bare-name lookup failures.
- non-posix special-builtin assignment-prefix behavior now restores prefix names unless builtin semantics require persistence.
- `-c` with no explicit argv0 now gets a stable default script name (`bash` in bash-compat lane) for parity-sensitive `$0` tests.

Remaining high-impact mismatch buckets:

1. assignment-prefix behavior around `eval`/special-builtin environment persistence.
2. `exec -a/-l` argv0 reporting mismatches in upstream lane.
3. positional-parameter behavior in sourced-script path tests (`source4.sub` lane).
4. array/assoc + `typeset`/`unset` behavior in `builtins5.sub` and `builtins6.sub`.
5. function-definition rendering and a few residual output ordering/formatting deltas.

Next closure order:

1. `declare` / `typeset` parity tranche.
2. source/path edge tranche.
3. diagnostic text normalization tranche.
4. function/printing formatting tranche.
