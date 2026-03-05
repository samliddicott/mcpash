# Bash Upstream Builtins Gap Report

Date: 2026-03-05

Source corpus:

- `tests/bash/upstream/baserock-bash-5.1-testing/tests/builtins.tests`

Comparator mode used for this report:

- `bash --posix` with `BASH_COMPAT=50`
- `mctash --posix` with `BASH_COMPAT=50`

Current result:

- bash rc: `2`
- mctash rc: `2`
- stdout diff lines: `251`
- stderr diff lines: `27`

Artifacts:

- `tests/bash/upstream/baserock-bash-5.1-testing/run-lanes/diff/builtins.bcompat.out.diff`
- `tests/bash/upstream/baserock-bash-5.1-testing/run-lanes/diff/builtins.bcompat.err.diff`

Implemented in this tranche:

- `exit status` non-numeric now exits with status `2` (no traceback crash).
- `type` gained bash-compatible `-t` and `-a` behavior in bash-compat mode while preserving ash-lane behavior.
- `exec` gained `-a`, `-l`, `-c` option handling.
- `declare -f` accepted and prints function definitions.
- POSIX special-builtin set corrected for `enable -s` (`exec`/`times` included; non-special entries removed).

Remaining high-impact mismatch buckets:

1. `declare` and assignment edge behavior in `declare -p` and assignment-prefix forms.
2. array/assoc + `typeset` behavior in `builtins4.sub` / `builtins5.sub`.
3. source/path edge flows (`source5.sub`/`source7.sub`) and parser behavior in those scripts.
4. diagnostics parity for several builtin error paths.
5. residual output formatting differences (`declare` rendering, function dump formatting, and selected builtin listings).

Next closure order:

1. `declare` / `typeset` parity tranche.
2. source/path edge tranche.
3. diagnostic text normalization tranche.
4. function/printing formatting tranche.
