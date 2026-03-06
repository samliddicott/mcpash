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
- stdout diff lines: `11`
- stderr diff lines: `0`

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
- sourced positional-parameter semantics now preserve caller `$@` only when source args remain unchanged, matching bash behavior in `source3/source4` lanes.
- `unset` now matches bash fallback semantics (`unset name` can remove functions when no variable exists) while respecting explicit `-v`.
- `test -v` now handles array/assoc/scalar subscripted forms used by upstream coverage.
- typed assignment behavior now respects declared array/assoc attributes during plain assignment commands.
- in-process pipeline capture now redirects fd0 for builtin/function stages, fixing `. /dev/stdin` pipeline sourcing behavior.
- `echo` now honors `shopt xpg_echo` escape decoding for upstream builtins coverage.

Remaining high-impact mismatch buckets:

1. assoc-array `declare -p` key ordering mismatch in `builtins4.sub` (`[one][two][three]` vs bash output order in this corpus run).

Rationale for treating assoc key order as non-contractual:

- Chet Ramey (bash maintainer): “There’s no guarantee that will happen. It’s a hash table.”
  - https://lists.nongnu.org/archive/html/bug-bash/2019-08/msg00032.html
- Reporter example showing declaration order differs from printed/iterated order:
  - https://lists.nongnu.org/archive/html/bug-bash/2019-08/msg00030.html
- Greg Wooledge guidance: if ordering is needed, use a separate indexed array:
  - https://lists.nongnu.org/archive/html/bug-bash/2019-08/msg00031.html

Test policy applied:

- Upstream lane now normalizes `declare -A ...` pair ordering in stdout diffs
  before comparison (semantic comparison for associative maps).

Next closure order:

1. `declare` / `typeset` parity tranche.
2. source/path edge tranche.
3. diagnostic text normalization tranche.
4. function/printing formatting tranche.
