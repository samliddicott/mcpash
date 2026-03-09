# Feature Gap Board

Generated: 2026-03-09 10:22:51Z

Purpose: implementation-first backlog grouped by feature topic (rows where either default or posix status is not `covered`).

## Topic Backlog Summary

| Topic | Gap Rows |
|---|---:|
| `builtin:alias` | 1 |
| `builtin:bg` | 1 |
| `builtin:bind` | 1 |
| `builtin:break` | 2 |
| `builtin:cd` | 2 |
| `builtin:command` | 12 |
| `builtin:continue` | 1 |
| `builtin:echo` | 2 |
| `builtin:export` | 1 |
| `builtin:history` | 3 |
| `builtin:jobs` | 1 |
| `builtin:kill` | 3 |
| `builtin:printf` | 1 |
| `builtin:pwd` | 1 |
| `builtin:read` | 1 |
| `builtin:return` | 2 |
| `builtin:set` | 5 |
| `builtin:shift` | 1 |
| `builtin:source` | 1 |
| `builtin:test` | 3 |
| `builtin:trap` | 2 |
| `builtin:type` | 1 |
| `builtin:ulimit` | 1 |
| `builtin:unset` | 1 |
| `builtin:wait` | 3 |
| `runtime:job-control` | 4 |
| `runtime:signals-traps` | 1 |
| `subcategory:compat-delta` | 3 |
| `subcategory:expansion-redir` | 1 |
| `subcategory:interactive` | 1 |
| `subcategory:misc-posix-mode` | 1 |
| `syntax:arithmetic` | 2 |
| `syntax:command-substitution` | 1 |
| `syntax:parameter-expansion` | 2 |
| `syntax:quoting` | 1 |

## Gap Topics

### `builtin:alias`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.CORE.047` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-047.sh` | When the ‘alias’ builtin displays alias definitions, it does not display them with a leading ‘alias ’ unless the ‘-p’ option is supplied. |

### `builtin:bg`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.CORE.048` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-048.sh` | The ‘bg’ builtin uses the required format to describe each job placed in the background, which does not include an indication of whether the job is the current or previous job. |

### `builtin:bind`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BCOMPAT.52.002` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-52-002.sh` | the -p and -P options to the bind builtin treat remaining arguments as bindable command names for which to print any key bindings |

### `builtin:break`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BCOMPAT.43.002` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-43-002.sh` | when executing a shell function, the loop state (while/until/etc.) is not reset, so `break' or `continue' in that function will break or continue loops in the calling context. Bash-4.4 and later reset the loop state to prevent this |
| `BCOMPAT.44.002` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-44-002.sh` | a subshell inherits loops from its parent context, so `break' or `continue' will cause the subshell to exit. Bash-5.0 and later reset the loop state to prevent the exit |

### `builtin:cd`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.CORE.049` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-049.sh` | When the ‘cd’ builtin is invoked in logical mode, and the pathname constructed from ‘$PWD’ and the directory name supplied as an argument does not refer to an existing directory, ‘cd’ will fail instead of falling back to physical mode. |
| `BPOSIX.CORE.050` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-050.sh` | When the ‘cd’ builtin cannot change a directory because the length of the pathname constructed from ‘$PWD’ and the directory name supplied as an argument exceeds ‘PATH_MAX’ when canonicalized, ‘cd’ will attempt to use the supplied directory name. |

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
| `BPOSIX.CORE.042` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-042.sh` | The ‘command’ builtin does not prevent builtins that take assignment statements as arguments from expanding them as assignment statements; when not in POSIX mode, declaration commands lose their assignment statement expansion properties when preceded by ‘command’. |
| `BPOSIX.CORE.043` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-043.sh` | Enabling POSIX mode has the effect of setting the ‘inherit_errexit’ option, so subshells spawned to execute command substitutions inherit the value of the ‘-e’ option from the parent shell. When the ‘inherit_errexit’ option is not enabled, Bash clears the ‘-e’ option in such subshells. |

### `builtin:continue`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BCOMPAT.44.003` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-44-003.sh` | variable assignments preceding builtins like export and readonly that set attributes continue to affect variables with the same name in the calling environment even if the shell is not in posix mode |

### `builtin:echo`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.CORE.051` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-051.sh` | When the ‘xpg_echo’ option is enabled, Bash does not attempt to interpret any arguments to ‘echo’ as options. ‘echo’ displays each argument after converting escape sequences. |
| `BPOSIX.EXTRA.003` | `bash-posix-doc` | `partial / out_of_scope` | `bash-posix-doc-extra-003.sh` | As noted above, Bash requires the ‘xpg_echo’ option to be enabled for the ‘echo’ builtin to be fully conformant. |

### `builtin:export`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.CORE.052` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-052.sh` | The ‘export’ and ‘readonly’ builtin commands display their output in the format required by POSIX. |

### `builtin:history`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.CORE.028` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-028.sh` | Prompt expansion enables the POSIX ‘PS1’ and ‘PS2’ expansions of ‘!’ to the history number and ‘!!’ to ‘!’, and Bash performs parameter expansion on the values of ‘PS1’ and ‘PS2’ regardless of the setting of the ‘promptvars’ option. |
| `BPOSIX.CORE.029` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-029.sh` | The default history file is ‘~/.sh_history’ (this is the default value the shell assigns to ‘$HISTFILE’). |
| `BPOSIX.CORE.030` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-030.sh` | The ‘!’ character does not introduce history expansion within a double-quoted string, even if the ‘histexpand’ option is enabled. |

### `builtin:jobs`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BCOMPAT.52.003` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-52-003.sh` | interactive shells will notify the user of completed jobs while sourcing a script. Newer versions defer notification until script execution completes. |

### `builtin:kill`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.CORE.057` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-057.sh` | The output of ‘kill -l’ prints all the signal names on a single line, separated by spaces, without the ‘SIG’ prefix. |
| `BPOSIX.CORE.058` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-058.sh` | The ‘kill’ builtin does not accept signal names with a ‘SIG’ prefix. |
| `BPOSIX.CORE.059` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-059.sh` | The ‘kill’ builtin returns a failure status if any of the pid or job arguments are invalid or if sending the specified signal to any of them fails. In default mode, ‘kill’ returns success if the signal was successfully sent to any of the specified processes. |

### `builtin:printf`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.CORE.060` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-060.sh` | The ‘printf’ builtin uses ‘double’ (via ‘strtod’) to convert arguments corresponding to floating point conversion specifiers, instead of ‘long double’ if it's available. The ‘L’ length modifier forces ‘printf’ to use ‘long double’ if it's available. |

### `builtin:pwd`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.CORE.061` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-061.sh` | The ‘pwd’ builtin verifies that the value it prints is the same as the current directory, even if it is not asked to check the file system with the ‘-P’ option. |

### `builtin:read`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.CORE.062` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-062.sh` | The ‘read’ builtin may be interrupted by a signal for which a trap has been set. If Bash receives a trapped signal while executing ‘read’, the trap handler executes and ‘read’ returns an exit status greater than 128. |

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
| `BPOSIX.CORE.063` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-063.sh` | When the ‘set’ builtin is invoked without options, it does not display shell function names and definitions. |
| `BPOSIX.CORE.064` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-064.sh` | When the ‘set’ builtin is invoked without options, it displays variable values without quotes, unless they contain shell metacharacters, even if the result contains nonprinting characters. |
| `BPOSIX.CORE.069` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-069.sh` | ‘trap -p’ without arguments displays signals whose dispositions are set to SIG_DFL and those that were ignored when the shell started, not just trapped signals. |

### `builtin:shift`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.CORE.044` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-044.sh` | Enabling POSIX mode has the effect of setting the ‘shift_verbose’ option, so numeric arguments to ‘shift’ that exceed the number of positional parameters will result in an error message. |

### `builtin:source`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.CORE.046` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-046.sh` | The ‘.’ and ‘source’ builtins do not search the current directory for the filename argument if it is not found by searching ‘PATH’. |

### `builtin:test`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BCOMPAT.52.001` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-52-001.sh` | the test builtin uses its historical algorithm for parsing expressions composed of five or more primaries. |
| `BPOSIX.CORE.065` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-065.sh` | The ‘test’ builtin compares strings using the current locale when evaluating the ‘<’ and ‘>’ binary operators. |
| `BPOSIX.CORE.066` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-066.sh` | The ‘test’ builtin's ‘-t’ unary primary requires an argument. Historical versions of ‘test’ made the argument optional in certain cases, and Bash attempts to accommodate those for backwards compatibility. |

### `builtin:trap`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.CORE.067` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-067.sh` | The ‘trap’ builtin displays signal names without the leading ‘SIG’. |
| `BPOSIX.CORE.068` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-068.sh` | The ‘trap’ builtin doesn't check the first argument for a possible signal specification and revert the signal handling to the original disposition if it is, unless that argument consists solely of digits and is a valid signal number. If users want to reset the handler for a given signal to the original disposition, they should use ‘-’ as the first argument. |

### `builtin:type`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.CORE.031` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-031.sh` | When printing shell function definitions (e.g., by ‘type’), Bash does not print the ‘function’ reserved word unless necessary. |

### `builtin:ulimit`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.CORE.071` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-071.sh` | The ‘ulimit’ builtin uses a block size of 512 bytes for the ‘-c’ and ‘-f’ options. |

### `builtin:unset`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BCOMPAT.51.001` | `bash-compat-doc` | `partial / partial` | `bash-compat-doc-51-001.sh` | The `unset' builtin will unset the array a given an argument like `a[@]'. Bash-5.2 will unset an element with key `@' (associative arrays) or remove all the elements without unsetting the array (indexed arrays) |

### `builtin:wait`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.CORE.026` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-026.sh` | Bash permanently removes jobs from the jobs table after notifying the user of their termination via the ‘wait’ or ‘jobs’ builtins. It removes the job from the jobs list after notifying the user of its termination, but the status is still available via ‘wait’, as long as ‘wait’ is supplied a PID argument. |
| `BPOSIX.CORE.074` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-074.sh` | The arrival of ‘SIGCHLD’ when a trap is set on ‘SIGCHLD’ does not interrupt the ‘wait’ builtin and cause it to return immediately. The trap command is run once for each child that exits. |
| `BPOSIX.CORE.075` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-075.sh` | Bash removes an exited background process's status from the list of such statuses after the ‘wait’ builtin returns it. |

### `runtime:job-control`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.CORE.022` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-022.sh` | The message printed by the job control code and builtins when a job exits with a non-zero status is 'Done(status)'. |
| `BPOSIX.CORE.023` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-023.sh` | The message printed by the job control code and builtins when a job is stopped is 'Stopped(SIGNAME)', where SIGNAME is, for example, ‘SIGTSTP’. |
| `BPOSIX.CORE.024` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-024.sh` | If the shell is interactive, Bash does not perform job notifications between executing commands in lists separated by ‘;’ or newline. Non-interactive shells print status messages after a foreground job in a list completes. |
| `BPOSIX.CORE.025` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-025.sh` | If the shell is interactive, Bash waits until the next prompt before printing the status of a background job that changes status or a foreground job that terminates due to a signal. Non-interactive shells print status messages after a foreground job completes. |

### `runtime:signals-traps`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.CORE.041` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-041.sh` | Assignment statements preceding POSIX special builtins persist in the shell environment after the builtin completes. |

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

### `subcategory:interactive`

| Req ID | Source | Status (default/posix) | Tests | Feature |
|---|---|---|---|---|
| `BPOSIX.CORE.045` | `bash-posix-doc` | `partial / partial` | `bash-posix-doc-045.sh` | Enabling POSIX mode has the effect of setting the ‘interactive_comments’ option (*note Comments::). |

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
