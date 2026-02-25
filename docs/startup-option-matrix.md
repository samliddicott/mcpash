# Startup Option Matrix (Ash Parity Scope)

Date: 2026-02-25

Reference baseline:

- `man ash` option surface
- POSIX shell option semantics where applicable

Scope note:

- This matrix is for non-interactive `mctash` startup behavior and `set -o/+o` parity.
- Interactive/editor/job-control runtime UX parity remains outside current milestone scope.

## Single-letter startup flags

| Flag | Name | Status in mctash | Notes |
|---|---|---|---|
| `-a` | allexport | Implemented | Parsed at startup; reflected in `$-` / `set -o`. |
| `-C` | noclobber | Implemented | Startup behavior enforced for `>` on existing regular files. |
| `-e` | errexit | Implemented | Startup behavior active. |
| `-f` | noglob | Implemented | Startup behavior active (pathname expansion disabled). |
| `-n` | noexec | Implemented | Startup behavior active (parse-only). |
| `-u` | nounset | Implemented (with known status-code divergence) | Startup behavior active; unset parameter error exits non-zero (currently status 1 in mctash). |
| `-v` | verbose | Partial | Parsed and exposed in options; full ash-verbose output parity not claimed. |
| `-x` | xtrace | Partial | Parsed and used; formatting parity is implementation-specific. |
| `-I` | ignoreeof | Parsed (out-of-scope runtime effect) | Interactive behavior not in current scope. |
| `-i` | interactive | Parsed (out-of-scope runtime effect) | Interactive mode parity not in current scope. |
| `-m` | monitor | Parsed (out-of-scope runtime effect) | Full job control parity not in current scope. |
| `-q` | nolog | Parsed | Included in `set -o/+o` listing compatibility. |
| `-V` | vi | Parsed (out-of-scope runtime effect) | Interactive editor mode parity not in current scope. |
| `-E` | emacs | Parsed (out-of-scope runtime effect) | Interactive editor mode parity not in current scope. |
| `-b` | notify | Parsed (out-of-scope runtime effect) | Job notification parity not in current scope. |
| `-p` | privileged | Parsed | Listed and tracked; full privilege-mode semantics not claimed. |
| `-s` | stdin | Parsed | Command intake mode control supported in startup parser path. |

## `-o/+o` option names

| Option name | Status in mctash | Notes |
|---|---|---|
| `allexport` | Implemented | Maps to `-a`. |
| `errexit` | Implemented | Maps to `-e`. |
| `noglob` | Implemented | Maps to `-f`. |
| `noexec` | Implemented | Maps to `-n`. |
| `nounset` | Implemented | Maps to `-u`. |
| `verbose` | Partial | Maps to `-v`. |
| `xtrace` | Partial | Maps to `-x`. |
| `noclobber` | Implemented | Maps to `-C`. |
| `vi` | Parsed (out-of-scope runtime effect) | Maps to `-V`. |
| `emacs` | Parsed (out-of-scope runtime effect) | Maps to `-E`. |
| `interactive` | Parsed (out-of-scope runtime effect) | Maps to `-i`. |
| `monitor` | Parsed (out-of-scope runtime effect) | Maps to `-m`. |
| `notify` | Parsed (out-of-scope runtime effect) | Maps to `-b`. |
| `ignoreeof` | Parsed (out-of-scope runtime effect) | Maps to `-I`. |
| `stdin` | Parsed | Maps to `-s`. |
| `privileged` | Parsed | Maps to `-p`. |
| `nolog` | Parsed | Maps to `-q`; included for ash listing compatibility. |
| `debug` | Parsed | Listed for ash compatibility surface. |
| `pipefail` | Implemented (extension) | Not in classic POSIX ash, retained as mctash extension. |

## Listing parity

- `set -o` and `set +o` are implemented with ash-style listing behavior in current scope.
- Listing includes `nolog`/`debug` names for ash compatibility, and `pipefail` as mctash extension.

## Current regression coverage

- `tests/regressions/run.sh` includes startup option checks for:
  - short options (`-eu`)
  - long option (`-o nounset`)
  - illegal startup option rejection
  - `set -o` / `set +o` listing
  - `nolog` / `debug` toggling and reporting
  - startup semantics for `-u`, `-f`, and `-C`
