# Feature Index

Generated: 2026-03-09 16:22:34Z

Purpose: group requirement rows by feature/topic so design, implementation, and tests can be handled as coherent feature stories instead of row-by-row patches.

Source matrices:

- `bash-compat-doc`: `https://tiswww.case.edu/php/chet/bash/COMPAT`
- `bash-man`: `man bash`
- `bash-posix-doc`: `https://tiswww.case.edu/php/chet/bash/POSIX`
- `docs/specs/bash-man-implementation-matrix.tsv`
- `docs/specs/bash-posix-mode-implementation-matrix.tsv`
- `docs/specs/bash-compat-deltas-implementation-matrix.tsv`

## Topic Summary

| Topic | Rows | Covered | Partial | Other |
|---|---:|---:|---:|---:|
| `builtin:.` | 1 | 1 | 0 | 0 |
| `builtin::` | 1 | 1 | 0 | 0 |
| `builtin:[` | 1 | 1 | 0 | 0 |
| `builtin:alias` | 5 | 5 | 0 | 0 |
| `builtin:bg` | 3 | 3 | 0 | 0 |
| `builtin:bind` | 3 | 2 | 1 | 0 |
| `builtin:break` | 3 | 1 | 2 | 0 |
| `builtin:builtin` | 1 | 1 | 0 | 0 |
| `builtin:caller` | 1 | 1 | 0 | 0 |
| `builtin:cd` | 3 | 3 | 0 | 0 |
| `builtin:command` | 34 | 25 | 9 | 0 |
| `builtin:compgen` | 2 | 2 | 0 | 0 |
| `builtin:complete` | 1 | 1 | 0 | 0 |
| `builtin:compopt` | 1 | 1 | 0 | 0 |
| `builtin:continue` | 2 | 1 | 1 | 0 |
| `builtin:declare` | 2 | 2 | 0 | 0 |
| `builtin:dirs` | 1 | 1 | 0 | 0 |
| `builtin:disown` | 1 | 1 | 0 | 0 |
| `builtin:echo` | 3 | 3 | 0 | 0 |
| `builtin:enable` | 1 | 1 | 0 | 0 |
| `builtin:eval` | 1 | 1 | 0 | 0 |
| `builtin:exec` | 2 | 2 | 0 | 0 |
| `builtin:exit` | 6 | 6 | 0 | 0 |
| `builtin:export` | 5 | 5 | 0 | 0 |
| `builtin:false` | 1 | 1 | 0 | 0 |
| `builtin:fc` | 11 | 11 | 0 | 0 |
| `builtin:fg` | 3 | 3 | 0 | 0 |
| `builtin:getopts` | 1 | 1 | 0 | 0 |
| `builtin:hash` | 1 | 1 | 0 | 0 |
| `builtin:help` | 2 | 2 | 0 | 0 |
| `builtin:history` | 7 | 7 | 0 | 0 |
| `builtin:jobs` | 5 | 4 | 1 | 0 |
| `builtin:kill` | 4 | 4 | 0 | 0 |
| `builtin:let` | 1 | 1 | 0 | 0 |
| `builtin:local` | 1 | 1 | 0 | 0 |
| `builtin:logout` | 1 | 1 | 0 | 0 |
| `builtin:mapfile` | 1 | 1 | 0 | 0 |
| `builtin:popd` | 1 | 1 | 0 | 0 |
| `builtin:printf` | 2 | 2 | 0 | 0 |
| `builtin:pushd` | 1 | 1 | 0 | 0 |
| `builtin:pwd` | 2 | 2 | 0 | 0 |
| `builtin:read` | 5 | 5 | 0 | 0 |
| `builtin:readarray` | 1 | 1 | 0 | 0 |
| `builtin:readonly` | 2 | 2 | 0 | 0 |
| `builtin:return` | 4 | 2 | 2 | 0 |
| `builtin:set` | 12 | 10 | 2 | 0 |
| `builtin:shift` | 2 | 2 | 0 | 0 |
| `builtin:shopt` | 3 | 3 | 0 | 0 |
| `builtin:source` | 3 | 3 | 0 | 0 |
| `builtin:suspend` | 2 | 2 | 0 | 0 |
| `builtin:test` | 4 | 3 | 1 | 0 |
| `builtin:times` | 1 | 1 | 0 | 0 |
| `builtin:trap` | 4 | 4 | 0 | 0 |
| `builtin:true` | 1 | 1 | 0 | 0 |
| `builtin:type` | 4 | 4 | 0 | 0 |
| `builtin:typeset` | 1 | 1 | 0 | 0 |
| `builtin:ulimit` | 2 | 2 | 0 | 0 |
| `builtin:umask` | 1 | 1 | 0 | 0 |
| `builtin:unalias` | 1 | 1 | 0 | 0 |
| `builtin:unset` | 4 | 3 | 1 | 0 |
| `builtin:wait` | 7 | 7 | 0 | 0 |
| `runtime:history` | 6 | 6 | 0 | 0 |
| `runtime:job-control` | 9 | 9 | 0 | 0 |
| `runtime:prompt` | 3 | 3 | 0 | 0 |
| `runtime:signals-traps` | 4 | 4 | 0 | 0 |
| `runtime:startup` | 7 | 7 | 0 | 0 |
| `subcategory:compat-delta` | 3 | 0 | 3 | 0 |
| `subcategory:compatibility` | 4 | 4 | 0 | 0 |
| `subcategory:expansion` | 8 | 8 | 0 | 0 |
| `subcategory:expansion-redir` | 3 | 3 | 0 | 0 |
| `subcategory:grammar.core` | 19 | 19 | 0 | 0 |
| `subcategory:interactive` | 4 | 4 | 0 | 0 |
| `subcategory:invocation.long-option` | 13 | 13 | 0 | 0 |
| `subcategory:invocation.set-o-option` | 25 | 25 | 0 | 0 |
| `subcategory:invocation.set-short-option` | 19 | 19 | 0 | 0 |
| `subcategory:invocation.short-option` | 12 | 12 | 0 | 0 |
| `subcategory:invocation.startup-files` | 2 | 2 | 0 | 0 |
| `subcategory:misc-posix-mode` | 1 | 1 | 0 | 0 |
| `subcategory:mode-framework` | 3 | 3 | 0 | 0 |
| `subcategory:parse-grammar` | 2 | 2 | 0 | 0 |
| `subcategory:redirection` | 9 | 9 | 0 | 0 |
| `subcategory:requirements-matrix` | 7 | 7 | 0 | 0 |
| `subcategory:shopt-option-surface` | 45 | 45 | 0 | 0 |
| `subcategory:state-model` | 2 | 2 | 0 | 0 |
| `subcategory:variables.special-parameters` | 9 | 9 | 0 | 0 |
| `syntax:arithmetic` | 3 | 1 | 2 | 0 |
| `syntax:command-substitution` | 2 | 1 | 1 | 0 |
| `syntax:parameter-expansion` | 20 | 18 | 2 | 0 |
| `syntax:quoting` | 7 | 6 | 1 | 0 |
| `syntax:redirection` | 14 | 14 | 0 | 0 |
| `var:BASH` | 1 | 1 | 0 | 0 |
| `var:BASHOPTS` | 1 | 1 | 0 | 0 |
| `var:BASHPID` | 1 | 1 | 0 | 0 |
| `var:BASH_ARGC` | 1 | 1 | 0 | 0 |
| `var:BASH_ARGV` | 1 | 1 | 0 | 0 |
| `var:BASH_ARGV0` | 1 | 1 | 0 | 0 |
| `var:BASH_CMDS` | 1 | 1 | 0 | 0 |
| `var:BASH_COMMAND` | 1 | 1 | 0 | 0 |
| `var:BASH_COMPAT` | 1 | 1 | 0 | 0 |
| `var:BASH_ENV` | 1 | 1 | 0 | 0 |
| `var:BASH_LINENO` | 1 | 1 | 0 | 0 |
| `var:BASH_LOADABLES_PATH` | 1 | 1 | 0 | 0 |
| `var:BASH_REMATCH` | 1 | 1 | 0 | 0 |
| `var:BASH_SOURCE` | 1 | 1 | 0 | 0 |
| `var:BASH_SUBSHELL` | 1 | 1 | 0 | 0 |
| `var:BASH_VERSINFO` | 1 | 1 | 0 | 0 |
| `var:BASH_VERSION` | 1 | 1 | 0 | 0 |
| `var:BASH_XTRACEFD` | 1 | 1 | 0 | 0 |
| `var:COMPREPLY` | 1 | 1 | 0 | 0 |
| `var:COMP_CWORD` | 1 | 1 | 0 | 0 |
| `var:COMP_KEY` | 1 | 1 | 0 | 0 |
| `var:COMP_LINE` | 1 | 1 | 0 | 0 |
| `var:COMP_POINT` | 1 | 1 | 0 | 0 |
| `var:COMP_TYPE` | 1 | 1 | 0 | 0 |
| `var:COMP_WORDBREAKS` | 1 | 1 | 0 | 0 |
| `var:COMP_WORDS` | 1 | 1 | 0 | 0 |
| `var:COPROC` | 1 | 1 | 0 | 0 |
| `var:DIRSTACK` | 1 | 1 | 0 | 0 |
| `var:ENV` | 1 | 1 | 0 | 0 |
| `var:EPOCHREALTIME` | 1 | 1 | 0 | 0 |
| `var:EPOCHSECONDS` | 1 | 1 | 0 | 0 |
| `var:EUID` | 1 | 1 | 0 | 0 |
| `var:FCEDIT` | 1 | 1 | 0 | 0 |
| `var:FUNCNAME` | 1 | 1 | 0 | 0 |
| `var:GROUPS` | 1 | 1 | 0 | 0 |
| `var:HISTCONTROL` | 1 | 1 | 0 | 0 |
| `var:HISTFILE` | 1 | 1 | 0 | 0 |
| `var:HISTFILESIZE` | 1 | 1 | 0 | 0 |
| `var:HISTIGNORE` | 1 | 1 | 0 | 0 |
| `var:HISTSIZE` | 1 | 1 | 0 | 0 |
| `var:HISTTIMEFORMAT` | 1 | 1 | 0 | 0 |
| `var:HOME` | 1 | 1 | 0 | 0 |
| `var:HOSTFILE` | 1 | 1 | 0 | 0 |
| `var:IFS` | 1 | 1 | 0 | 0 |
| `var:LANG` | 1 | 1 | 0 | 0 |
| `var:LC_ALL` | 1 | 1 | 0 | 0 |
| `var:LC_CTYPE` | 1 | 1 | 0 | 0 |
| `var:LC_MESSAGES` | 1 | 1 | 0 | 0 |
| `var:LINENO` | 1 | 1 | 0 | 0 |
| `var:MAIL` | 1 | 1 | 0 | 0 |
| `var:MAILPATH` | 1 | 1 | 0 | 0 |
| `var:OLDPWD` | 1 | 1 | 0 | 0 |
| `var:OPTARG` | 1 | 1 | 0 | 0 |
| `var:OPTIND` | 1 | 1 | 0 | 0 |
| `var:PATH` | 1 | 1 | 0 | 0 |
| `var:PPID` | 1 | 1 | 0 | 0 |
| `var:PROMPT_COMMAND` | 1 | 1 | 0 | 0 |
| `var:PS0` | 1 | 1 | 0 | 0 |
| `var:PS1` | 1 | 1 | 0 | 0 |
| `var:PS2` | 1 | 1 | 0 | 0 |
| `var:PS3` | 1 | 1 | 0 | 0 |
| `var:PS4` | 1 | 1 | 0 | 0 |
| `var:PWD` | 1 | 1 | 0 | 0 |
| `var:RANDOM` | 1 | 1 | 0 | 0 |
| `var:REPLY` | 1 | 1 | 0 | 0 |
| `var:SECONDS` | 1 | 1 | 0 | 0 |
| `var:SHELLOPTS` | 1 | 1 | 0 | 0 |
| `var:SRANDOM` | 1 | 1 | 0 | 0 |
| `var:TIMEFORMAT` | 1 | 1 | 0 | 0 |
| `var:TMOUT` | 1 | 1 | 0 | 0 |
| `var:UID` | 1 | 1 | 0 | 0 |

## Feature Topics

### `builtin:.`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.DOT` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-05-dot-source` | . |

Notes:

- `C5.BUILTIN.DOT`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin::`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.COLON` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-04-misc-builtins` | : |

Notes:

- `C5.BUILTIN.COLON`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:[`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.LBRACK` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-03-io-signals.sh` | [ |

Notes:

- `C5.BUILTIN.LBRACK`: Mapped to test/[ parity case via man-bash-posix-03-io-signals.sh.

### `builtin:alias`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.003` | `bash-posix-doc` | bash/POSIX 6.11.2 item 3 | `covered / covered` | `bash-posix-doc-003.sh` | Alias expansion is always enabled, even in non-interactive shells. |
| `BPOSIX.CORE.004` | `bash-posix-doc` | bash/POSIX 6.11.2 item 4 | `covered / covered` | `bash-posix-doc-004.sh` | Reserved words appearing in a context where reserved words are recognized do not undergo alias expansion. |
| `BPOSIX.CORE.005` | `bash-posix-doc` | bash/POSIX 6.11.2 item 5 | `covered / covered` | `bash-posix-doc-005.sh` | Alias expansion is performed when initially parsing a command substitution. The default (non-posix) mode generally defers it, when enabled, until the command substitution is executed. This means that command substitution will not expand aliases that are defined after the command substitution is initially parsed (e.g., as part of a function definition). |
| `BPOSIX.CORE.047` | `bash-posix-doc` | bash/POSIX 6.11.2 item 47 | `covered / covered` | `bash-posix-doc-047.sh` | When the ‘alias’ builtin displays alias definitions, it does not display them with a leading ‘alias ’ unless the ‘-p’ option is supplied. |
| `C5.BUILTIN.ALIAS` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-04-misc-builtins` | alias |

Notes:

- `BPOSIX.CORE.003`: Row-level comparator evidence passes in tests/diff/cases/bash-posix-doc-001-010.sh; Source: bash/POSIX 6.11.2 item 3.
- `BPOSIX.CORE.004`: Row-level comparator evidence passes in tests/diff/cases/bash-posix-doc-001-010.sh; Source: bash/POSIX 6.11.2 item 4.
- `BPOSIX.CORE.005`: Row-level comparator evidence passes in tests/diff/cases/bash-posix-doc-001-010.sh; Source: bash/POSIX 6.11.2 item 5.
- `BPOSIX.CORE.047`: Strict comparator case validates alias display format difference between `alias` and `alias -p`.
- `C5.BUILTIN.ALIAS`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:bg`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.048` | `bash-posix-doc` | bash/POSIX 6.11.2 item 48 | `covered / covered` | `bash-posix-doc-048.sh` | The ‘bg’ builtin uses the required format to describe each job placed in the background, which does not include an indication of whether the job is the current or previous job. |
| `C5.BUILTIN.BG` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-10-jobs-fg-bg-interactive` | bg |
| `C8.JOB.04` | `bash-man` | bash(1) section SIGNALS + JOB CONTROL + builtins | `covered / covered` | `man-bash-posix-10-jobs-fg-bg-interactive.sh,man-ash-jobs.sh` | bg builtin jobspec resume in background |

Notes:

- `BPOSIX.CORE.048`: Strict comparator case validates POSIX mode option/reporting behavior for case row 48.
- `C5.BUILTIN.BG`: Seeded from tests/compat/bash_posix_man_coverage.tsv
- `C8.JOB.04`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.

### `builtin:bind`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BCOMPAT.52.002` | `bash-compat-doc` | bash/COMPAT level 52 item 2 | `partial / partial` | `bash-compat-doc-52-002.sh` | the -p and -P options to the bind builtin treat remaining arguments as bindable command names for which to print any key bindings |
| `C5.BUILTIN.BIND` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `bash-builtin-completion` | bind |
| `C7.INT.04` | `bash-man` | bash(1) section PROMPTING + READLINE + HISTORY | `covered / covered` | `run_completion_interactive_matrix.sh,bash-builtin-completion.sh` | bind builtin keymap/query/assignment |

Notes:

- `BCOMPAT.52.002`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat52 (set using BASH_COMPAT) i…
- `C5.BUILTIN.BIND`: Seeded from tests/compat/bash_posix_man_coverage.tsv
- `C7.INT.04`: Strict PTY interactive comparator evidence passes via run_interactive_ux_matrix.sh and run_completion_interactive_matrix.sh.

### `builtin:break`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BCOMPAT.43.002` | `bash-compat-doc` | bash/COMPAT level 43 item 2 | `partial / partial` | `bash-compat-doc-43-002.sh` | when executing a shell function, the loop state (while/until/etc.) is not reset, so `break' or `continue' in that function will break or continue loops in the calling context. Bash-4.4 and later reset the loop state to prevent this |
| `BCOMPAT.44.002` | `bash-compat-doc` | bash/COMPAT level 44 item 2 | `partial / partial` | `bash-compat-doc-44-002.sh` | a subshell inherits loops from its parent context, so `break' or `continue' will cause the subshell to exit. Bash-5.0 and later reset the loop state to prevent the exit |
| `C5.BUILTIN.BREAK` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-06-loop-control` | break |

Notes:

- `BCOMPAT.43.002`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat43 item 2; compatibility del…
- `BCOMPAT.44.002`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat44 item 2; compatibility del…
- `C5.BUILTIN.BREAK`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:builtin`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.BUILTIN` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-07-builtin-dispatch` | builtin |

Notes:

- `C5.BUILTIN.BUILTIN`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:caller`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.CALLER` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-11-extension-builtins-core` | caller |

Notes:

- `C5.BUILTIN.CALLER`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:cd`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.049` | `bash-posix-doc` | bash/POSIX 6.11.2 item 49 | `covered / covered` | `bash-posix-doc-049.sh` | When the ‘cd’ builtin is invoked in logical mode, and the pathname constructed from ‘$PWD’ and the directory name supplied as an argument does not refer to an existing directory, ‘cd’ will fail instead of falling back to physical mode. |
| `BPOSIX.CORE.050` | `bash-posix-doc` | bash/POSIX 6.11.2 item 50 | `covered / covered` | `bash-posix-doc-050.sh` | When the ‘cd’ builtin cannot change a directory because the length of the pathname constructed from ‘$PWD’ and the directory name supplied as an argument exceeds ‘PATH_MAX’ when canonicalized, ‘cd’ will attempt to use the supplied directory name. |
| `C5.BUILTIN.CD` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-02-path-command` | cd |

Notes:

- `BPOSIX.CORE.049`: Strict comparator case validates POSIX mode behavior for case row 49.
- `BPOSIX.CORE.050`: Strict comparator case validates POSIX mode behavior for case row 50.
- `C5.BUILTIN.CD`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:command`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BCOMPAT.31.001` | `bash-compat-doc` | bash/COMPAT level 31 item 1 | `partial / partial` | `bash-compat-doc-31-001.sh` | the < and > operators to the [[ command do not consider the current locale when comparing strings; they use ASCII ordering |
| `BCOMPAT.31.002` | `bash-compat-doc` | bash/COMPAT level 31 item 2 | `partial / partial` | `bash-compat-doc-31-002.sh` | quoting the rhs of the [[ command's regexp matching operator (=~) has no special effect |
| `BCOMPAT.32.001` | `bash-compat-doc` | bash/COMPAT level 32 item 1 | `partial / partial` | `bash-compat-doc-32-001.sh` | the < and > operators to the [[ command do not consider the current locale when comparing strings; they use ASCII ordering |
| `BCOMPAT.40.001` | `bash-compat-doc` | bash/COMPAT level 40 item 1 | `partial / partial` | `bash-compat-doc-40-001.sh` | the < and > operators to the [[ command do not consider the current locale when comparing strings; they use ASCII ordering. Bash versions prior to bash-4.1 use ASCII collation and strcmp(3); bash-4.1 and later use the current locale's collation sequence and strcoll(3). |
| `BCOMPAT.43.001` | `bash-compat-doc` | bash/COMPAT level 43 item 1 | `partial / partial` | `bash-compat-doc-43-001.sh` | word expansion errors are considered non-fatal errors that cause the current command to fail, even in posix mode (the default behavior is to make them fatal errors that cause the shell to exit) |
| `BCOMPAT.50.002` | `bash-compat-doc` | bash/COMPAT level 50 item 2 | `partial / partial` | `bash-compat-doc-50-002.sh` | If the command hash table is empty, bash versions prior to bash-5.1 printed an informational message to that effect even when writing output in a format that can be reused as input (-l). Bash-5.1 suppresses that message if -l is supplied |
| `BCOMPAT.51.003` | `bash-compat-doc` | bash/COMPAT level 51 item 3 | `partial / partial` | `bash-compat-doc-51-003.sh` | expressions used as arguments to arithmetic operators in the [[ conditional command can be expanded more than once |
| `BCOMPAT.51.004` | `bash-compat-doc` | bash/COMPAT level 51 item 4 | `partial / partial` | `bash-compat-doc-51-004.sh` | indexed and associative array subscripts used as arguments to the operators in the [[ conditional command (e.g., `[[ -v') can be expanded more than once. Bash-5.2 behaves as if the `assoc_expand_once' option were enabled. |
| `BCOMPAT.51.010` | `bash-compat-doc` | bash/COMPAT level 51 item 10 | `partial / partial` | `bash-compat-doc-51-010.sh` | Parsing command substitutions will act as if extended glob is enabled, so that parsing a command substitution containing an extglob pattern (say, as part of a shell function) will not fail. This assumes the intent is to enable extglob before the command is executed and word expansions are performed. It will fail at word expansion time if extglob hasn't been enabled by the time the command is executed. |
| `BPOSIX.CORE.006` | `bash-posix-doc` | bash/POSIX 6.11.2 item 6 | `covered / covered` | `bash-posix-doc-006.sh` | The ‘time’ reserved word may be used by itself as a simple command. When used in this way, it displays timing statistics for the shell and its completed children. The ‘TIMEFORMAT’ variable controls the format of the timing information. |
| `BPOSIX.CORE.012` | `bash-posix-doc` | bash/POSIX 6.11.2 item 12 | `covered / covered` | `bash-posix-doc-012.sh` | Tilde expansion is only performed on assignments preceding a command name, rather than on all assignment statements on the line. |
| `BPOSIX.CORE.015` | `bash-posix-doc` | bash/POSIX 6.11.2 item 15 | `covered / covered` | `bash-posix-doc-015.sh` | A double quote character (‘"’) is treated specially when it appears in a backquoted command substitution in the body of a here-document that undergoes expansion. That means, for example, that a backslash preceding a double quote character will escape it and the backslash will be removed. |
| `BPOSIX.CORE.016` | `bash-posix-doc` | bash/POSIX 6.11.2 item 16 | `covered / covered` | `bash-posix-doc-016.sh` | Command substitutions don't set the ‘?’ special parameter. The exit status of a simple command without a command word is still the exit status of the last command substitution that occurred while evaluating the variable assignments and redirections in that command, but that does not happen until after all of the assignments and redirections. |
| `BPOSIX.CORE.020` | `bash-posix-doc` | bash/POSIX 6.11.2 item 20 | `covered / covered` | `bash-posix-doc-020.sh` | When a command in the hash table no longer exists, Bash will re-search ‘$PATH’ to find the new location. This is also available with ‘shopt -s checkhash’. |
| `BPOSIX.CORE.021` | `bash-posix-doc` | bash/POSIX 6.11.2 item 21 | `covered / covered` | `bash-posix-doc-021.sh` | Bash will not insert a command without the execute bit set into the command hash table, even if it returns it as a (last-ditch) result from a ‘$PATH’ search. |
| `BPOSIX.CORE.027` | `bash-posix-doc` | bash/POSIX 6.11.2 item 27 | `covered / covered` | `bash-posix-doc-027.sh` | The ‘vi’ editing mode will invoke the ‘vi’ editor directly when the ‘v’ command is run, instead of checking ‘$VISUAL’ and ‘$EDITOR’. |
| `BPOSIX.CORE.034` | `bash-posix-doc` | bash/POSIX 6.11.2 item 34 | `covered / covered` | `bash-posix-doc-034.sh` | If a POSIX special builtin returns an error status, a non-interactive shell exits. The fatal errors are those listed in the POSIX standard, and include things like passing incorrect options, redirection errors, variable assignment errors for assignments preceding the command name, and so on. |
| `BPOSIX.CORE.035` | `bash-posix-doc` | bash/POSIX 6.11.2 item 35 | `covered / covered` | `bash-posix-doc-035.sh` | A non-interactive shell exits with an error status if a variable assignment error occurs when no command name follows the assignment statements. A variable assignment error occurs, for example, when trying to assign a value to a readonly variable. |
| `BPOSIX.CORE.036` | `bash-posix-doc` | bash/POSIX 6.11.2 item 36 | `covered / covered` | `bash-posix-doc-036.sh` | A non-interactive shell exits with an error status if a variable assignment error occurs in an assignment statement preceding a special builtin, but not with any other simple command. For any other simple command, the shell aborts execution of that command, and execution continues at the top level ("the shell shall not perform any further processing of the command in which the error occurred"). |
| `BPOSIX.CORE.042` | `bash-posix-doc` | bash/POSIX 6.11.2 item 42 | `covered / covered` | `bash-posix-doc-042.sh` | The ‘command’ builtin does not prevent builtins that take assignment statements as arguments from expanding them as assignment statements; when not in POSIX mode, declaration commands lose their assignment statement expansion properties when preceded by ‘command’. |
| `BPOSIX.CORE.043` | `bash-posix-doc` | bash/POSIX 6.11.2 item 43 | `covered / covered` | `bash-posix-doc-043.sh` | Enabling POSIX mode has the effect of setting the ‘inherit_errexit’ option, so subshells spawned to execute command substitutions inherit the value of the ‘-e’ option from the parent shell. When the ‘inherit_errexit’ option is not enabled, Bash clears the ‘-e’ option in such subshells. |
| `C2.GRAM.001` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | simple command |
| `C2.GRAM.008` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | compound command: ( list ) subshell |
| `C2.GRAM.009` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | compound command: { list; } grouping |
| `C2.GRAM.022` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh,man-ash-grammar-word-matrix.sh` | [[ conditional command ]] |
| `C2.GRAM.023` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh,man-ash-grammar-word-matrix.sh` | (( arithmetic command )) |
| `C2.GRAM.024` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-select-coproc.sh` | coproc command |
| `C2.GRAM.026` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | newline as command separator |
| `C3.EXP.021` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `bash-man-expansion-core.sh` | command substitution $(cmd) |
| `C3.EXP.030` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `bash-man-expansion-core.sh` | command substitution newline trimming |
| `C5.BUILTIN.COMMAND` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-02-path-command` | command |
| `C7.INT.11` | `bash-man` | bash(1) section PROMPTING + Shell Variables | `covered / covered` | `run_interactive_ux_matrix.sh` | PS1 parameter/command/arithmetic expansion at prompt render time (promptvars) |
| `C8.JOB.13` | `bash-man` | bash(1) section SIGNALS + JOB CONTROL | `covered / covered` | `run_interactive_sigint_matrix.sh` | interactive Ctrl-C during foreground external command returns prompt and keeps shell alive |
| `C9.COMP.01` | `bash-man` | bash(1) section SHELL COMPATIBILITY MODE + RESTRICTED SHELL | `covered / covered` | `run_startup_mode_matrix.sh,man-bash-posix-08-declare-posix-policy.sh` | restricted shell command/path assignment limits |

Notes:

- `BCOMPAT.31.001`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat31 item 1; compatibility del…
- `BCOMPAT.31.002`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat31 item 2; compatibility del…
- `BCOMPAT.32.001`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat32 item 1; compatibility del…
- `BCOMPAT.40.001`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat40 item 1; compatibility del…
- `BCOMPAT.43.001`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat43 item 1; compatibility del…
- `BCOMPAT.50.002`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat50 (set using BASH_COMPAT) i…
- `BCOMPAT.51.003`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat51 (set using BASH_COMPAT) i…
- `BCOMPAT.51.004`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat51 (set using BASH_COMPAT) i…
- (Plus 26 additional row notes; see `docs/specs/feature-index.tsv`.)

### `builtin:compgen`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.COMPGEN` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `bash-builtin-completion` | compgen |
| `C7.INT.08` | `bash-man` | bash(1) section PROMPTING + READLINE + HISTORY | `covered / covered` | `run_completion_interactive_matrix.sh,bash-builtin-completion.sh` | programmable completion complete/compgen/compopt |

Notes:

- `C5.BUILTIN.COMPGEN`: Seeded from tests/compat/bash_posix_man_coverage.tsv
- `C7.INT.08`: Strict PTY interactive comparator evidence passes via run_interactive_ux_matrix.sh and run_completion_interactive_matrix.sh.

### `builtin:complete`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.COMPLETE` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `bash-builtin-completion` | complete |

Notes:

- `C5.BUILTIN.COMPLETE`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:compopt`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.COMPOPT` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `bash-builtin-completion` | compopt |

Notes:

- `C5.BUILTIN.COMPOPT`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:continue`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BCOMPAT.44.003` | `bash-compat-doc` | bash/COMPAT level 44 item 3 | `partial / partial` | `bash-compat-doc-44-003.sh` | variable assignments preceding builtins like export and readonly that set attributes continue to affect variables with the same name in the calling environment even if the shell is not in posix mode |
| `C5.BUILTIN.CONTINUE` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-06-loop-control` | continue |

Notes:

- `BCOMPAT.44.003`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat44 item 3; compatibility del…
- `C5.BUILTIN.CONTINUE`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:declare`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C10.STATE.01` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh,man-bash-posix-14-env-exec-flow.sh,bash-builtin-declare-typeset-local.sh` | variables assignment attributes (declare/local/typeset) |
| `C5.BUILTIN.DECLARE` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-08-declare-posix-policy` | declare |

Notes:

- `C10.STATE.01`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C5.BUILTIN.DECLARE`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:dirs`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.DIRS` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `bash-builtin-dirstack` | dirs |

Notes:

- `C5.BUILTIN.DIRS`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:disown`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.DISOWN` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `bash-builtin-disown` | disown |

Notes:

- `C5.BUILTIN.DISOWN`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:echo`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.051` | `bash-posix-doc` | bash/POSIX 6.11.2 item 51 | `covered / covered` | `bash-posix-doc-051.sh` | When the ‘xpg_echo’ option is enabled, Bash does not attempt to interpret any arguments to ‘echo’ as options. ‘echo’ displays each argument after converting escape sequences. |
| `BPOSIX.EXTRA.003` | `bash-posix-doc` | bash/POSIX 6.11.2 item 3 | `covered / covered` | `bash-posix-doc-extra-003.sh` | As noted above, Bash requires the ‘xpg_echo’ option to be enabled for the ‘echo’ builtin to be fully conformant. |
| `C5.BUILTIN.ECHO` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-04-misc-builtins` | echo |

Notes:

- `BPOSIX.CORE.051`: Strict comparator case validates xpg_echo interaction in POSIX lane.
- `BPOSIX.EXTRA.003`: Policy update: in both bash and posix lanes, xpg_echo behavior follows bash --posix-compatible semantics for this row; validated by bash-po…
- `C5.BUILTIN.ECHO`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:enable`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.ENABLE` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `bash-builtin-enable` | enable |

Notes:

- `C5.BUILTIN.ENABLE`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:eval`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.EVAL` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-04-misc-builtins` | eval |

Notes:

- `C5.BUILTIN.EVAL`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:exec`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.EXEC` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-04-misc-builtins` | exec |
| `C7.INT.07` | `bash-man` | bash(1) section PROMPTING + READLINE + HISTORY | `covered / covered` | `run_interactive_ux_matrix.sh,man-bash-posix-12-history-suspend-logout.sh` | fc editor/list/re-exec flows |

Notes:

- `C5.BUILTIN.EXEC`: Seeded from tests/compat/bash_posix_man_coverage.tsv
- `C7.INT.07`: Strict PTY interactive comparator evidence passes via run_interactive_ux_matrix.sh and run_completion_interactive_matrix.sh.

### `builtin:exit`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.032` | `bash-posix-doc` | bash/POSIX 6.11.2 item 32 | `covered / covered` | `bash-posix-doc-032.sh` | Non-interactive shells exit if a syntax error in an arithmetic expansion results in an invalid expression. |
| `BPOSIX.CORE.033` | `bash-posix-doc` | bash/POSIX 6.11.2 item 33 | `covered / covered` | `bash-posix-doc-033.sh` | Non-interactive shells exit if a parameter expansion error occurs. |
| `BPOSIX.CORE.038` | `bash-posix-doc` | bash/POSIX 6.11.2 item 38 | `covered / covered` | `bash-posix-doc-038.sh` | Non-interactive shells exit if FILENAME in ‘.’ FILENAME is not found. |
| `C5.BUILTIN.EXIT` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-09-return-exit` | exit |
| `C8.JOB.09` | `bash-man` | bash(1) section SIGNALS + JOB CONTROL + builtins | `covered / covered` | `man-ash-trap-signal-matrix.sh,man-ash-trap-delivery.sh` | EXIT trap semantics |
| `C8.JOB.27` | `bash-man` | bash(1) section JOB CONTROL | `covered / covered` | `run_job_exitwarn_matrix.sh` | `exit` with stopped jobs warns once; second exit terminates stopped jobs |

Notes:

- `BPOSIX.CORE.032`: Strict semantic parity case: arithmetic expansion syntax error in non-interactive shell exits before post-line.
- `BPOSIX.CORE.033`: Strict semantic parity case: parameter expansion error in non-interactive shell exits before post-line.
- `BPOSIX.CORE.038`: Strict semantic parity case: missing dot/source file is fatal in non-interactive shell.
- `C5.BUILTIN.EXIT`: Seeded from tests/compat/bash_posix_man_coverage.tsv
- `C8.JOB.09`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C8.JOB.27`: Interactive strict exitwarn matrix now covers first-exit warning continuation and second-exit stopped-job termination (pid liveness parity …

### `builtin:export`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.040` | `bash-posix-doc` | bash/POSIX 6.11.2 item 40 | `covered / covered` | `bash-posix-doc-040.sh` | Non-interactive shells exit if the ‘export’, ‘readonly’ or ‘unset’ builtin commands get an argument that is not a valid identifier, and they are not operating on shell functions. These errors force an exit because these are special builtins. |
| `BPOSIX.CORE.052` | `bash-posix-doc` | bash/POSIX 6.11.2 item 52 | `covered / covered` | `bash-posix-doc-052.sh` | The ‘export’ and ‘readonly’ builtin commands display their output in the format required by POSIX. |
| `C10.STATE.02` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh,man-bash-posix-14-env-exec-flow.sh,bash-builtin-declare-typeset-local.sh` | readonly/export attribute propagation |
| `C10.STATE.04` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh,man-bash-posix-14-env-exec-flow.sh,bash-builtin-declare-typeset-local.sh` | environment import/export behavior |
| `C5.BUILTIN.EXPORT` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-01-core-state` | export |

Notes:

- `BPOSIX.CORE.040`: Strict semantic parity case: invalid identifier to special builtins exits non-interactive shell.
- `BPOSIX.CORE.052`: Strict comparator case validates export/readonly print behavior with `-p` in POSIX lane.
- `C10.STATE.02`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C10.STATE.04`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C5.BUILTIN.EXPORT`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:false`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.FALSE` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-04-misc-builtins` | false |

Notes:

- `C5.BUILTIN.FALSE`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:fc`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.053` | `bash-posix-doc` | bash/POSIX 6.11.2 item 53 | `covered / covered` | `bash-posix-doc-053.sh` | When listing the history, the ‘fc’ builtin does not include an indication of whether or not a history entry has been modified. |
| `BPOSIX.CORE.054` | `bash-posix-doc` | bash/POSIX 6.11.2 item 54 | `covered / covered` | `bash-posix-doc-054.sh` | The default editor used by ‘fc’ is ‘ed’. |
| `BPOSIX.CORE.055` | `bash-posix-doc` | bash/POSIX 6.11.2 item 55 | `covered / covered` | `bash-posix-doc-055.sh` | ‘fc’ treats extra arguments as an error instead of ignoring them. |
| `BPOSIX.CORE.056` | `bash-posix-doc` | bash/POSIX 6.11.2 item 56 | `covered / covered` | `bash-posix-doc-056.sh` | If there are too many arguments supplied to ‘fc -s’, ‘fc’ prints an error message and returns failure. |
| `BPOSIX.EXTRA.002` | `bash-posix-doc` | bash/POSIX 6.11.2 item 2 | `covered / covered` | `bash-posix-doc-extra-002.sh` | The ‘fc’ builtin checks ‘$EDITOR’ as a program to edit history entries if ‘FCEDIT’ is unset, rather than defaulting directly to ‘ed’. ‘fc’ uses ‘ed’ if ‘EDITOR’ is unset. |
| `C5.BUILTIN.FC` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-ash-fc` | fc |
| `C5.BUILTIN.FC.EMPTY` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-ash-fc-empty-history` | fc empty-history behavior |
| `C5.BUILTIN.FC.ENV` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-ash-fc-editor-env` | fc editor env propagation |
| `C5.BUILTIN.FC.EOVERRIDE` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-ash-fc-e-override` | fc -e override precedence |
| `C5.BUILTIN.FC.REF` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-ash-fc-ref-precedence` | fc reference precedence |
| `C7.INT.07.FC` | `bash-man` | bash(1) section PROMPTING + READLINE + HISTORY | `covered / covered` | `run_fc_interactive_matrix.sh` | fc interactive editor execution flow |

Notes:

- `BPOSIX.CORE.053`: Strict comparator probe validates `fc -l` list status and absence of `*` modified markers. Source: bash/POSIX 6.11.2 item 53.
- `BPOSIX.CORE.054`: Comparator-backed row probe for default-editor lane (`fc -e -`) now strict on status shape under harness constraints. Source: bash/POSIX 6.…
- `BPOSIX.CORE.055`: Strict comparator probe asserts failure status + stderr presence for extra-arg `fc` invocation. Source: bash/POSIX 6.11.2 item 55.
- `BPOSIX.CORE.056`: Strict comparator probe asserts failure status + stderr presence for over-arg `fc -s` invocation. Source: bash/POSIX 6.11.2 item 56.
- `BPOSIX.EXTRA.002`: Strict comparator probe validates EDITOR fallback path when FCEDIT is unset by observing deterministic editor invocation marker. Source: ba…
- `C5.BUILTIN.FC`: Seeded from tests/compat/bash_posix_man_coverage.tsv
- `C5.BUILTIN.FC.EMPTY`: Strict comparator case covers empty-history behavior for list/edit/reexec/substitute forms.
- `C5.BUILTIN.FC.ENV`: Strict comparator case verifies fc editor subprocess observes shell runtime env snapshot.
- (Plus 3 additional row notes; see `docs/specs/feature-index.tsv`.)

### `builtin:fg`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.FG` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-10-jobs-fg-bg-interactive` | fg |
| `C8.JOB.03` | `bash-man` | bash(1) section SIGNALS + JOB CONTROL + builtins | `covered / covered` | `man-bash-posix-10-jobs-fg-bg-interactive.sh,man-ash-jobs.sh` | fg builtin jobspec resume in foreground |
| `C8.JOB.24` | `bash-man` | bash(1) section JOB CONTROL | `covered / covered` | `bash-man-jobcontrol-jobspec-command-forms.sh,run_jobs_interactive_matrix.sh` | `%jobspec` and `%jobspec &` command forms map to `fg` and `bg` behavior |

Notes:

- `C5.BUILTIN.FG`: Seeded from tests/compat/bash_posix_man_coverage.tsv
- `C8.JOB.03`: Strict job-control/signal comparator evidence passes via run_jobs_interactive_matrix.sh, run_trap_noninteractive_matrix.sh, and run_trap_in…
- `C8.JOB.24`: Dedicated non-interactive and PTY interactive comparator cases cover `%jobspec` foreground/background shorthand dispatch and redirection-sa…

### `builtin:getopts`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.GETOPTS` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-01-core-state` | getopts |

Notes:

- `C5.BUILTIN.GETOPTS`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:hash`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.HASH` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-02-path-command` | hash |

Notes:

- `C5.BUILTIN.HASH`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:help`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C1.OPT.LONG.HELP` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | --help |
| `C5.BUILTIN.HELP` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `bash-builtin-help` | help |

Notes:

- `C1.OPT.LONG.HELP`: Mapped by run_bash_invocation_option_matrix.sh (and startup mode matrix where applicable); comparator evidence run passes in default and --…
- `C5.BUILTIN.HELP`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:history`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.028` | `bash-posix-doc` | bash/POSIX 6.11.2 item 28 | `covered / covered` | `bash-posix-doc-028.sh` | Prompt expansion enables the POSIX ‘PS1’ and ‘PS2’ expansions of ‘!’ to the history number and ‘!!’ to ‘!’, and Bash performs parameter expansion on the values of ‘PS1’ and ‘PS2’ regardless of the setting of the ‘promptvars’ option. |
| `BPOSIX.CORE.029` | `bash-posix-doc` | bash/POSIX 6.11.2 item 29 | `covered / covered` | `bash-posix-doc-029.sh` | The default history file is ‘~/.sh_history’ (this is the default value the shell assigns to ‘$HISTFILE’). |
| `BPOSIX.CORE.030` | `bash-posix-doc` | bash/POSIX 6.11.2 item 30 | `covered / covered` | `bash-posix-doc-030.sh` | The ‘!’ character does not introduce history expansion within a double-quoted string, even if the ‘histexpand’ option is enabled. |
| `C1.OPT.SETO.HISTORY` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | history |
| `C5.BUILTIN.HISTORY` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-12-history-suspend-logout` | history |
| `C7.INT.05` | `bash-man` | bash(1) section PROMPTING + READLINE + HISTORY | `covered / covered` | `run_interactive_ux_matrix.sh,man-bash-posix-12-history-suspend-logout.sh` | history list/edit/delete/write/read |
| `C7.INT.06` | `bash-man` | bash(1) section PROMPTING + READLINE + HISTORY | `covered / covered` | `run_interactive_ux_matrix.sh,man-bash-posix-12-history-suspend-logout.sh` | history expansion ! forms |

Notes:

- `BPOSIX.CORE.028`: Comparator case validates promptvars/PS1 behavior in POSIX interactive lane.
- `BPOSIX.CORE.029`: Strict comparator case validates default HISTFILE state in POSIX mode.
- `BPOSIX.CORE.030`: Strict comparator case validates `!` handling in double quotes under POSIX mode.
- `C1.OPT.SETO.HISTORY`: Mapped by bash-man-seto-surface.sh; comparator evidence run passes in default and --posix lanes.
- `C5.BUILTIN.HISTORY`: Seeded from tests/compat/bash_posix_man_coverage.tsv
- `C7.INT.05`: Strict PTY interactive comparator evidence passes via run_interactive_ux_matrix.sh and run_completion_interactive_matrix.sh.
- `C7.INT.06`: Strict PTY interactive comparator evidence passes via run_interactive_ux_matrix.sh and run_completion_interactive_matrix.sh.

### `builtin:jobs`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BCOMPAT.52.003` | `bash-compat-doc` | bash/COMPAT level 52 item 3 | `partial / partial` | `bash-compat-doc-52-003.sh` | interactive shells will notify the user of completed jobs while sourcing a script. Newer versions defer notification until script execution completes. |
| `C5.BUILTIN.JOBS` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-10-jobs-fg-bg-interactive` | jobs |
| `C8.JOB.02` | `bash-man` | bash(1) section SIGNALS + JOB CONTROL + builtins | `covered / covered` | `man-bash-posix-10-jobs-fg-bg-interactive.sh,man-ash-jobs.sh` | jobs builtin listing forms |
| `C8.JOB.07` | `bash-man` | bash(1) section SIGNALS + JOB CONTROL + builtins | `covered / covered` | `man-ash-trap-signal-matrix.sh,man-ash-trap-delivery.sh` | signal delivery to foreground jobs |
| `C8.JOB.15` | `bash-man` | bash(1) section JOB CONTROL | `covered / covered` | `man-bash-posix-10-jobs-fg-bg-interactive.sh,run_jobs_interactive_matrix.sh` | background launch banner `[job] pid` is emitted for async jobs |

Notes:

- `BCOMPAT.52.003`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat52 (set using BASH_COMPAT) i…
- `C5.BUILTIN.JOBS`: Seeded from tests/compat/bash_posix_man_coverage.tsv
- `C8.JOB.02`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C8.JOB.07`: Strict job-control/signal comparator evidence passes via run_jobs_interactive_matrix.sh, run_trap_noninteractive_matrix.sh, and run_trap_in…
- `C8.JOB.15`: Dedicated strict comparator lane (`bg-launch-banner`) asserts interactive async launch banner presence and format parity (PID normalized).;…

### `builtin:kill`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.057` | `bash-posix-doc` | bash/POSIX 6.11.2 item 57 | `covered / covered` | `bash-posix-doc-057.sh` | The output of ‘kill -l’ prints all the signal names on a single line, separated by spaces, without the ‘SIG’ prefix. |
| `BPOSIX.CORE.058` | `bash-posix-doc` | bash/POSIX 6.11.2 item 58 | `covered / covered` | `bash-posix-doc-058.sh` | The ‘kill’ builtin does not accept signal names with a ‘SIG’ prefix. |
| `BPOSIX.CORE.059` | `bash-posix-doc` | bash/POSIX 6.11.2 item 59 | `covered / covered` | `bash-posix-doc-059.sh` | The ‘kill’ builtin returns a failure status if any of the pid or job arguments are invalid or if sending the specified signal to any of them fails. In default mode, ‘kill’ returns success if the signal was successfully sent to any of the specified processes. |
| `C5.BUILTIN.KILL` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-03-io-signals` | kill |

Notes:

- `BPOSIX.CORE.057`: Strict comparator case validates POSIX row 57 behavior in current runtime lane.
- `BPOSIX.CORE.058`: Strict comparator case validates kill SIG-prefix rejection in POSIX mode.
- `BPOSIX.CORE.059`: Strict comparator case validates POSIX row 59 behavior in current runtime lane.
- `C5.BUILTIN.KILL`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:let`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.LET` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-11-extension-builtins-core` | let |

Notes:

- `C5.BUILTIN.LET`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:local`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.LOCAL` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `bash-builtin-declare-typeset-local` | local |

Notes:

- `C5.BUILTIN.LOCAL`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:logout`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.LOGOUT` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-12-history-suspend-logout` | logout |

Notes:

- `C5.BUILTIN.LOGOUT`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:mapfile`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.MAPFILE` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `bash-compat-mapfile-readarray` | mapfile |

Notes:

- `C5.BUILTIN.MAPFILE`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:popd`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.POPD` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `bash-builtin-dirstack` | popd |

Notes:

- `C5.BUILTIN.POPD`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:printf`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.060` | `bash-posix-doc` | bash/POSIX 6.11.2 item 60 | `covered / covered` | `bash-posix-doc-060.sh` | The ‘printf’ builtin uses ‘double’ (via ‘strtod’) to convert arguments corresponding to floating point conversion specifiers, instead of ‘long double’ if it's available. The ‘L’ length modifier forces ‘printf’ to use ‘long double’ if it's available. |
| `C5.BUILTIN.PRINTF` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-04-misc-builtins` | printf |

Notes:

- `BPOSIX.CORE.060`: Strict comparator case validates printf floating-point conversion behavior.
- `C5.BUILTIN.PRINTF`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:pushd`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.PUSHD` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `bash-builtin-dirstack` | pushd |

Notes:

- `C5.BUILTIN.PUSHD`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:pwd`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.061` | `bash-posix-doc` | bash/POSIX 6.11.2 item 61 | `covered / covered` | `bash-posix-doc-061.sh` | The ‘pwd’ builtin verifies that the value it prints is the same as the current directory, even if it is not asked to check the file system with the ‘-P’ option. |
| `C5.BUILTIN.PWD` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-02-path-command` | pwd |

Notes:

- `BPOSIX.CORE.061`: Strict comparator case validates POSIX row 61 behavior in current runtime lane.
- `C5.BUILTIN.PWD`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:read`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.062` | `bash-posix-doc` | bash/POSIX 6.11.2 item 62 | `covered / covered` | `bash-posix-doc-062.sh` | The ‘read’ builtin may be interrupted by a signal for which a trap has been set. If Bash receives a trapped signal while executing ‘read’, the trap handler executes and ‘read’ returns an exit status greater than 128. |
| `C4.REDIR.004` | `bash-man` | bash(1) section REDIRECTION | `covered / covered` | `man-ash-redir-heredoc-matrix.sh` | [n]<>word read/write redirection |
| `C5.BUILTIN.READ` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-03-io-signals` | read |
| `C8.JOB.18` | `bash-man` | bash(1) section JOB CONTROL | `covered / covered` | `run_job_tty_stop_matrix.sh` | background process read from controlling tty gets SIGTTIN stop |
| `C8.JOB.21` | `bash-man` | bash(1) section JOB CONTROL | `covered / covered` | `bash-man-jobcontrol-suspend-y.sh,run_job_suspend_ctrl_matrix.sh` | delayed suspend char ^Y stops on terminal-read attempt |

Notes:

- `BPOSIX.CORE.062`: Strict comparator case validates read interruption status with trapped signal path.
- `C4.REDIR.004`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C5.BUILTIN.READ`: Seeded from tests/compat/bash_posix_man_coverage.tsv
- `C8.JOB.18`: Interactive PTY comparator `sigttin` lane verifies background tty-read job transitions to `Stopped(SIGTTIN)` and remains jobspec-addressabl…
- `C8.JOB.21`: Covered in comparator scope with informational `^Y` (`dsusp`) probing lane and explicit terminal-driver caveat for non-deterministic PTY au…

### `builtin:readarray`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.READARRAY` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `bash-compat-mapfile-readarray` | readarray |

Notes:

- `C5.BUILTIN.READARRAY`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:readonly`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.037` | `bash-posix-doc` | bash/POSIX 6.11.2 item 37 | `covered / covered` | `bash-posix-doc-037.sh` | A non-interactive shell exits with an error status if the iteration variable in a ‘for’ statement or the selection variable in a ‘select’ statement is a readonly variable or has an invalid name. |
| `C5.BUILTIN.READONLY` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-01-core-state` | readonly |

Notes:

- `BPOSIX.CORE.037`: Strict semantic parity case: readonly for-loop iterator assignment is fatal in non-interactive shell.
- `C5.BUILTIN.READONLY`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:return`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BCOMPAT.51.008` | `bash-compat-doc` | bash/COMPAT level 51 item 8 | `partial / partial` | `bash-compat-doc-51-008.sh` | `test -v', when given an argument of A[@], where A is an existing associative array, will return true if the array has any set elements. Bash-5.2 will look for a key named `@'; |
| `BCOMPAT.51.009` | `bash-compat-doc` | bash/COMPAT level 51 item 9 | `partial / partial` | `bash-compat-doc-51-009.sh` | the ${param[:]=value} word expansion will return VALUE, before any variable-specific transformations have been performed (e.g., converting to lowercase). Bash-5.2 will return the final value assigned to the variable, as POSIX specifies; |
| `C5.BUILTIN.RETURN` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-09-return-exit` | return |
| `C8.JOB.10` | `bash-man` | bash(1) section SIGNALS + JOB CONTROL + builtins | `covered / covered` | `man-ash-trap-signal-matrix.sh,man-ash-trap-delivery.sh` | DEBUG/RETURN/ERR trap options and inheritance |

Notes:

- `BCOMPAT.51.008`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat51 (set using BASH_COMPAT) i…
- `BCOMPAT.51.009`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat51 (set using BASH_COMPAT) i…
- `C5.BUILTIN.RETURN`: Seeded from tests/compat/bash_posix_man_coverage.tsv
- `C8.JOB.10`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.

### `builtin:set`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BCOMPAT.50.001` | `bash-compat-doc` | bash/COMPAT level 50 item 1 | `partial / partial` | `bash-compat-doc-50-001.sh` | Bash-5.1 changed the way $RANDOM is generated to introduce slightly more randomness. If the shell compatibility level is set to 50 or lower, it reverts to the method from bash-5.0 and previous versions, so seeding the random number generator by assigning a value to RANDOM will produce the same sequence as in bash-5.0 |
| `BCOMPAT.50.003` | `bash-compat-doc` | bash/COMPAT level 50 item 3 | `partial / partial` | `bash-compat-doc-50-003.sh` | Bash-5.1 and later use pipes for here-documents and here-strings if they are smaller than the pipe capacity. If the shell compatibility level is set to 50 or lower, it reverts to using temporary files. |
| `BPOSIX.CORE.001` | `bash-posix-doc` | bash/POSIX 6.11.2 item 1 | `covered / covered` | `bash-posix-doc-001.sh` | Bash ensures that the ‘POSIXLY_CORRECT’ variable is set. |
| `BPOSIX.CORE.063` | `bash-posix-doc` | bash/POSIX 6.11.2 item 63 | `covered / covered` | `bash-posix-doc-063.sh` | When the ‘set’ builtin is invoked without options, it does not display shell function names and definitions. |
| `BPOSIX.CORE.064` | `bash-posix-doc` | bash/POSIX 6.11.2 item 64 | `covered / covered` | `bash-posix-doc-064.sh` | When the ‘set’ builtin is invoked without options, it displays variable values without quotes, unless they contain shell metacharacters, even if the result contains nonprinting characters. |
| `BPOSIX.CORE.069` | `bash-posix-doc` | bash/POSIX 6.11.2 item 69 | `covered / covered` | `bash-posix-doc-069.sh` | ‘trap -p’ without arguments displays signals whose dispositions are set to SIG_DFL and those that were ignored when the shell started, not just trapped signals. |
| `C11.MODE.01` | `bash-man` | bash(1) section OPTIONS + INVOCATION | `covered / covered` | `bash-man-seto-surface.sh,run_startup_mode_matrix.sh` | set -o option reporting format |
| `C5.BUILTIN.SET` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-01-core-state` | set |
| `C8.JOB.06` | `bash-man` | bash(1) section SIGNALS + JOB CONTROL + builtins | `covered / covered` | `man-ash-trap-signal-matrix.sh,man-ash-trap-delivery.sh` | trap set/list/clear handlers |
| `C8.JOB.11` | `bash-man` | bash(1) section SIGNALS + JOB CONTROL + builtins | `covered / covered` | `man-ash-set-monitor.sh` | set -m monitor mode behavior |
| `C8.JOB.12` | `bash-man` | bash(1) section SIGNALS + JOB CONTROL + builtins | `covered / covered` | `man-ash-set-monitor.sh` | notification mode set -b/notify |
| `C8.JOB.25` | `bash-man` | bash(1) section JOB CONTROL | `covered / covered` | `run_job_notify_matrix.sh` | job status notifications are deferred to prompt by default and immediate with `set -b` |

Notes:

- `BCOMPAT.50.001`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat50 (set using BASH_COMPAT) i…
- `BCOMPAT.50.003`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat50 (set using BASH_COMPAT) i…
- `BPOSIX.CORE.001`: Row-level comparator evidence now passes for --posix POSIXLY_CORRECT exposure in focused lane; Source: bash/POSIX 6.11.2 item 1.
- `BPOSIX.CORE.063`: Strict comparator case validates POSIX row 63 behavior in current runtime lane.
- `BPOSIX.CORE.064`: Strict comparator case validates POSIX row 64 behavior in current runtime lane.
- `BPOSIX.CORE.069`: Strict comparator case validates POSIX row 69 behavior in current runtime lane.
- `C11.MODE.01`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C5.BUILTIN.SET`: Seeded from tests/compat/bash_posix_man_coverage.tsv
- (Plus 4 additional row notes; see `docs/specs/feature-index.tsv`.)

### `builtin:shift`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.044` | `bash-posix-doc` | bash/POSIX 6.11.2 item 44 | `covered / covered` | `bash-posix-doc-044.sh` | Enabling POSIX mode has the effect of setting the ‘shift_verbose’ option, so numeric arguments to ‘shift’ that exceed the number of positional parameters will result in an error message. |
| `C5.BUILTIN.SHIFT` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-01-core-state` | shift |

Notes:

- `BPOSIX.CORE.044`: Strict comparator case validates special-builtin dispatch precedence in POSIX lane.
- `C5.BUILTIN.SHIFT`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:shopt`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C11.MODE.02` | `bash-man` | bash(1) section OPTIONS + INVOCATION | `covered / covered` | `bash-man-seto-surface.sh,run_startup_mode_matrix.sh` | shopt -p reporting format |
| `C5.BUILTIN.SHOPT` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-11-extension-builtins-core` | shopt |
| `C9.COMP.04` | `bash-man` | bash(1) section SHELL COMPATIBILITY MODE + RESTRICTED SHELL | `covered / covered` | `run_startup_mode_matrix.sh,man-bash-posix-08-declare-posix-policy.sh` | shopt compat31..compat44 switches |

Notes:

- `C11.MODE.02`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C5.BUILTIN.SHOPT`: Seeded from tests/compat/bash_posix_man_coverage.tsv
- `C9.COMP.04`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.

### `builtin:source`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.039` | `bash-posix-doc` | bash/POSIX 6.11.2 item 39 | `covered / covered` | `bash-posix-doc-039.sh` | Non-interactive shells exit if there is a syntax error in a script read with the ‘.’ or ‘source’ builtins, or in a string processed by the ‘eval’ builtin. |
| `BPOSIX.CORE.046` | `bash-posix-doc` | bash/POSIX 6.11.2 item 46 | `covered / covered` | `bash-posix-doc-046.sh` | The ‘.’ and ‘source’ builtins do not search the current directory for the filename argument if it is not found by searching ‘PATH’. |
| `C5.BUILTIN.SOURCE` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-05-dot-source` | source |

Notes:

- `BPOSIX.CORE.039`: Strict semantic parity case: eval syntax error is fatal in non-interactive shell.
- `BPOSIX.CORE.046`: Strict comparator case validates dot/source PATH-only lookup when operand lacks slash.
- `C5.BUILTIN.SOURCE`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:suspend`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.SUSPEND` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-12-history-suspend-logout` | suspend |
| `C8.JOB.20` | `bash-man` | bash(1) section JOB CONTROL | `covered / covered` | `run_jobs_interactive_matrix.sh,run_job_suspend_ctrl_matrix.sh` | interactive suspend char ^Z stops foreground job and returns prompt |

Notes:

- `C5.BUILTIN.SUSPEND`: Seeded from tests/compat/bash_posix_man_coverage.tsv
- `C8.JOB.20`: Covered in comparator scope via strict signal-equivalent foreground stop lane plus informational literal `^Z` PTY lane for control-characte…

### `builtin:test`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BCOMPAT.52.001` | `bash-compat-doc` | bash/COMPAT level 52 item 1 | `partial / partial` | `bash-compat-doc-52-001.sh` | the test builtin uses its historical algorithm for parsing expressions composed of five or more primaries. |
| `BPOSIX.CORE.065` | `bash-posix-doc` | bash/POSIX 6.11.2 item 65 | `covered / covered` | `bash-posix-doc-065.sh` | The ‘test’ builtin compares strings using the current locale when evaluating the ‘<’ and ‘>’ binary operators. |
| `BPOSIX.CORE.066` | `bash-posix-doc` | bash/POSIX 6.11.2 item 66 | `covered / covered` | `bash-posix-doc-066.sh` | The ‘test’ builtin's ‘-t’ unary primary requires an argument. Historical versions of ‘test’ made the argument optional in certain cases, and Bash attempts to accommodate those for backwards compatibility. |
| `C5.BUILTIN.TEST` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-03-io-signals` | test |

Notes:

- `BCOMPAT.52.001`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat52 (set using BASH_COMPAT) i…
- `BPOSIX.CORE.065`: Strict comparator case validates POSIX row 65 behavior in current runtime lane.
- `BPOSIX.CORE.066`: Strict comparator case validates POSIX row 66 behavior in current runtime lane.
- `C5.BUILTIN.TEST`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:times`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.TIMES` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-04-misc-builtins` | times |

Notes:

- `C5.BUILTIN.TIMES`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:trap`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.067` | `bash-posix-doc` | bash/POSIX 6.11.2 item 67 | `covered / covered` | `bash-posix-doc-067.sh` | The ‘trap’ builtin displays signal names without the leading ‘SIG’. |
| `BPOSIX.CORE.068` | `bash-posix-doc` | bash/POSIX 6.11.2 item 68 | `covered / covered` | `bash-posix-doc-068.sh` | The ‘trap’ builtin doesn't check the first argument for a possible signal specification and revert the signal handling to the original disposition if it is, unless that argument consists solely of digits and is a valid signal number. If users want to reset the handler for a given signal to the original disposition, they should use ‘-’ as the first argument. |
| `C5.BUILTIN.TRAP` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-03-io-signals` | trap |
| `C8.JOB.26` | `bash-man` | bash(1) section JOB CONTROL | `covered / covered` | `bash-man-jobcontrol-sigchld-per-child.sh` | `trap SIGCHLD` runs per exiting child |

Notes:

- `BPOSIX.CORE.067`: Strict comparator case validates POSIX row 67 behavior in current runtime lane.
- `BPOSIX.CORE.068`: Strict comparator case validates POSIX row 68 behavior in current runtime lane.
- `C5.BUILTIN.TRAP`: Seeded from tests/compat/bash_posix_man_coverage.tsv
- `C8.JOB.26`: Dedicated comparator case covers CHLD trap delivery across two async children with sequential waits and bash-matching wait status/marker or…

### `builtin:true`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.TRUE` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-04-misc-builtins` | true |

Notes:

- `C5.BUILTIN.TRUE`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:type`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.018` | `bash-posix-doc` | bash/POSIX 6.11.2 item 18 | `covered / covered` | `bash-posix-doc-018.sh` | Command lookup finds POSIX special builtins before shell functions, including output printed by the ‘type’ and ‘command’ builtins. |
| `BPOSIX.CORE.031` | `bash-posix-doc` | bash/POSIX 6.11.2 item 31 | `covered / covered` | `bash-posix-doc-031.sh` | When printing shell function definitions (e.g., by ‘type’), Bash does not print the ‘function’ reserved word unless necessary. |
| `BPOSIX.CORE.070` | `bash-posix-doc` | bash/POSIX 6.11.2 item 70 | `covered / covered` | `bash-posix-doc-070.sh` | The ‘type’ and ‘command’ builtins will not report a non-executable file as having been found, though the shell will attempt to execute such a file if it is the only so-named file found in ‘$PATH’. |
| `C5.BUILTIN.TYPE` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-02-path-command` | type |

Notes:

- `BPOSIX.CORE.018`: Strict comparator probe validates special-builtin precedence against function shadowing and reporting surfaces for `type`/`command`; Source…
- `BPOSIX.CORE.031`: Strict comparator case validates POSIX `type` function formatting behavior.
- `BPOSIX.CORE.070`: Strict comparator probe validates command/type non-exec reporting policy with execute-attempt fallback remaining permission-denied class; S…
- `C5.BUILTIN.TYPE`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:typeset`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.TYPESET` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `bash-builtin-declare-typeset-local` | typeset |

Notes:

- `C5.BUILTIN.TYPESET`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:ulimit`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.071` | `bash-posix-doc` | bash/POSIX 6.11.2 item 71 | `covered / covered` | `bash-posix-doc-071.sh` | The ‘ulimit’ builtin uses a block size of 512 bytes for the ‘-c’ and ‘-f’ options. |
| `C5.BUILTIN.ULIMIT` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-04-misc-builtins` | ulimit |

Notes:

- `BPOSIX.CORE.071`: Strict comparator case validates POSIX row 71 behavior in current runtime lane.
- `C5.BUILTIN.ULIMIT`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:umask`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.UMASK` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-04-misc-builtins` | umask |

Notes:

- `C5.BUILTIN.UMASK`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:unalias`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C5.BUILTIN.UNALIAS` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-04-misc-builtins` | unalias |

Notes:

- `C5.BUILTIN.UNALIAS`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:unset`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BCOMPAT.51.001` | `bash-compat-doc` | bash/COMPAT level 51 item 1 | `partial / partial` | `bash-compat-doc-51-001.sh` | The `unset' builtin will unset the array a given an argument like `a[@]'. Bash-5.2 will unset an element with key `@' (associative arrays) or remove all the elements without unsetting the array (indexed arrays) |
| `BPOSIX.CORE.072` | `bash-posix-doc` | bash/POSIX 6.11.2 item 72 | `covered / covered` | `bash-posix-doc-072.sh` | The ‘unset’ builtin with the ‘-v’ option specified returns a fatal error if it attempts to unset a ‘readonly’ or ‘non-unsettable’ variable, which causes a non-interactive shell to exit. |
| `BPOSIX.CORE.073` | `bash-posix-doc` | bash/POSIX 6.11.2 item 73 | `covered / covered` | `bash-posix-doc-073.sh` | When asked to unset a variable that appears in an assignment statement preceding the command, the ‘unset’ builtin attempts to unset a variable of the same name in the current or previous scope as well. This implements the required "if an assigned variable is further modified by the utility, the modifications made by the utility shall persist" behavior. |
| `C5.BUILTIN.UNSET` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-01-core-state` | unset |

Notes:

- `BCOMPAT.51.001`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat51 (set using BASH_COMPAT) i…
- `BPOSIX.CORE.072`: Strict semantic parity case tracks bash comparator behavior for unset -v readonly (non-fatal with nonzero status).
- `BPOSIX.CORE.073`: Strict semantic parity case: unset effect with assignment prefix persists per comparator behavior.
- `C5.BUILTIN.UNSET`: Seeded from tests/compat/bash_posix_man_coverage.tsv

### `builtin:wait`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.026` | `bash-posix-doc` | bash/POSIX 6.11.2 item 26 | `covered / covered` | `bash-posix-doc-026.sh` | Bash permanently removes jobs from the jobs table after notifying the user of their termination via the ‘wait’ or ‘jobs’ builtins. It removes the job from the jobs list after notifying the user of its termination, but the status is still available via ‘wait’, as long as ‘wait’ is supplied a PID argument. |
| `BPOSIX.CORE.074` | `bash-posix-doc` | bash/POSIX 6.11.2 item 74 | `covered / covered` | `bash-posix-doc-074.sh` | The arrival of ‘SIGCHLD’ when a trap is set on ‘SIGCHLD’ does not interrupt the ‘wait’ builtin and cause it to return immediately. The trap command is run once for each child that exits. |
| `BPOSIX.CORE.075` | `bash-posix-doc` | bash/POSIX 6.11.2 item 75 | `covered / covered` | `bash-posix-doc-075.sh` | Bash removes an exited background process's status from the list of such statuses after the ‘wait’ builtin returns it. |
| `C5.BUILTIN.WAIT` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS | `covered / covered` | `man-bash-posix-03-io-signals` | wait |
| `C8.JOB.05` | `bash-man` | bash(1) section SIGNALS + JOB CONTROL + builtins | `covered / covered` | `man-ash-kill-wait.sh` | wait builtin with pid/jobspec and status propagation |
| `C8.JOB.28` | `bash-man` | bash(1) section JOB CONTROL | `covered / covered` | `run_jobs_interactive_matrix.sh` | with job control enabled, `wait` returns on job state change |
| `C8.JOB.29` | `bash-man` | bash(1) section JOB CONTROL | `covered / covered` | `run_jobs_interactive_matrix.sh` | `wait -f` waits for termination (not merely state change) |

Notes:

- `BPOSIX.CORE.026`: Strict comparator case validates `wait` status-retention semantics after notification.
- `BPOSIX.CORE.074`: Strict comparator case validates POSIX row 74 behavior in current runtime lane.
- `BPOSIX.CORE.075`: Strict comparator case validates POSIX row 75 behavior in current runtime lane.
- `C5.BUILTIN.WAIT`: Seeded from tests/compat/bash_posix_man_coverage.tsv
- `C8.JOB.05`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C8.JOB.28`: Interactive strict matrix `wait-state-change` lane asserts `wait %1` returns stop-status (`147`) after `SIGSTOP` transition before terminat…
- `C8.JOB.29`: Interactive strict matrix `wait-f-termination` lane asserts `wait -f %1` ignores stop/continue transitions and returns termination status (…

### `runtime:history`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C1.OPT.SETO.HISTEXPAND` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | histexpand |
| `C11.SHOPT.CMDHIST` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | cmdhist |
| `C11.SHOPT.HISTAPPEND` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | histappend |
| `C11.SHOPT.HISTREEDIT` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | histreedit |
| `C11.SHOPT.HISTVERIFY` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | histverify |
| `C11.SHOPT.LITHIST` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | lithist |

Notes:

- `C1.OPT.SETO.HISTEXPAND`: Mapped by bash-man-seto-surface.sh; comparator evidence run passes in default and --posix lanes.
- `C11.SHOPT.CMDHIST`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C11.SHOPT.HISTAPPEND`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C11.SHOPT.HISTREEDIT`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C11.SHOPT.HISTVERIFY`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C11.SHOPT.LITHIST`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.

### `runtime:job-control`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.022` | `bash-posix-doc` | bash/POSIX 6.11.2 item 22 | `covered / covered` | `bash-posix-doc-022.sh` | The message printed by the job control code and builtins when a job exits with a non-zero status is 'Done(status)'. |
| `BPOSIX.CORE.023` | `bash-posix-doc` | bash/POSIX 6.11.2 item 23 | `covered / covered` | `bash-posix-doc-023.sh` | The message printed by the job control code and builtins when a job is stopped is 'Stopped(SIGNAME)', where SIGNAME is, for example, ‘SIGTSTP’. |
| `BPOSIX.CORE.024` | `bash-posix-doc` | bash/POSIX 6.11.2 item 24 | `covered / covered` | `bash-posix-doc-024.sh` | If the shell is interactive, Bash does not perform job notifications between executing commands in lists separated by ‘;’ or newline. Non-interactive shells print status messages after a foreground job in a list completes. |
| `BPOSIX.CORE.025` | `bash-posix-doc` | bash/POSIX 6.11.2 item 25 | `covered / covered` | `bash-posix-doc-025.sh` | If the shell is interactive, Bash waits until the next prompt before printing the status of a background job that changes status or a foreground job that terminates due to a signal. Non-interactive shells print status messages after a foreground job completes. |
| `C8.JOB.01` | `bash-man` | bash(1) section SIGNALS + JOB CONTROL + builtins | `covered / covered` | `man-bash-posix-13-exec-errors-signals-jobs.sh` | job table maintenance for async commands |
| `C8.JOB.14` | `bash-man` | bash(1) section JOB CONTROL | `covered / covered` | `man-bash-posix-10-jobs-fg-bg-interactive.sh,run_jobs_interactive_matrix.sh` | each pipeline is tracked as one job entry |
| `C8.JOB.16` | `bash-man` | bash(1) section JOB CONTROL | `covered / covered` | `run_jobs_interactive_matrix.sh` | all processes in one pipeline share a process group/job |
| `C8.JOB.22` | `bash-man` | bash(1) section JOB CONTROL | `covered / covered` | `bash-man-jobcontrol-jobspec-core.sh` | jobspec forms resolve correctly: `%n`, `%%`/`%+`, `%-`, bare `%` |
| `C8.JOB.23` | `bash-man` | bash(1) section JOB CONTROL | `covered / covered` | `bash-man-jobcontrol-jobspec-match.sh` | jobspec name matching supports prefix `%name` and substring `%?text` with ambiguity errors |

Notes:

- `BPOSIX.CORE.022`: Strict comparator case validates Done(status) state reporting for non-zero completed jobs under monitor mode. Note: this row currently uses…
- `BPOSIX.CORE.023`: Strict comparator case validates stopped-job state reporting in jobs output under monitor mode. Note: this row currently uses normalized in…
- `BPOSIX.CORE.024`: Comparator case validates interactive notification timing scaffold behavior for row 24.
- `BPOSIX.CORE.025`: Comparator case validates interactive notification prompt-boundary behavior for row 25.
- `C8.JOB.01`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C8.JOB.14`: Dedicated strict comparator lane (`pipeline-job-table`) asserts multi-pipeline job-table cardinality and jobspec wait routing.; design:docs…
- `C8.JOB.16`: Interactive pipeline case asserts one background pipeline maps to one job entry and jobspec wait target within current runtime model scope.…
- `C8.JOB.22`: Dedicated jobspec core case is parity-covered via wait/jobspec resolution in bash --posix and mctash --posix lanes.; design:docs/design/job…
- (Plus 1 additional row notes; see `docs/specs/feature-index.tsv`.)

### `runtime:prompt`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C11.SHOPT.PROMPTVARS` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | promptvars |
| `C7.INT.01` | `bash-man` | bash(1) section PROMPTING + READLINE + HISTORY | `covered / covered` | `run_interactive_ux_matrix.sh` | prompt escapes in PS1/PS2/PS4 (\u, \h, \w, \!, etc.) |
| `C7.INT.02` | `bash-man` | bash(1) section PROMPTING + READLINE + HISTORY | `covered / covered` | `run_interactive_ux_matrix.sh` | PROMPT_COMMAND execution before primary prompt |

Notes:

- `C11.SHOPT.PROMPTVARS`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C7.INT.01`: PS1/PS2/PS4 escape lanes are covered with strict PTY assertions in the interactive UX matrix.
- `C7.INT.02`: Strict PTY interactive comparator evidence passes via run_interactive_ux_matrix.sh and run_completion_interactive_matrix.sh.

### `runtime:signals-traps`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.041` | `bash-posix-doc` | bash/POSIX 6.11.2 item 41 | `covered / covered` | `bash-posix-doc-041.sh` | Assignment statements preceding POSIX special builtins persist in the shell environment after the builtin completes. |
| `C8.JOB.08` | `bash-man` | bash(1) section SIGNALS + JOB CONTROL + builtins | `covered / covered` | `man-ash-trap-signal-matrix.sh,man-ash-trap-delivery.sh` | SIGINT/SIGQUIT/SIGTERM handling semantics |
| `C8.JOB.17` | `bash-man` | bash(1) section JOB CONTROL | `covered / covered` | `run_interactive_sigint_matrix.sh,bash-man-jobcontrol-foreground-signals.sh` | foreground process group receives keyboard-generated SIGINT |
| `C8.JOB.19` | `bash-man` | bash(1) section JOB CONTROL | `covered / covered` | `run_job_tty_stop_matrix.sh` | background process write with `stty tostop` gets SIGTTOU stop |

Notes:

- `BPOSIX.CORE.041`: Strict comparator case validates command lookup and assignment interactions in POSIX lane.
- `C8.JOB.08`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C8.JOB.17`: Comparator scope is closed with signal-routing groundwork plus informational PTY keyboard lane; strict control-character determinism remain…
- `C8.JOB.19`: Interactive PTY comparator `sigttou` lane verifies background tty-write job transitions to `Stopped(SIGTTOU)` when `stty tostop` is enabled…

### `runtime:startup`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.002` | `bash-posix-doc` | bash/POSIX 6.11.2 item 2 | `covered / covered` | `bash-posix-doc-002.sh` | Bash reads and executes the POSIX startup files (‘$ENV’) rather than the normal Bash files (*note Bash Startup Files::. |
| `C1.STARTUP.01` | `bash-man` | bash(1) section INVOCATION | `covered / covered` | `run_startup_mode_matrix.sh` | login-shell startup sequence |
| `C1.STARTUP.02` | `bash-man` | bash(1) section INVOCATION | `covered / covered` | `run_startup_mode_matrix.sh` | interactive non-login startup |
| `C1.STARTUP.03` | `bash-man` | bash(1) section INVOCATION | `covered / covered` | `run_startup_mode_matrix.sh` | non-interactive startup |
| `C1.STARTUP.04` | `bash-man` | bash(1) section INVOCATION | `covered / covered` | `run_startup_mode_matrix.sh` | invoked-as-sh startup |
| `C10.STATE.05` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh,man-bash-posix-14-env-exec-flow.sh,bash-builtin-declare-typeset-local.sh` | startup-time variable influences (POSIXLY_CORRECT, BASH_ENV, ENV) |
| `C9.COMP.02` | `bash-man` | bash(1) section SHELL COMPATIBILITY MODE + RESTRICTED SHELL | `covered / covered` | `run_startup_mode_matrix.sh,man-bash-posix-08-declare-posix-policy.sh` | rbash invocation behavior |

Notes:

- `BPOSIX.CORE.002`: Row-level comparator evidence now passes for POSIX interactive ENV startup loading in focused lane; Source: bash/POSIX 6.11.2 item 2.
- `C1.STARTUP.01`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C1.STARTUP.02`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C1.STARTUP.03`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C1.STARTUP.04`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C10.STATE.05`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C9.COMP.02`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.

### `subcategory:compat-delta`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BCOMPAT.41.001` | `bash-compat-doc` | bash/COMPAT level 41 item 1 | `partial / partial` | `bash-compat-doc-41-001.sh` | in posix mode, `time' may be followed by options and still be recognized as a reserved word (this is POSIX interpretation 267) |
| `BCOMPAT.44.001` | `bash-compat-doc` | bash/COMPAT level 44 item 1 | `partial / partial` | `bash-compat-doc-44-001.sh` | the shell sets up the values used by BASH_ARGV and BASH_ARGC so they can expand to the shell's positional parameters even if extended debug mode is not enabled |
| `BCOMPAT.51.005` | `bash-compat-doc` | bash/COMPAT level 51 item 5 | `partial / partial` | `bash-compat-doc-51-005.sh` | the expressions in substring parameter brace expansion can be expanded more than once |

Notes:

- `BCOMPAT.41.001`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat41 item 1; compatibility del…
- `BCOMPAT.44.001`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat44 item 1; compatibility del…
- `BCOMPAT.51.005`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat51 (set using BASH_COMPAT) i…

### `subcategory:compatibility`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C9.COMP.03` | `bash-man` | bash(1) section SHELL COMPATIBILITY MODE + RESTRICTED SHELL | `covered / covered` | `run_startup_mode_matrix.sh,man-bash-posix-08-declare-posix-policy.sh` | BASH_COMPAT compatibility levels |
| `C9.COMP.05` | `bash-man` | bash(1) section SHELL COMPATIBILITY MODE + RESTRICTED SHELL | `covered / covered` | `run_startup_mode_matrix.sh,man-bash-posix-08-declare-posix-policy.sh` | invoked-as-sh behavior changes |
| `C9.COMP.06` | `bash-man` | bash(1) section SHELL COMPATIBILITY MODE + RESTRICTED SHELL | `covered / covered` | `run_startup_mode_matrix.sh,man-bash-posix-08-declare-posix-policy.sh` | posix mode deviations from default bash |
| `C9.COMP.07` | `bash-man` | bash(1) section SHELL COMPATIBILITY MODE + RESTRICTED SHELL | `covered / covered` | `run_startup_mode_matrix.sh,man-bash-posix-08-declare-posix-policy.sh` | compatibility and mode diagnostics surfaces |

Notes:

- `C9.COMP.03`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C9.COMP.05`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C9.COMP.06`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C9.COMP.07`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.

### `subcategory:expansion`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C3.EXP.001` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `bash-man-expansion-brace-locale.sh` | brace expansion {a,b} |
| `C3.EXP.002` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `bash-man-expansion-core.sh` | tilde expansion ~ and ~user |
| `C3.EXP.004` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh` | special parameters $* $@ $# $? $- $$ $! $0 |
| `C3.EXP.022` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `bash-man-expansion-core.sh` | backtick substitution `cmd` |
| `C3.EXP.024` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `bash-man-expansion-process-subst.sh` | process substitution <(cmd) >(cmd) |
| `C3.EXP.025` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `man-ash-glob-full-matrix.sh` | word splitting using IFS |
| `C3.EXP.026` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh` | pathname expansion (globbing) |
| `C3.EXP.031` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `bash-man-expansion-core.sh` | expansion order as documented in EXPANSION |

Notes:

- `C3.EXP.001`: brace expansion implemented for structured fields; mapped evidence run passes.
- `C3.EXP.002`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C3.EXP.004`: Expansion rows validated by man-ash-var-ops-matrix.sh, bash-compat-param-array-hash-extended.sh, and bash-man-expansion-process-subst.sh; c…
- `C3.EXP.022`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C3.EXP.024`: Expansion rows validated by man-ash-var-ops-matrix.sh, bash-compat-param-array-hash-extended.sh, and bash-man-expansion-process-subst.sh; c…
- `C3.EXP.025`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C3.EXP.026`: Expansion rows validated by man-ash-var-ops-matrix.sh, bash-compat-param-array-hash-extended.sh, and bash-man-expansion-process-subst.sh; c…
- `C3.EXP.031`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.

### `subcategory:expansion-redir`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.013` | `bash-posix-doc` | bash/POSIX 6.11.2 item 13 | `covered / covered` | `bash-posix-doc-013.sh` | While variable indirection is available, it may not be applied to the ‘#’ and ‘?’ special parameters. |
| `BPOSIX.CORE.017` | `bash-posix-doc` | bash/POSIX 6.11.2 item 17 | `covered / covered` | `bash-posix-doc-017.sh` | Literal tildes that appear as the first character in elements of the ‘PATH’ variable are not expanded as described above under *note Tilde Expansion::. |
| `BPOSIX.EXTRA.001` | `bash-posix-doc` | bash/POSIX 6.11.2 item 1 | `covered / covered` | `bash-posix-doc-extra-001.sh` | POSIX requires that word splitting be byte-oriented. That is, each _byte_ in the value of ‘IFS’ potentially splits a word, even if that byte is part of a multibyte character in ‘IFS’ or part of multibyte character in the word. Bash allows multibyte characters in the value of ‘IFS’, treating a valid multibyte character as a single delimiter, and will not split a valid multibyte character even if one of the bytes composing that character appears in ‘IFS’. This is POSIX interpretation 1560, further modified by issue 1924. |

Notes:

- `BPOSIX.CORE.013`: Comparator parity: alias expansion timing in command substitutions aligns in POSIX lane.
- `BPOSIX.CORE.017`: Comparator parity: command substitution parsing and quoting behavior aligns in POSIX lane.
- `BPOSIX.EXTRA.001`: Policy decision: follow bash multibyte-aware IFS splitting behavior (not strict byte-wise POSIX interpretation) across modes; covered by ba…

### `subcategory:grammar.core`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C2.GRAM.002` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | pipeline |
| `C2.GRAM.003` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | list with ; |
| `C2.GRAM.004` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | list with & |
| `C2.GRAM.005` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | AND list (&&) |
| `C2.GRAM.006` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | OR list (||) |
| `C2.GRAM.007` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | negated pipeline (! pipeline) |
| `C2.GRAM.010` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | if ... then ... fi |
| `C2.GRAM.011` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | if ... then ... else ... fi |
| `C2.GRAM.012` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | if ... then ... elif ... fi |
| `C2.GRAM.013` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | while ... do ... done |
| `C2.GRAM.014` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | until ... do ... done |
| `C2.GRAM.015` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | for name in words; do ... done |
| `C2.GRAM.016` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | for name; do ... done |
| `C2.GRAM.018` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | case WORD in ... esac |
| `C2.GRAM.019` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-select-coproc.sh` | select NAME in ...; do ... done |
| `C2.GRAM.020` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | function definition name() compound |
| `C2.GRAM.021` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh,man-ash-grammar-word-matrix.sh` | function keyword form function name [()] compound |
| `C2.GRAM.025` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | time reserved word and -p form |
| `C2.GRAM.027` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | comments in interactive/non-interactive modes |

Notes:

- `C2.GRAM.002`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C2.GRAM.003`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C2.GRAM.004`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C2.GRAM.005`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C2.GRAM.006`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C2.GRAM.007`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C2.GRAM.010`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C2.GRAM.011`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- (Plus 11 additional row notes; see `docs/specs/feature-index.tsv`.)

### `subcategory:interactive`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.045` | `bash-posix-doc` | bash/POSIX 6.11.2 item 45 | `covered / covered` | `bash-posix-doc-045.sh` | Enabling POSIX mode has the effect of setting the ‘interactive_comments’ option (*note Comments::). |
| `C7.INT.03` | `bash-man` | bash(1) section PROMPTING + READLINE + HISTORY | `covered / covered` | `run_interactive_ux_matrix.sh` | readline editing modes emacs/vi |
| `C7.INT.09` | `bash-man` | bash(1) section PROMPTING + READLINE + HISTORY | `covered / covered` | `run_completion_interactive_matrix.sh,bash-builtin-completion.sh` | completion variables COMP_* and COMPREPLY |
| `C7.INT.10` | `bash-man` | bash(1) section PROMPTING + READLINE + HISTORY | `covered / covered` | `run_interactive_ux_matrix.sh` | interactive comments behavior (interactive_comments) |

Notes:

- `BPOSIX.CORE.045`: Strict comparator case validates POSIX builtin execution/exit-status semantics.
- `C7.INT.03`: Strict PTY interactive comparator evidence passes via run_interactive_ux_matrix.sh and run_completion_interactive_matrix.sh.
- `C7.INT.09`: Strict PTY interactive comparator evidence passes via run_interactive_ux_matrix.sh and run_completion_interactive_matrix.sh.
- `C7.INT.10`: Strict PTY interactive comparator evidence passes via run_interactive_ux_matrix.sh and run_completion_interactive_matrix.sh.

### `subcategory:invocation.long-option`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C1.OPT.LONG.DEBUGGER` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | --debugger |
| `C1.OPT.LONG.DUMP_PO_STRINGS` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | --dump-po-strings |
| `C1.OPT.LONG.DUMP_STRINGS` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | --dump-strings |
| `C1.OPT.LONG.INIT_FILE_FILE` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | --init-file FILE |
| `C1.OPT.LONG.LOGIN` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | --login |
| `C1.OPT.LONG.NOEDITING` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | --noediting |
| `C1.OPT.LONG.NOPROFILE` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | --noprofile |
| `C1.OPT.LONG.NORC` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | --norc |
| `C1.OPT.LONG.POSIX` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | --posix |
| `C1.OPT.LONG.RCFILE_FILE` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | --rcfile FILE |
| `C1.OPT.LONG.RESTRICTED` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | --restricted |
| `C1.OPT.LONG.VERBOSE` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | --verbose |
| `C1.OPT.LONG.VERSION` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | --version |

Notes:

- `C1.OPT.LONG.DEBUGGER`: Mapped by run_bash_invocation_option_matrix.sh (and startup mode matrix where applicable); comparator evidence run passes in default and --…
- `C1.OPT.LONG.DUMP_PO_STRINGS`: --dump-po-strings currently rejected as illegal option. Validated by passing run_bash_invocation_option_matrix.sh.
- `C1.OPT.LONG.DUMP_STRINGS`: --dump-strings currently rejected as illegal option. Validated by passing run_bash_invocation_option_matrix.sh.
- `C1.OPT.LONG.INIT_FILE_FILE`: Mapped by run_bash_invocation_option_matrix.sh (and startup mode matrix where applicable); comparator evidence run passes in default and --…
- `C1.OPT.LONG.LOGIN`: Mapped by run_bash_invocation_option_matrix.sh (and startup mode matrix where applicable); comparator evidence run passes in default and --…
- `C1.OPT.LONG.NOEDITING`: Mapped by run_bash_invocation_option_matrix.sh (and startup mode matrix where applicable); comparator evidence run passes in default and --…
- `C1.OPT.LONG.NOPROFILE`: Mapped by run_bash_invocation_option_matrix.sh (and startup mode matrix where applicable); comparator evidence run passes in default and --…
- `C1.OPT.LONG.NORC`: Mapped by run_bash_invocation_option_matrix.sh (and startup mode matrix where applicable); comparator evidence run passes in default and --…
- (Plus 5 additional row notes; see `docs/specs/feature-index.tsv`.)

### `subcategory:invocation.set-o-option`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C1.OPT.SETO.ALLEXPORT` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | allexport |
| `C1.OPT.SETO.BRACEEXPAND` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | braceexpand |
| `C1.OPT.SETO.EMACS` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | emacs |
| `C1.OPT.SETO.ERREXIT` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | errexit |
| `C1.OPT.SETO.ERRTRACE` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | errtrace |
| `C1.OPT.SETO.FUNCTRACE` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | functrace |
| `C1.OPT.SETO.HASHALL` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | hashall |
| `C1.OPT.SETO.IGNOREEOF` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | ignoreeof |
| `C1.OPT.SETO.INTERACTIVE_COMMENTS` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | interactive-comments |
| `C1.OPT.SETO.KEYWORD` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | keyword |
| `C1.OPT.SETO.MONITOR` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | monitor |
| `C1.OPT.SETO.NOCLOBBER` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | noclobber |
| `C1.OPT.SETO.NOEXEC` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | noexec |
| `C1.OPT.SETO.NOGLOB` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | noglob |
| `C1.OPT.SETO.NOLOG` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | nolog |
| `C1.OPT.SETO.NOTIFY` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | notify |
| `C1.OPT.SETO.NOUNSET` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | nounset |
| `C1.OPT.SETO.ONECMD` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | onecmd |
| `C1.OPT.SETO.PHYSICAL` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | physical |
| `C1.OPT.SETO.PIPEFAIL` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | pipefail |
| `C1.OPT.SETO.POSIX` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | posix |
| `C1.OPT.SETO.PRIVILEGED` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | privileged |
| `C1.OPT.SETO.VERBOSE` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | verbose |
| `C1.OPT.SETO.VI` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | vi |
| `C1.OPT.SETO.XTRACE` | `bash-man` | bash(1) section set builtin | `covered / covered` | `bash-man-seto-surface.sh` | xtrace |

Notes:

- `C1.OPT.SETO.ALLEXPORT`: Mapped by bash-man-seto-surface.sh; comparator evidence run passes in default and --posix lanes.
- `C1.OPT.SETO.BRACEEXPAND`: Mapped by bash-man-seto-surface.sh; comparator evidence run passes in default and --posix lanes.
- `C1.OPT.SETO.EMACS`: Mapped by bash-man-seto-surface.sh; comparator evidence run passes in default and --posix lanes.
- `C1.OPT.SETO.ERREXIT`: Mapped by bash-man-seto-surface.sh; comparator evidence run passes in default and --posix lanes.
- `C1.OPT.SETO.ERRTRACE`: Mapped by bash-man-seto-surface.sh; comparator evidence run passes in default and --posix lanes.
- `C1.OPT.SETO.FUNCTRACE`: Mapped by bash-man-seto-surface.sh; comparator evidence run passes in default and --posix lanes.
- `C1.OPT.SETO.HASHALL`: Mapped by bash-man-seto-surface.sh; comparator evidence run passes in default and --posix lanes.
- `C1.OPT.SETO.IGNOREEOF`: Mapped by bash-man-seto-surface.sh; comparator evidence run passes in default and --posix lanes.
- (Plus 17 additional row notes; see `docs/specs/feature-index.tsv`.)

### `subcategory:invocation.set-short-option`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C1.OPT.SET.B` | `bash-man` | bash(1) section OPTIONS + set builtin | `covered / covered` | `bash-man-seto-surface.sh` | -B |
| `C1.OPT.SET.C` | `bash-man` | bash(1) section OPTIONS + set builtin | `covered / covered` | `bash-man-seto-surface.sh` | -C |
| `C1.OPT.SET.E` | `bash-man` | bash(1) section OPTIONS + set builtin | `covered / covered` | `bash-man-seto-surface.sh` | -E |
| `C1.OPT.SET.H` | `bash-man` | bash(1) section OPTIONS + set builtin | `covered / covered` | `bash-man-seto-surface.sh` | -H |
| `C1.OPT.SET.P` | `bash-man` | bash(1) section OPTIONS + set builtin | `covered / covered` | `bash-man-seto-surface.sh` | -P |
| `C1.OPT.SET.T` | `bash-man` | bash(1) section OPTIONS + set builtin | `covered / covered` | `bash-man-seto-surface.sh` | -T |
| `C1.OPT.SET.a` | `bash-man` | bash(1) section OPTIONS + set builtin | `covered / covered` | `bash-man-seto-surface.sh` | -a |
| `C1.OPT.SET.b` | `bash-man` | bash(1) section OPTIONS + set builtin | `covered / covered` | `bash-man-seto-surface.sh` | -b |
| `C1.OPT.SET.e` | `bash-man` | bash(1) section OPTIONS + set builtin | `covered / covered` | `bash-man-seto-surface.sh` | -e |
| `C1.OPT.SET.f` | `bash-man` | bash(1) section OPTIONS + set builtin | `covered / covered` | `bash-man-seto-surface.sh` | -f |
| `C1.OPT.SET.h` | `bash-man` | bash(1) section OPTIONS + set builtin | `covered / covered` | `bash-man-seto-surface.sh` | -h |
| `C1.OPT.SET.k` | `bash-man` | bash(1) section OPTIONS + set builtin | `covered / covered` | `bash-man-seto-surface.sh` | -k |
| `C1.OPT.SET.m` | `bash-man` | bash(1) section OPTIONS + set builtin | `covered / covered` | `bash-man-seto-surface.sh` | -m |
| `C1.OPT.SET.n` | `bash-man` | bash(1) section OPTIONS + set builtin | `covered / covered` | `bash-man-seto-surface.sh` | -n |
| `C1.OPT.SET.p` | `bash-man` | bash(1) section OPTIONS + set builtin | `covered / covered` | `bash-man-seto-surface.sh` | -p |
| `C1.OPT.SET.t` | `bash-man` | bash(1) section OPTIONS + set builtin | `covered / covered` | `bash-man-seto-surface.sh` | -t |
| `C1.OPT.SET.u` | `bash-man` | bash(1) section OPTIONS + set builtin | `covered / covered` | `bash-man-seto-surface.sh` | -u |
| `C1.OPT.SET.v` | `bash-man` | bash(1) section OPTIONS + set builtin | `covered / covered` | `bash-man-seto-surface.sh` | -v |
| `C1.OPT.SET.x` | `bash-man` | bash(1) section OPTIONS + set builtin | `covered / covered` | `bash-man-seto-surface.sh` | -x |

Notes:

- `C1.OPT.SET.B`: Mapped by bash-man-seto-surface.sh; comparator evidence run passes in default and --posix lanes.
- `C1.OPT.SET.C`: Mapped by bash-man-seto-surface.sh; comparator evidence run passes in default and --posix lanes.
- `C1.OPT.SET.E`: Mapped by bash-man-seto-surface.sh; comparator evidence run passes in default and --posix lanes.
- `C1.OPT.SET.H`: Mapped by bash-man-seto-surface.sh; comparator evidence run passes in default and --posix lanes.
- `C1.OPT.SET.P`: Mapped by bash-man-seto-surface.sh; comparator evidence run passes in default and --posix lanes.
- `C1.OPT.SET.T`: Mapped by bash-man-seto-surface.sh; comparator evidence run passes in default and --posix lanes.
- `C1.OPT.SET.a`: Mapped by bash-man-seto-surface.sh; comparator evidence run passes in default and --posix lanes.
- `C1.OPT.SET.b`: Mapped by bash-man-seto-surface.sh; comparator evidence run passes in default and --posix lanes.
- (Plus 11 additional row notes; see `docs/specs/feature-index.tsv`.)

### `subcategory:invocation.short-option`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C1.OPT.SHORT.D` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | -D |
| `C1.OPT.SHORT.DASHDASH` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh,run_startup_mode_matrix.sh` | -- |
| `C1.OPT.SHORT.O` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | -O [shopt_option] |
| `C1.OPT.SHORT.PLUSO` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | +O [shopt_option] |
| `C1.OPT.SHORT.SINGLEDASH` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh,run_startup_mode_matrix.sh` | - (as argument) |
| `C1.OPT.SHORT.c` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | -c |
| `C1.OPT.SHORT.i` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | -i |
| `C1.OPT.SHORT.l` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | -l |
| `C1.OPT.SHORT.r` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | -r |
| `C1.OPT.SHORT.s` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | -s |
| `C1.OPT.SHORT.v` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | -v |
| `C1.OPT.SHORT.x` | `bash-man` | bash(1) section OPTIONS | `covered / covered` | `run_bash_invocation_option_matrix.sh` | -x |

Notes:

- `C1.OPT.SHORT.D`: -D currently rejected as illegal option. Validated by passing run_bash_invocation_option_matrix.sh.
- `C1.OPT.SHORT.DASHDASH`: Mapped by run_bash_invocation_option_matrix.sh (and startup mode matrix where applicable); comparator evidence run passes in default and --…
- `C1.OPT.SHORT.O`: Invocation option handling validated by run_bash_invocation_option_matrix.sh; shopt semantics tracked separately in category 10.
- `C1.OPT.SHORT.PLUSO`: Invocation option handling validated by run_bash_invocation_option_matrix.sh; shopt semantics tracked separately in category 10.
- `C1.OPT.SHORT.SINGLEDASH`: Mapped by run_bash_invocation_option_matrix.sh (and startup mode matrix where applicable); comparator evidence run passes in default and --…
- `C1.OPT.SHORT.c`: Mapped by run_bash_invocation_option_matrix.sh (and startup mode matrix where applicable); comparator evidence run passes in default and --…
- `C1.OPT.SHORT.i`: Mapped by run_bash_invocation_option_matrix.sh (and startup mode matrix where applicable); comparator evidence run passes in default and --…
- `C1.OPT.SHORT.l`: Mapped by run_bash_invocation_option_matrix.sh (and startup mode matrix where applicable); comparator evidence run passes in default and --…
- (Plus 4 additional row notes; see `docs/specs/feature-index.tsv`.)

### `subcategory:invocation.startup-files`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C1.STARTUP.05` | `bash-man` | bash(1) section INVOCATION | `covered / covered` | `run_startup_mode_matrix.sh` | posix mode entry points |
| `C1.STARTUP.06` | `bash-man` | bash(1) section INVOCATION | `covered / covered` | `run_startup_mode_matrix.sh` | restricted mode entry points |

Notes:

- `C1.STARTUP.05`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C1.STARTUP.06`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.

### `subcategory:misc-posix-mode`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.019` | `bash-posix-doc` | bash/POSIX 6.11.2 item 19 | `covered / covered` | `bash-posix-doc-019.sh` | Even if a shell function whose name contains a slash was defined before entering POSIX mode, the shell will not execute a function whose name contains one or more slashes. |

Notes:

- `BPOSIX.CORE.019`: Comparator case now closes row 19 with POSIX eval/function-name behavior parity in non-interactive lane.

### `subcategory:mode-framework`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C11.MODE.03` | `bash-man` | bash(1) section OPTIONS + INVOCATION | `covered / covered` | `bash-man-seto-surface.sh,run_startup_mode_matrix.sh` | diagnostic style selection (bash/ash modes) |
| `C11.MODE.04` | `bash-man` | bash(1) section OPTIONS + INVOCATION | `covered / covered` | `bash-man-seto-surface.sh,run_startup_mode_matrix.sh` | mode selection by argv0 (sh/ash/dash vs bash/mctash) |
| `C11.MODE.05` | `bash-man` | bash(1) section OPTIONS + INVOCATION | `covered / covered` | `bash-man-seto-surface.sh,run_startup_mode_matrix.sh` | restricted-mode enforcement matrix |

Notes:

- `C11.MODE.03`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C11.MODE.04`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C11.MODE.05`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.

### `subcategory:parse-grammar`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.007` | `bash-posix-doc` | bash/POSIX 6.11.2 item 7 | `covered / covered` | `bash-posix-doc-007.sh` | The parser does not recognize ‘time’ as a reserved word if the next token begins with a ‘-’. |
| `BPOSIX.CORE.011` | `bash-posix-doc` | bash/POSIX 6.11.2 item 11 | `covered / covered` | `bash-posix-doc-011.sh` | Function names may not be the same as one of the POSIX special builtins. |

Notes:

- `BPOSIX.CORE.007`: Row-level comparator evidence now passes after POSIX dispatch model update for `time -...`; Source: bash/POSIX 6.11.2 item 7.
- `BPOSIX.CORE.011`: Comparator parity: getopts behavior aligns in POSIX lane with strict row-level case.

### `subcategory:redirection`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C4.REDIR.005` | `bash-man` | bash(1) section REDIRECTION | `covered / covered` | `man-ash-redir-heredoc-matrix.sh` | [n]>&word duplicate output fd |
| `C4.REDIR.006` | `bash-man` | bash(1) section REDIRECTION | `covered / covered` | `man-ash-redir-heredoc-matrix.sh` | [n]<&word duplicate input fd |
| `C4.REDIR.007` | `bash-man` | bash(1) section REDIRECTION | `covered / covered` | `man-ash-redir-heredoc-matrix.sh` | [n]>&- close output fd |
| `C4.REDIR.008` | `bash-man` | bash(1) section REDIRECTION | `covered / covered` | `man-ash-redir-heredoc-matrix.sh` | [n]<&- close input fd |
| `C4.REDIR.009` | `bash-man` | bash(1) section REDIRECTION | `covered / covered` | `man-ash-redir-heredoc-matrix.sh` | [n]>|word noclobber override |
| `C4.REDIR.013` | `bash-man` | bash(1) section REDIRECTION | `covered / covered` | `bash-man-redir-bash-ext.sh` | redirect stdout+stderr &>word |
| `C4.REDIR.014` | `bash-man` | bash(1) section REDIRECTION | `covered / covered` | `bash-man-redir-bash-ext.sh` | append stdout+stderr &>>word |
| `C4.REDIR.015` | `bash-man` | bash(1) section REDIRECTION | `covered / covered` | `man-ash-redir-heredoc-matrix.sh` | move fd [n]>&digit- and [n]<&digit- |
| `C4.REDIR.018` | `bash-man` | bash(1) section REDIRECTION | `covered / covered` | `man-ash-redir-heredoc-matrix.sh` | /dev/stdin /dev/stdout /dev/stderr handling |

Notes:

- `C4.REDIR.005`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C4.REDIR.006`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C4.REDIR.007`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C4.REDIR.008`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C4.REDIR.009`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C4.REDIR.013`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C4.REDIR.014`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C4.REDIR.015`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- (Plus 1 additional row notes; see `docs/specs/feature-index.tsv`.)

### `subcategory:requirements-matrix`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C12.MATRIX.01` | `bash-man` | bash(1) section project policy | `covered / covered` | `run_bash_posix_man_matrix.sh,run_bash_category_bucket_matrix.sh` | matrix column: bash default comparator |
| `C12.MATRIX.02` | `bash-man` | bash(1) section project policy | `covered / covered` | `run_bash_posix_man_matrix.sh,run_bash_category_bucket_matrix.sh` | matrix column: bash --posix comparator |
| `C12.MATRIX.03` | `bash-man` | bash(1) section project policy | `covered / covered` | `run_bash_posix_man_matrix.sh,run_bash_category_bucket_matrix.sh` | matrix column: mctash default mode |
| `C12.MATRIX.04` | `bash-man` | bash(1) section project policy | `covered / covered` | `run_bash_posix_man_matrix.sh,run_bash_category_bucket_matrix.sh` | matrix column: mctash --posix mode |
| `C12.MATRIX.05` | `bash-man` | bash(1) section project policy | `covered / covered` | `run_bash_posix_man_matrix.sh,run_bash_category_bucket_matrix.sh` | matrix row must map to at least one executable case id |
| `C12.MATRIX.06` | `bash-man` | bash(1) section project policy | `covered / covered` | `run_bash_posix_man_matrix.sh,run_bash_category_bucket_matrix.sh` | matrix row must record POSIX classification |
| `C12.MATRIX.07` | `bash-man` | bash(1) section project policy | `covered / covered` | `run_bash_posix_man_matrix.sh,run_bash_category_bucket_matrix.sh` | matrix row must avoid grouped shorthand and etc |

Notes:

- `C12.MATRIX.01`: Governance/meta requirement validated by matrix harness scripts and report generation.
- `C12.MATRIX.02`: Governance/meta requirement validated by matrix harness scripts and report generation.
- `C12.MATRIX.03`: Governance/meta requirement validated by matrix harness scripts and report generation.
- `C12.MATRIX.04`: Governance/meta requirement validated by matrix harness scripts and report generation.
- `C12.MATRIX.05`: Governance/meta requirement validated by matrix harness scripts and report generation.
- `C12.MATRIX.06`: Governance/meta requirement validated by matrix harness scripts and report generation.
- `C12.MATRIX.07`: Governance/meta requirement validated by matrix harness scripts and report generation.

### `subcategory:shopt-option-surface`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C11.SHOPT.ASSOC_EXPAND_ONCE` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | assoc_expand_once |
| `C11.SHOPT.AUTOCD` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | autocd |
| `C11.SHOPT.CDABLE_VARS` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | cdable_vars |
| `C11.SHOPT.CDSPELL` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | cdspell |
| `C11.SHOPT.CHECKHASH` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | checkhash |
| `C11.SHOPT.CHECKJOBS` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | checkjobs |
| `C11.SHOPT.CHECKWINSIZE` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | checkwinsize |
| `C11.SHOPT.COMPAT31` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | compat31 |
| `C11.SHOPT.COMPAT32` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | compat32 |
| `C11.SHOPT.COMPAT40` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | compat40 |
| `C11.SHOPT.COMPAT41` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | compat41 |
| `C11.SHOPT.COMPAT42` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | compat42 |
| `C11.SHOPT.COMPAT43` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | compat43 |
| `C11.SHOPT.COMPAT44` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | compat44 |
| `C11.SHOPT.DIREXPAND` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | direxpand |
| `C11.SHOPT.DIRSPELL` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | dirspell |
| `C11.SHOPT.DOTGLOB` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | dotglob |
| `C11.SHOPT.EXECFAIL` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | execfail |
| `C11.SHOPT.EXPAND_ALIASES` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | expand_aliases |
| `C11.SHOPT.EXTDEBUG` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | extdebug |
| `C11.SHOPT.EXTGLOB` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | extglob |
| `C11.SHOPT.FAILGLOB` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | failglob |
| `C11.SHOPT.FORCE_FIGNORE` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | force_fignore |
| `C11.SHOPT.GLOBASCIIRANGES` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | globasciiranges |
| `C11.SHOPT.GLOBSTAR` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | globstar |
| `C11.SHOPT.GNU_ERRFMT` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | gnu_errfmt |
| `C11.SHOPT.HOSTCOMPLETE` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | hostcomplete |
| `C11.SHOPT.HUPONEXIT` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | huponexit |
| `C11.SHOPT.INHERIT_ERREXIT` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | inherit_errexit |
| `C11.SHOPT.INTERACTIVE_COMMENTS` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | interactive_comments |
| `C11.SHOPT.LASTPIPE` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | lastpipe |
| `C11.SHOPT.LOCALVAR_INHERIT` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | localvar_inherit |
| `C11.SHOPT.LOCALVAR_UNSET` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | localvar_unset |
| `C11.SHOPT.LOGIN_SHELL` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | login_shell |
| `C11.SHOPT.MAILWARN` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | mailwarn |
| `C11.SHOPT.NOCASEGLOB` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | nocaseglob |
| `C11.SHOPT.NOCASEMATCH` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | nocasematch |
| `C11.SHOPT.NO_EMPTY_CMD_COMPLETION` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | no_empty_cmd_completion |
| `C11.SHOPT.NULLGLOB` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | nullglob |
| `C11.SHOPT.PROGCOMP` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | progcomp |
| `C11.SHOPT.PROGCOMP_ALIAS` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | progcomp_alias |
| `C11.SHOPT.RESTRICTED_SHELL` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | restricted_shell |
| `C11.SHOPT.SHIFT_VERBOSE` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | shift_verbose |
| `C11.SHOPT.SOURCEPATH` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | sourcepath |
| `C11.SHOPT.XPG_ECHO` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | xpg_echo |

Notes:

- `C11.SHOPT.ASSOC_EXPAND_ONCE`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C11.SHOPT.AUTOCD`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C11.SHOPT.CDABLE_VARS`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C11.SHOPT.CDSPELL`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C11.SHOPT.CHECKHASH`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C11.SHOPT.CHECKJOBS`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C11.SHOPT.CHECKWINSIZE`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C11.SHOPT.COMPAT31`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- (Plus 37 additional row notes; see `docs/specs/feature-index.tsv`.)

### `subcategory:state-model`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C10.STATE.03` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh,man-bash-posix-14-env-exec-flow.sh,bash-builtin-declare-typeset-local.sh` | array/indexed/assoc state model |
| `C10.STATE.06` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh,man-bash-posix-14-env-exec-flow.sh,bash-builtin-declare-typeset-local.sh` | special variable side effects (RANDOM, LINENO, SECONDS, REPLY) |

Notes:

- `C10.STATE.03`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C10.STATE.06`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.

### `subcategory:variables.special-parameters`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.SPARAM.01` | `bash-man` | bash(1) section PARAMETERS | `covered / covered` | `bash-compat-param-positional-extended.sh` | $* |
| `C6.SPARAM.02` | `bash-man` | bash(1) section PARAMETERS | `covered / covered` | `bash-compat-param-positional-extended.sh` | $@ |
| `C6.SPARAM.03` | `bash-man` | bash(1) section PARAMETERS | `covered / covered` | `bash-compat-param-positional-extended.sh` | $# |
| `C6.SPARAM.04` | `bash-man` | bash(1) section PARAMETERS | `covered / covered` | `bash-compat-param-positional-extended.sh` | $? |
| `C6.SPARAM.05` | `bash-man` | bash(1) section PARAMETERS | `covered / covered` | `bash-compat-param-positional-extended.sh` | $- |
| `C6.SPARAM.06` | `bash-man` | bash(1) section PARAMETERS | `covered / covered` | `bash-compat-param-positional-extended.sh` | $$ |
| `C6.SPARAM.07` | `bash-man` | bash(1) section PARAMETERS | `covered / covered` | `bash-compat-param-positional-extended.sh` | $! |
| `C6.SPARAM.08` | `bash-man` | bash(1) section PARAMETERS | `covered / covered` | `bash-compat-param-positional-extended.sh` | $0 |
| `C6.SPARAM.09` | `bash-man` | bash(1) section PARAMETERS | `covered / covered` | `bash-compat-param-positional-extended.sh` | $1..$N |

Notes:

- `C6.SPARAM.01`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C6.SPARAM.02`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C6.SPARAM.03`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C6.SPARAM.04`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C6.SPARAM.05`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C6.SPARAM.06`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C6.SPARAM.07`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C6.SPARAM.08`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- (Plus 1 additional row notes; see `docs/specs/feature-index.tsv`.)

### `syntax:arithmetic`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BCOMPAT.51.002` | `bash-compat-doc` | bash/COMPAT level 51 item 2 | `partial / partial` | `bash-compat-doc-51-002.sh` | arithmetic commands ( ((...)) ) and the expressions in an arithmetic for statement can be expanded more than once |
| `BCOMPAT.51.007` | `bash-compat-doc` | bash/COMPAT level 51 item 7 | `partial / partial` | `bash-compat-doc-51-007.sh` | arithmetic expressions used as indexed array subscripts can be expanded more than once; |
| `C2.GRAM.017` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | arithmetic for (( expr1 ; expr2 ; expr3 )) |

Notes:

- `BCOMPAT.51.002`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat51 (set using BASH_COMPAT) i…
- `BCOMPAT.51.007`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat51 (set using BASH_COMPAT) i…
- `C2.GRAM.017`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.

### `syntax:command-substitution`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BCOMPAT.51.006` | `bash-compat-doc` | bash/COMPAT level 51 item 6 | `partial / partial` | `bash-compat-doc-51-006.sh` | the expressions in the $(( ... )) word expansion can be expanded more than once |
| `C3.EXP.023` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `bash-man-expansion-core.sh` | arithmetic expansion $((expr)) |

Notes:

- `BCOMPAT.51.006`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat51 (set using BASH_COMPAT) i…
- `C3.EXP.023`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.

### `syntax:parameter-expansion`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BCOMPAT.41.002` | `bash-compat-doc` | bash/COMPAT level 41 item 2 | `partial / partial` | `bash-compat-doc-41-002.sh` | in posix mode, the parser requires that an even number of single quotes occur in the `word' portion of a double-quoted ${...} parameter expansion and treats them specially, so that characters within the single quotes are considered quoted (this is POSIX interpretation 221) |
| `BCOMPAT.42.002` | `bash-compat-doc` | bash/COMPAT level 42 item 2 | `partial / partial` | `bash-compat-doc-42-002.sh` | in posix mode, single quotes are considered special when expanding the `word' portion of a double-quoted ${...} parameter expansion and can be used to quote a closing brace or other special character (this is part of POSIX interpretation 221); in later versions, single quotes are not special within double-quoted word expansions |
| `BPOSIX.CORE.008` | `bash-posix-doc` | bash/POSIX 6.11.2 item 8 | `covered / covered` | `bash-posix-doc-008.sh` | When parsing and expanding a ${...} expansion that appears within double quotes, single quotes are no longer special and cannot be used to quote a closing brace or other special character, unless the operator is one of those defined to perform pattern removal. In this case, they do not have to appear as matched pairs. |
| `C3.EXP.003` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh` | parameter expansion $name ${name} |
| `C3.EXP.005` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh` | positional parameters $1..${N} |
| `C3.EXP.006` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh` | parameter default operators ${v-word} ${v:-word} |
| `C3.EXP.007` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh` | parameter assign operators ${v=word} ${v:=word} |
| `C3.EXP.008` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh` | parameter error operators ${v?word} ${v:?word} |
| `C3.EXP.009` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh` | parameter alternate operators ${v+word} ${v:+word} |
| `C3.EXP.010` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `bash-man-expansion-core.sh` | substring expansion ${v:offset} ${v:offset:length} |
| `C3.EXP.011` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `bash-man-expansion-core.sh` | length expansion ${#v} |
| `C3.EXP.012` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `bash-man-expansion-core.sh` | prefix trim ${v#pat} ${v##pat} |
| `C3.EXP.013` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `bash-man-expansion-core.sh` | suffix trim ${v%pat} ${v%%pat} |
| `C3.EXP.014` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `bash-man-expansion-core.sh` | replacement ${v/pat/repl} ${v//pat/repl} |
| `C3.EXP.015` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh` | case modification ${v^} ${v^^} ${v,} ${v,,} |
| `C3.EXP.016` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `bash-man-param-transform-ops.sh,bash-man-param-transform-ops-variants.sh,bash-man-param-transform-prompt.sh,bash-man-param-transform-prompt-escapes.sh` | transformation operator ${v@op} (scalar/positional/array variants) |
| `C3.EXP.017` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh` | indirection ${!name} |
| `C3.EXP.018` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh` | name expansion ${!prefix*} ${!prefix@} |
| `C3.EXP.019` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh` | array subscript expansion ${a[i]} ${a[@]} ${a[*]} |
| `C3.EXP.020` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `man-ash-var-ops-matrix.sh,bash-compat-param-array-hash-extended.sh` | array slicing ${a[@]:o:l} |

Notes:

- `BCOMPAT.41.002`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat41 item 2; compatibility del…
- `BCOMPAT.42.002`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat42 item 2; compatibility del…
- `BPOSIX.CORE.008`: Row-level comparator evidence passes in tests/diff/cases/bash-posix-doc-001-010.sh; Source: bash/POSIX 6.11.2 item 8.
- `C3.EXP.003`: Expansion rows validated by man-ash-var-ops-matrix.sh, bash-compat-param-array-hash-extended.sh, and bash-man-expansion-process-subst.sh; c…
- `C3.EXP.005`: Expansion rows validated by man-ash-var-ops-matrix.sh, bash-compat-param-array-hash-extended.sh, and bash-man-expansion-process-subst.sh; c…
- `C3.EXP.006`: Expansion rows validated by man-ash-var-ops-matrix.sh, bash-compat-param-array-hash-extended.sh, and bash-man-expansion-process-subst.sh; c…
- `C3.EXP.007`: Expansion rows validated by man-ash-var-ops-matrix.sh, bash-compat-param-array-hash-extended.sh, and bash-man-expansion-process-subst.sh; c…
- `C3.EXP.008`: Expansion rows validated by man-ash-var-ops-matrix.sh, bash-compat-param-array-hash-extended.sh, and bash-man-expansion-process-subst.sh; c…
- (Plus 12 additional row notes; see `docs/specs/feature-index.tsv`.)

### `syntax:quoting`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BCOMPAT.42.001` | `bash-compat-doc` | bash/COMPAT level 42 item 1 | `partial / partial` | `bash-compat-doc-42-001.sh` | the replacement string in double-quoted pattern substitution is not run through quote removal, as it is in versions after bash-4.2 |
| `BPOSIX.CORE.014` | `bash-posix-doc` | bash/POSIX 6.11.2 item 14 | `covered / covered` | `bash-posix-doc-014.sh` | Expanding the ‘*’ special parameter in a pattern context where the expansion is double-quoted does not treat the ‘$*’ as if it were double-quoted. |
| `C11.SHOPT.COMPLETE_FULLQUOTE` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | complete_fullquote |
| `C11.SHOPT.EXTQUOTE` | `bash-man` | bash(1) section SHELL BUILTIN COMMANDS (shopt) | `covered / covered` | `bash-man-shopt-surface.sh` | extquote |
| `C3.EXP.027` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `bash-man-expansion-core.sh` | quote removal |
| `C3.EXP.028` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `bash-man-expansion-core.sh` | ANSI-C quoting $'...' |
| `C3.EXP.029` | `bash-man` | bash(1) section QUOTING + PARAMETERS + EXPANSION | `covered / covered` | `bash-man-expansion-brace-locale.sh` | locale translation quoting $"..." |

Notes:

- `BCOMPAT.42.001`: Scaffold comparator case mapped and executable; strict row-level assertions pending. Source: bash/COMPAT compat42 item 1; compatibility del…
- `BPOSIX.CORE.014`: Comparator parity: PS1/PS2 parameter expansions apply in POSIX lane.
- `C11.SHOPT.COMPLETE_FULLQUOTE`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C11.SHOPT.EXTQUOTE`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C3.EXP.027`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C3.EXP.028`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C3.EXP.029`: locale $"..." parsing/execution path implemented (identity translation under C locale); mapped evidence run passes.

### `syntax:redirection`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `BPOSIX.CORE.009` | `bash-posix-doc` | bash/POSIX 6.11.2 item 9 | `covered / covered` | `bash-posix-doc-009.sh` | Redirection operators do not perform filename expansion on the word in a redirection unless the shell is interactive. |
| `BPOSIX.CORE.010` | `bash-posix-doc` | bash/POSIX 6.11.2 item 10 | `covered / covered` | `bash-posix-doc-010.sh` | Redirection operators do not perform word splitting on the word in a redirection. |
| `C2.GRAM.028` | `bash-man` | bash(1) section SHELL GRAMMAR | `covered / covered` | `bash-man-grammar-core.sh` | here-doc grammar attachment and queueing |
| `C4.REDIR.001` | `bash-man` | bash(1) section REDIRECTION | `covered / covered` | `man-ash-redir-heredoc-matrix.sh` | [n]<word input redirection |
| `C4.REDIR.002` | `bash-man` | bash(1) section REDIRECTION | `covered / covered` | `man-ash-redir-heredoc-matrix.sh` | [n]>word output redirection |
| `C4.REDIR.003` | `bash-man` | bash(1) section REDIRECTION | `covered / covered` | `man-ash-redir-heredoc-matrix.sh` | [n]>>word append redirection |
| `C4.REDIR.010` | `bash-man` | bash(1) section REDIRECTION | `covered / covered` | `man-ash-redir-heredoc-matrix.sh` | here-document <<word |
| `C4.REDIR.011` | `bash-man` | bash(1) section REDIRECTION | `covered / covered` | `man-ash-redir-heredoc-matrix.sh` | here-document with tab-strip <<-word |
| `C4.REDIR.012` | `bash-man` | bash(1) section REDIRECTION | `covered / covered` | `bash-man-redir-here-string.sh` | here-string <<<word |
| `C4.REDIR.016` | `bash-man` | bash(1) section REDIRECTION | `covered / covered` | `bash-man-redir-bash-ext.sh` | named-fd redirection {varname}<word and family |
| `C4.REDIR.017` | `bash-man` | bash(1) section REDIRECTION | `covered / covered` | `man-ash-redir-heredoc-matrix.sh` | /dev/fd/N pseudo-path redirection |
| `C4.REDIR.019` | `bash-man` | bash(1) section REDIRECTION | `covered / covered` | `bash-man-redir-bash-ext.sh` | /dev/tcp/host/port redirection |
| `C4.REDIR.020` | `bash-man` | bash(1) section REDIRECTION | `covered / covered` | `bash-man-redir-bash-ext.sh` | /dev/udp/host/port redirection |
| `C4.REDIR.021` | `bash-man` | bash(1) section REDIRECTION | `covered / covered` | `man-ash-redir-heredoc-matrix.sh` | redirection ordering left-to-right |

Notes:

- `BPOSIX.CORE.009`: Row-level comparator evidence passes in tests/diff/cases/bash-posix-doc-001-010.sh; Source: bash/POSIX 6.11.2 item 9.
- `BPOSIX.CORE.010`: Row-level comparator evidence passes in tests/diff/cases/bash-posix-doc-001-010.sh; Source: bash/POSIX 6.11.2 item 10.
- `C2.GRAM.028`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C4.REDIR.001`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C4.REDIR.002`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C4.REDIR.003`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C4.REDIR.010`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- `C4.REDIR.011`: Row-level evidence mapping assigned from requirement->case rules. Evidence run: mapped tests all pass.
- (Plus 6 additional row notes; see `docs/specs/feature-index.tsv`.)

### `var:BASH`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.BASH` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | BASH |

Notes:

- `C6.VAR.BASH.BASH`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:BASHOPTS`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.BASHOPTS` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | BASHOPTS |

Notes:

- `C6.VAR.BASH.BASHOPTS`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:BASHPID`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.BASHPID` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | BASHPID |

Notes:

- `C6.VAR.BASH.BASHPID`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:BASH_ARGC`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.BASH_ARGC` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | BASH_ARGC |

Notes:

- `C6.VAR.BASH.BASH_ARGC`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:BASH_ARGV`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.BASH_ARGV` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | BASH_ARGV |

Notes:

- `C6.VAR.BASH.BASH_ARGV`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:BASH_ARGV0`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.BASH_ARGV0` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | BASH_ARGV0 |

Notes:

- `C6.VAR.BASH.BASH_ARGV0`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:BASH_CMDS`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.BASH_CMDS` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | BASH_CMDS |

Notes:

- `C6.VAR.BASH.BASH_CMDS`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:BASH_COMMAND`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.BASH_COMMAND` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | BASH_COMMAND |

Notes:

- `C6.VAR.BASH.BASH_COMMAND`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:BASH_COMPAT`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.BASH_COMPAT` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | BASH_COMPAT |

Notes:

- `C6.VAR.BASH.BASH_COMPAT`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:BASH_ENV`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.BASH_ENV` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | BASH_ENV |

Notes:

- `C6.VAR.BASH.BASH_ENV`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:BASH_LINENO`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.BASH_LINENO` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | BASH_LINENO |

Notes:

- `C6.VAR.BASH.BASH_LINENO`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:BASH_LOADABLES_PATH`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.BASH_LOADABLES_PATH` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | BASH_LOADABLES_PATH |

Notes:

- `C6.VAR.BASH.BASH_LOADABLES_PATH`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:BASH_REMATCH`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.BASH_REMATCH` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | BASH_REMATCH |

Notes:

- `C6.VAR.BASH.BASH_REMATCH`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:BASH_SOURCE`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.BASH_SOURCE` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | BASH_SOURCE |

Notes:

- `C6.VAR.BASH.BASH_SOURCE`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:BASH_SUBSHELL`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.BASH_SUBSHELL` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | BASH_SUBSHELL |

Notes:

- `C6.VAR.BASH.BASH_SUBSHELL`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:BASH_VERSINFO`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.BASH_VERSINFO` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | BASH_VERSINFO |

Notes:

- `C6.VAR.BASH.BASH_VERSINFO`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:BASH_VERSION`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.BASH_VERSION` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | BASH_VERSION |

Notes:

- `C6.VAR.BASH.BASH_VERSION`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:BASH_XTRACEFD`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.BASH_XTRACEFD` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh,bash-man-bash_xtracefd.sh` | BASH_XTRACEFD |

Notes:

- `C6.VAR.BASH.BASH_XTRACEFD`: Trace stream routing to configured FD is parity-covered by dedicated differential evidence.

### `var:COMPREPLY`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.COMPREPLY` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | COMPREPLY |

Notes:

- `C6.VAR.BASH.COMPREPLY`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:COMP_CWORD`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.COMP_CWORD` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | COMP_CWORD |

Notes:

- `C6.VAR.BASH.COMP_CWORD`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:COMP_KEY`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.COMP_KEY` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | COMP_KEY |

Notes:

- `C6.VAR.BASH.COMP_KEY`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:COMP_LINE`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.COMP_LINE` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | COMP_LINE |

Notes:

- `C6.VAR.BASH.COMP_LINE`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:COMP_POINT`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.COMP_POINT` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | COMP_POINT |

Notes:

- `C6.VAR.BASH.COMP_POINT`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:COMP_TYPE`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.COMP_TYPE` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | COMP_TYPE |

Notes:

- `C6.VAR.BASH.COMP_TYPE`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:COMP_WORDBREAKS`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.COMP_WORDBREAKS` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | COMP_WORDBREAKS |

Notes:

- `C6.VAR.BASH.COMP_WORDBREAKS`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:COMP_WORDS`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.COMP_WORDS` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | COMP_WORDS |

Notes:

- `C6.VAR.BASH.COMP_WORDS`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:COPROC`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.COPROC` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | COPROC |

Notes:

- `C6.VAR.BASH.COPROC`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:DIRSTACK`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.DIRSTACK` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | DIRSTACK |

Notes:

- `C6.VAR.BASH.DIRSTACK`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:ENV`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.CORE.ENV` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh` | ENV |

Notes:

- `C6.VAR.CORE.ENV`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:EPOCHREALTIME`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.EPOCHREALTIME` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | EPOCHREALTIME |

Notes:

- `C6.VAR.BASH.EPOCHREALTIME`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:EPOCHSECONDS`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.EPOCHSECONDS` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | EPOCHSECONDS |

Notes:

- `C6.VAR.BASH.EPOCHSECONDS`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:EUID`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.EUID` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | EUID |

Notes:

- `C6.VAR.BASH.EUID`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:FCEDIT`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.FCEDIT` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | FCEDIT |

Notes:

- `C6.VAR.BASH.FCEDIT`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:FUNCNAME`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.FUNCNAME` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | FUNCNAME |

Notes:

- `C6.VAR.BASH.FUNCNAME`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:GROUPS`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.GROUPS` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | GROUPS |

Notes:

- `C6.VAR.BASH.GROUPS`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:HISTCONTROL`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.HISTCONTROL` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | HISTCONTROL |

Notes:

- `C6.VAR.BASH.HISTCONTROL`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:HISTFILE`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.HISTFILE` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | HISTFILE |

Notes:

- `C6.VAR.BASH.HISTFILE`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:HISTFILESIZE`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.HISTFILESIZE` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | HISTFILESIZE |

Notes:

- `C6.VAR.BASH.HISTFILESIZE`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:HISTIGNORE`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.HISTIGNORE` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | HISTIGNORE |

Notes:

- `C6.VAR.BASH.HISTIGNORE`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:HISTSIZE`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.HISTSIZE` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | HISTSIZE |

Notes:

- `C6.VAR.BASH.HISTSIZE`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:HISTTIMEFORMAT`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.HISTTIMEFORMAT` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh,bash-man-histtimeformat.sh` | HISTTIMEFORMAT |

Notes:

- `C6.VAR.BASH.HISTTIMEFORMAT`: History timestamp-prefix behavior under `HISTTIMEFORMAT` is parity-covered with dedicated comparator evidence.

### `var:HOME`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.CORE.HOME` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh` | HOME |

Notes:

- `C6.VAR.CORE.HOME`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:HOSTFILE`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.HOSTFILE` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | HOSTFILE |

Notes:

- `C6.VAR.BASH.HOSTFILE`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:IFS`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.CORE.IFS` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh` | IFS |

Notes:

- `C6.VAR.CORE.IFS`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:LANG`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.CORE.LANG` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh` | LANG |

Notes:

- `C6.VAR.CORE.LANG`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:LC_ALL`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.CORE.LC_ALL` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh` | LC_ALL |

Notes:

- `C6.VAR.CORE.LC_ALL`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:LC_CTYPE`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.CORE.LC_CTYPE` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh` | LC_CTYPE |

Notes:

- `C6.VAR.CORE.LC_CTYPE`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:LC_MESSAGES`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.CORE.LC_MESSAGES` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh` | LC_MESSAGES |

Notes:

- `C6.VAR.CORE.LC_MESSAGES`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:LINENO`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.CORE.LINENO` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh` | LINENO |

Notes:

- `C6.VAR.CORE.LINENO`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:MAIL`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.CORE.MAIL` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh` | MAIL |

Notes:

- `C6.VAR.CORE.MAIL`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:MAILPATH`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.CORE.MAILPATH` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh` | MAILPATH |

Notes:

- `C6.VAR.CORE.MAILPATH`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:OLDPWD`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.CORE.OLDPWD` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh` | OLDPWD |

Notes:

- `C6.VAR.CORE.OLDPWD`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:OPTARG`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.CORE.OPTARG` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh` | OPTARG |

Notes:

- `C6.VAR.CORE.OPTARG`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:OPTIND`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.CORE.OPTIND` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh` | OPTIND |

Notes:

- `C6.VAR.CORE.OPTIND`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:PATH`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.CORE.PATH` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh` | PATH |

Notes:

- `C6.VAR.CORE.PATH`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:PPID`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.PPID` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | PPID |

Notes:

- `C6.VAR.BASH.PPID`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:PROMPT_COMMAND`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.PROMPT_COMMAND` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | PROMPT_COMMAND |

Notes:

- `C6.VAR.BASH.PROMPT_COMMAND`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:PS0`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.PS0` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | PS0 |

Notes:

- `C6.VAR.BASH.PS0`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:PS1`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.CORE.PS1` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh,run_interactive_ux_matrix.sh` | PS1 |

Notes:

- `C6.VAR.CORE.PS1`: Surface presence plus interactive prompt render behavior evidence (PROMPTING + promptvars-on interpolation path).

### `var:PS2`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.CORE.PS2` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh` | PS2 |

Notes:

- `C6.VAR.CORE.PS2`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:PS3`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.PS3` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | PS3 |

Notes:

- `C6.VAR.BASH.PS3`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:PS4`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.PS4` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | PS4 |

Notes:

- `C6.VAR.BASH.PS4`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:PWD`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.CORE.PWD` | `bash-man` | bash(1) section PARAMETERS + Shell Variables | `covered / covered` | `bash-man-variables-surface.sh` | PWD |

Notes:

- `C6.VAR.CORE.PWD`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:RANDOM`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.RANDOM` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | RANDOM |

Notes:

- `C6.VAR.BASH.RANDOM`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:REPLY`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.REPLY` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | REPLY |

Notes:

- `C6.VAR.BASH.REPLY`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:SECONDS`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.SECONDS` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | SECONDS |

Notes:

- `C6.VAR.BASH.SECONDS`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:SHELLOPTS`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.SHELLOPTS` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | SHELLOPTS |

Notes:

- `C6.VAR.BASH.SHELLOPTS`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:SRANDOM`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.SRANDOM` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | SRANDOM |

Notes:

- `C6.VAR.BASH.SRANDOM`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.

### `var:TIMEFORMAT`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.TIMEFORMAT` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-timeformat.sh` | TIMEFORMAT |

Notes:

- `C6.VAR.BASH.TIMEFORMAT`: `TIMEFORMAT` `%R/%U/%S/%P/%%` rendering and invalid-format diagnostics are now parity-covered in dedicated differential evidence.

### `var:TMOUT`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.TMOUT` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh,run_interactive_tmout_matrix.sh` | TMOUT |

Notes:

- `C6.VAR.BASH.TMOUT`: Interactive timeout/auto-logout semantics are parity-covered by dedicated PTY matrix evidence.

### `var:UID`

| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|---|
| `C6.VAR.BASH.UID` | `bash-man` | bash(1) section Shell Variables + builtins | `covered / covered` | `bash-man-variables-surface.sh` | UID |

Notes:

- `C6.VAR.BASH.UID`: Mapped by bash-man-variables-surface.sh; comparator evidence run passes in default and --posix lanes.
