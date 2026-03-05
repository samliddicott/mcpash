# Bash Feature Categories from `man bash`

Source read: local `man bash` (rendered via `col -b` on 2026-03-04).

Authoritative exhaustive inventory: `docs/specs/bash-man-requirements.tsv` with summary in `docs/specs/bash-man-requirements.md`.

Purpose: categorize Bash features into matrix-ready implementation buckets, with `--posix` presence notes.

## Legend

- `present`: feature surface exists in `bash --posix`.
- `changed`: feature exists but behavior/defaults differ in `--posix`.
- `extension`: Bash-specific (non-POSIX) feature; may still be available in `--posix`.
- `n/a`: interactive-only or environment-dependent in non-interactive matrix lanes.

## 1) Invocation, Startup, and Mode Selection

Features:

- Invocation options (`-c`, `-i`, `-l`, `-r`, `-s`, `-v`, `-x`, `-D`, `-O/+O`, long options).
- Startup file loading (`/etc/profile`, `~/.bash_profile`, `~/.bashrc`, `ENV`, `BASH_ENV`).
- Invocation identity modes (`bash`, `sh`, restricted shell).
- POSIX mode entry points (`--posix`, `set -o posix`, `POSIXLY_CORRECT`, invoked-as-`sh`).

`--posix` status:

- `present` for invocation/startup machinery.
- `changed` startup behavior and standards-conformance behavior.

## 2) Lexing and Grammar Surface

Features:

- Reserved words and control operators.
- Simple commands, pipelines, lists, compound commands.
- Functions, arithmetic command forms, conditionals, subshell/grouping.

`--posix` status:

- Core grammar: `present`.
- Bash grammar extensions (`[[ ... ]]`, `(( ... ))`, `coproc`, `function` keyword): `extension` (generally still parsable; not POSIX-required).
- `time` reserved-word handling: `changed` in POSIX mode (documented in man page).

## 3) Word/Parameter/Command Expansion

Features:

- Parameter expansion forms.
- Command substitution, arithmetic expansion.
- Field splitting, pathname expansion, quote removal.
- Brace expansion and process substitution.

`--posix` status:

- Core POSIX expansion phases: `present`.
- Several expansion corner semantics: `changed` in POSIX mode.
- Brace expansion/process substitution: `extension` (Bash-specific; not required by POSIX).

## 4) Redirection and FD Semantics

Features:

- Standard redirections (`<`, `>`, `>>`, `<>`, here-doc/here-string variants, fd duplication/closure).
- Ordering of redirections and pipeline integration.

`--posix` status:

- Core redirection surface: `present`.
- Some diagnostics/edge behavior may be `changed`.
- Bash-only forms remain `extension`.

## 5) Execution, Environment, Errors, Signals, Jobs

Features:

- Command lookup/execution and subshell environment.
- Exit status rules, signal/trap handling.
- Job control (`jobs`, `fg`, `bg`, monitor mode).

`--posix` status:

- Execution/error model: `present` with `changed` details.
- Job control: `present` but mostly `n/a` in non-interactive scripts; behavior differs by tty/monitor mode.

## 6) Interactive UX Subsystems

Features:

- Prompt expansion (`PS0`-`PS4`, `PROMPT_COMMAND`).
- Readline keymaps/options.
- History storage/edit/re-expansion (`history`, `fc`, `!` expansion).
- Programmable completion (`complete`, `compgen`, `compopt`).

`--posix` status:

- Surface mostly `present`.
- Many parts are `extension` and/or `n/a` in non-interactive lanes.

## 7) Builtins (Complete Inventory, Grouped)

All 61 builtins reported by `compgen -b` are available as command surface in both default and `--posix` launch.

### 7.1 POSIX/core command builtins

- `.`, `:`, `[`, `break`, `cd`, `continue`, `eval`, `exec`, `exit`, `export`, `getopts`, `hash`, `pwd`, `readonly`, `return`, `set`, `shift`, `test`, `times`, `trap`, `umask`, `unalias`, `unset`, `wait`.

Status in `--posix`: `present` (some semantics `changed` to POSIX rules).

### 7.2 Shell environment/control builtins

- `alias`, `bg`, `builtin`, `command`, `false`, `fg`, `jobs`, `kill`, `printf`, `read`, `true`, `type`, `ulimit`.

Status in `--posix`: `present`.

### 7.3 Bash extension builtins

- `bind`, `caller`, `compgen`, `complete`, `compopt`, `declare`, `dirs`, `disown`, `enable`, `help`, `history`, `let`, `local`, `logout`, `mapfile`, `popd`, `pushd`, `readarray`, `shopt`, `source`, `suspend`, `typeset`, `fc`, `echo`.

Status in `--posix`: mostly `present` as Bash extensions; not POSIX-required.

## 8) `set -o` Option Surface

Option names (27 total):

- `allexport`, `braceexpand`, `emacs`, `errexit`, `errtrace`, `functrace`, `hashall`, `histexpand`, `history`, `ignoreeof`, `interactive-comments`, `keyword`, `monitor`, `noclobber`, `noexec`, `noglob`, `nolog`, `notify`, `nounset`, `onecmd`, `physical`, `pipefail`, `posix`, `privileged`, `verbose`, `vi`, `xtrace`.

`--posix` default deltas observed:

- `posix`: `off -> on`.
- other `set -o` defaults unchanged at shell start.

## 9) `shopt` Option Surface

Option names (53 total):

- `autocd`, `assoc_expand_once`, `cdable_vars`, `cdspell`, `checkhash`, `checkjobs`, `checkwinsize`, `cmdhist`, `compat31`, `compat32`, `compat40`, `compat41`, `compat42`, `compat43`, `compat44`, `complete_fullquote`, `direxpand`, `dirspell`, `dotglob`, `execfail`, `expand_aliases`, `extdebug`, `extglob`, `extquote`, `failglob`, `force_fignore`, `globasciiranges`, `globstar`, `gnu_errfmt`, `histappend`, `histreedit`, `histverify`, `hostcomplete`, `huponexit`, `inherit_errexit`, `interactive_comments`, `lastpipe`, `lithist`, `localvar_inherit`, `localvar_unset`, `login_shell`, `mailwarn`, `no_empty_cmd_completion`, `nocaseglob`, `nocasematch`, `nullglob`, `progcomp`, `progcomp_alias`, `promptvars`, `restricted_shell`, `shift_verbose`, `sourcepath`, `xpg_echo`.

`--posix` default deltas observed:

- `expand_aliases`: `off -> on`
- `inherit_errexit`: `off -> on`
- `shift_verbose`: `off -> on`

(Other values unchanged at startup.)

## 10) Variable Surface (Category Buckets)

### 10.1 POSIX/core shell variables

- `HOME`, `PATH`, `IFS`, `PWD`, `OLDPWD`, `OPTIND`, `OPTARG`, `PS1`, `PS2`, `MAIL`, `MAILPATH`, `LANG`, `LC_*`, `ENV`, `LINENO`, etc.

`--posix`: `present`, with some `changed` behavior.

### 10.2 Bash internals / introspection

- `BASH`, `BASH_VERSION`, `BASH_VERSINFO`, `BASH_SOURCE`, `BASH_LINENO`, `BASH_COMMAND`, `BASH_SUBSHELL`, `BASHOPTS`, `SHELLOPTS`, `BASH_COMPAT`, etc.

`--posix`: `present` as `extension` variables.

### 10.3 History/readline/completion variables

- `HIST*`, `FCEDIT`, `READLINE_*`, `COMP_*`, `COMPREPLY`, `HOSTFILE`, `INPUTRC`.

`--posix`: `present`, mostly interactive (`n/a` in non-interactive scripts).

### 10.4 Job/process/runtime variables

- `BASHPID`, `PPID`, `PIPESTATUS`, `SECONDS`, `RANDOM`, `SRANDOM`, `EPOCH*`, `UID`, `EUID`, `GROUPS`, `COPROC`.

`--posix`: `present` (many are Bash-specific extensions).

## 11) Compatibility and Restriction Frameworks

Features:

- Compatibility levels via `BASH_COMPAT` / `compatNN` (`shopt`).
- Restricted shell (`rbash` / `set -r`).

`--posix` status:

- Compatibility framework: `present` (Bash extension).
- Restricted shell: `present` and orthogonal to POSIX mode.

## 12) Matrix-Ready Implementation Buckets

Use these buckets directly for parity matrices:

1. Invocation/startup and mode toggles.
2. Grammar/parser productions.
3. Expansion engine (word/param/command/arithmetic).
4. Redirection and FD behavior.
5. Builtins (core POSIX first, then Bash-extension lanes).
6. Variables and shell state reporting.
7. Interactive subsystems (prompt/readline/history/completion).
8. Jobs/traps/signals (non-interactive and PTY-interactive lanes).
9. Compatibility and restricted-mode behavior.

Each matrix row should include comparator mode columns:

- `bash` default
- `bash --posix`
- `mctash` default (bash-compat mode)
- `mctash --posix`

and a standards column:

- `POSIX required` / `POSIX optional` / `Bash extension`.

## Notes on `--posix` Presence Interpretation

From `man bash`, POSIX mode primarily changes behavior where default Bash differs from POSIX; it does not remove most Bash command surface. For matrix design, treat many non-POSIX features as:

- still callable in `--posix`, but
- classified as `Bash extension` rather than POSIX conformance requirements.
