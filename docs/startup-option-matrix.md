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
| `-u` | nounset | Implemented | Startup behavior active; unset parameter error exits with status 2. |
| `-v` | verbose | Implemented (basic parity) | Startup behavior echoes input lines to stderr before execution. |
| `-x` | xtrace | Implemented (basic parity) | Startup behavior traces simple commands; `PS4` prefix is honored. |
| `-I` | ignoreeof | Partial | Interactive REPL path honors ignore-EOF loop on TTY; full dash UX parity not claimed. |
| `-i` | interactive | Implemented (partial parity) | Forces interactive REPL mode; full editor/history/job-control parity still pending. |
| `-m` | monitor | Partial | Auto-set for interactive shells; full job-control semantics are pending. |
| `-q` | nolog | Parsed | Included in `set -o/+o` listing compatibility. |
| `-V` | vi | Partial | Readline vi editing mode is requested when available; full dash editor parity not claimed. |
| `-E` | emacs | Partial | Readline emacs editing mode is requested when available; full dash editor parity not claimed. |
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
| `verbose` | Implemented (basic parity) | Maps to `-v`; echoes shell input to stderr. |
| `xtrace` | Implemented (basic parity) | Maps to `-x`; simple command tracing with `PS4` prefix support. |
| `noclobber` | Implemented | Maps to `-C`. |
| `vi` | Partial | Maps to `-V`; readline-backed mode request when available. |
| `emacs` | Partial | Maps to `-E`; readline-backed mode request when available. |
| `interactive` | Implemented (partial parity) | Maps to `-i`; forces REPL path. |
| `monitor` | Partial | Maps to `-m`; full job-control semantics pending. |
| `notify` | Parsed (out-of-scope runtime effect) | Maps to `-b`. |
| `ignoreeof` | Partial | Maps to `-I`; implemented for TTY REPL path. |
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
  - startup `-v` input echoing
  - startup `-x` with `PS4` prefix
