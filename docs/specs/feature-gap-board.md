# Feature Gap Board

Generated: 2026-03-09 12:04:16Z

Purpose: implementation-first backlog grouped by feature topic (rows where either default or posix status is not `covered`).

## Topic Backlog Summary

| Topic | Gap Rows |
|---|---:|
| `builtin:bind` | 1 |
| `builtin:break` | 2 |
| `builtin:command` | 10 |
| `builtin:continue` | 1 |
| `builtin:echo` | 1 |
| `builtin:jobs` | 1 |
| `builtin:return` | 2 |
| `builtin:set` | 2 |
| `builtin:test` | 1 |
| `builtin:unset` | 1 |
| `runtime:job-control` | 2 |
| `subcategory:compat-delta` | 3 |
| `subcategory:expansion-redir` | 1 |
| `subcategory:misc-posix-mode` | 1 |
| `syntax:arithmetic` | 2 |
| `syntax:command-substitution` | 1 |
| `syntax:parameter-expansion` | 2 |
| `syntax:quoting` | 1 |

## Gap Topics

### `builtin:bind`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BCOMPAT.52.002` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-52-002.sh` | the -p and -P options to the bind builtin treat remaining arguments as bindable command names for which to print any key bindings |

### `builtin:break`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BCOMPAT.43.002` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-43-002.sh` | when executing a shell function, the loop state (while/until/etc.) is not reset, so `break' or `continue' in that function will break or continue loops in the calling context. Bash-4.4 and later reset the loop state to prevent this |
| `BCOMPAT.44.002` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-44-002.sh` | a subshell inherits loops from its parent context, so `break' or `continue' will cause the subshell to exit. Bash-5.0 and later reset the loop state to prevent the exit |

### `builtin:command`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BCOMPAT.31.001` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-31-001.sh` | the < and > operators to the [[ command do not consider the current locale when comparing strings; they use ASCII ordering |
| `BCOMPAT.31.002` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-31-002.sh` | quoting the rhs of the [[ command's regexp matching operator (=~) has no special effect |
| `BCOMPAT.32.001` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-32-001.sh` | the < and > operators to the [[ command do not consider the current locale when comparing strings; they use ASCII ordering |
| `BCOMPAT.40.001` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-40-001.sh` | the < and > operators to the [[ command do not consider the current locale when comparing strings; they use ASCII ordering. Bash versions prior to bash-4.1 use ASCII collation and strcmp(3); bash-4.1 and later use the current locale's collation sequence and strcoll(3). |
| `BCOMPAT.43.001` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-43-001.sh` | word expansion errors are considered non-fatal errors that cause the current command to fail, even in posix mode (the default behavior is to make them fatal errors that cause the shell to exit) |
| `BCOMPAT.50.002` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-50-002.sh` | If the command hash table is empty, bash versions prior to bash-5.1 printed an informational message to that effect even when writing output in a format that can be reused as input (-l). Bash-5.1 suppresses that message if -l is supplied |
| `BCOMPAT.51.003` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-51-003.sh` | expressions used as arguments to arithmetic operators in the [[ conditional command can be expanded more than once |
| `BCOMPAT.51.004` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-51-004.sh` | indexed and associative array subscripts used as arguments to the operators in the [[ conditional command (e.g., `[[ -v') can be expanded more than once. Bash-5.2 behaves as if the `assoc_expand_once' option were enabled. |
| `BCOMPAT.51.010` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-51-010.sh` | Parsing command substitutions will act as if extended glob is enabled, so that parsing a command substitution containing an extglob pattern (say, as part of a shell function) will not fail. This assumes the intent is to enable extglob before the command is executed and word expansions are performed. It will fail at word expansion time if extglob hasn't been enabled by the time the command is executed. |
| `BPOSIX.CORE.027` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-027.sh` | The ‘vi’ editing mode will invoke the ‘vi’ editor directly when the ‘v’ command is run, instead of checking ‘$VISUAL’ and ‘$EDITOR’. |

### `builtin:continue`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BCOMPAT.44.003` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-44-003.sh` | variable assignments preceding builtins like export and readonly that set attributes continue to affect variables with the same name in the calling environment even if the shell is not in posix mode |

### `builtin:echo`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.EXTRA.003` | `bash-posix-doc` | `partial / out_of_scope` | `bash-posix-doc-extra-003.sh` | As noted above, Bash requires the ‘xpg_echo’ option to be enabled for the ‘echo’ builtin to be fully conformant. |

### `builtin:jobs`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BCOMPAT.52.003` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-52-003.sh` | interactive shells will notify the user of completed jobs while sourcing a script. Newer versions defer notification until script execution completes. |

### `builtin:return`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BCOMPAT.51.008` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-51-008.sh` | `test -v', when given an argument of A[@], where A is an existing associative array, will return true if the array has any set elements. Bash-5.2 will look for a key named `@'; |
| `BCOMPAT.51.009` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-51-009.sh` | the ${param[:]=value} word expansion will return VALUE, before any variable-specific transformations have been performed (e.g., converting to lowercase). Bash-5.2 will return the final value assigned to the variable, as POSIX specifies; |

### `builtin:set`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BCOMPAT.50.001` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-50-001.sh` | Bash-5.1 changed the way $RANDOM is generated to introduce slightly more randomness. If the shell compatibility level is set to 50 or lower, it reverts to the method from bash-5.0 and previous versions, so seeding the random number generator by assigning a value to RANDOM will produce the same sequence as in bash-5.0 |
| `BCOMPAT.50.003` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-50-003.sh` | Bash-5.1 and later use pipes for here-documents and here-strings if they are smaller than the pipe capacity. If the shell compatibility level is set to 50 or lower, it reverts to using temporary files. |

### `builtin:test`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BCOMPAT.52.001` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-52-001.sh` | the test builtin uses its historical algorithm for parsing expressions composed of five or more primaries. |

### `builtin:unset`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BCOMPAT.51.001` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-51-001.sh` | The `unset' builtin will unset the array a given an argument like `a[@]'. Bash-5.2 will unset an element with key `@' (associative arrays) or remove all the elements without unsetting the array (indexed arrays) |

### `runtime:job-control`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.CORE.022` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-022.sh` | The message printed by the job control code and builtins when a job exits with a non-zero status is 'Done(status)'. |
| `BPOSIX.CORE.023` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-023.sh` | The message printed by the job control code and builtins when a job is stopped is 'Stopped(SIGNAME)', where SIGNAME is, for example, ‘SIGTSTP’. |

### `subcategory:compat-delta`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BCOMPAT.41.001` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-41-001.sh` | in posix mode, `time' may be followed by options and still be recognized as a reserved word (this is POSIX interpretation 267) |
| `BCOMPAT.44.001` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-44-001.sh` | the shell sets up the values used by BASH_ARGV and BASH_ARGC so they can expand to the shell's positional parameters even if extended debug mode is not enabled |
| `BCOMPAT.51.005` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-51-005.sh` | the expressions in substring parameter brace expansion can be expanded more than once |

### `subcategory:expansion-redir`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.EXTRA.001` | `bash-posix-doc` | `partial / out_of_scope` | `bash-posix-doc-extra-001.sh` | POSIX requires that word splitting be byte-oriented. That is, each _byte_ in the value of ‘IFS’ potentially splits a word, even if that byte is part of a multibyte character in ‘IFS’ or part of multibyte character in the word. Bash allows multibyte characters in the value of ‘IFS’, treating a valid multibyte character as a single delimiter, and will not split a valid multibyte character even if one of the bytes composing that character appears in ‘IFS’. This is POSIX interpretation 1560, further modified by issue 1924. |

### `subcategory:misc-posix-mode`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.CORE.019` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-019.sh` | Even if a shell function whose name contains a slash was defined before entering POSIX mode, the shell will not execute a function whose name contains one or more slashes. |

### `syntax:arithmetic`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BCOMPAT.51.002` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-51-002.sh` | arithmetic commands ( ((...)) ) and the expressions in an arithmetic for statement can be expanded more than once |
| `BCOMPAT.51.007` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-51-007.sh` | arithmetic expressions used as indexed array subscripts can be expanded more than once; |

### `syntax:command-substitution`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BCOMPAT.51.006` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-51-006.sh` | the expressions in the $(( ... )) word expansion can be expanded more than once |

### `syntax:parameter-expansion`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BCOMPAT.41.002` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-41-002.sh` | in posix mode, the parser requires that an even number of single quotes occur in the `word' portion of a double-quoted ${...} parameter expansion and treats them specially, so that characters within the single quotes are considered quoted (this is POSIX interpretation 221) |
| `BCOMPAT.42.002` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-42-002.sh` | in posix mode, single quotes are considered special when expanding the `word' portion of a double-quoted ${...} parameter expansion and can be used to quote a closing brace or other special character (this is part of POSIX interpretation 221); in later versions, single quotes are not special within double-quoted word expansions |

### `syntax:quoting`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BCOMPAT.42.001` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-42-001.sh` | the replacement string in double-quoted pattern substitution is not run through quote removal, as it is in versions after bash-4.2 |
