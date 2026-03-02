# Shell/Brush <-> Python Bridge Specification (Implementation Guide)

This is a practical, implementation-oriented spec for a POSIX shell written in Python that wants feature parity with the brush/bash Python bridge model.

## 1. Scope and goals


## Naming

- Canonical injected object name: `sh`
- Compatibility alias: `bash` (legacy alias retained for migration)
- Optional readability alias: `shell`

All normative API references in this spec use `sh.*`. Implementations MUST keep `bash.*`
as a compatibility alias for milestone-2 rollout.

The bridge must provide:

1. Shell -> Python execution (`py`, `PYTHON ... END_PYTHON`)
2. Python -> Shell callbacks (`sh()`, `sh.run`, `sh.popen`)
3. Shared shell-state access (`sh.vars`, `sh.env`, `sh.fn`, `sh.stack`, `sh.shared`)
4. Cross-language function exposure (`from ... import ... as ...`, callable wrappers)
5. Structured exception/status behavior suitable for shell scripting

Use RFC-style language:
- `MUST` = required for compatibility
- `SHOULD` = strongly recommended
- `MAY` = optional

## 2. Core execution model

1. Shell variable/function store is canonical for shell-visible state.
2. Python runtime is embedded/persistent within shell process lifetime.
3. Python accesses shell via injected `sh` object only.
4. Shell commands block until Python action completes (for `py`/`PYTHON`) unless explicitly using process APIs (`sh.popen`).
5. Subshell/pipeline semantics must match normal shell behavior.

## 3. Shell command surface

## 3.1 `py` command

`py` executes Python code with callable-first dispatch.

### 3.1.1 Forms

- `py 'python statements'`
- `py -e 'python expression'`
- `py <callable_name> [args...]`
- `py -r VAR <callable_or_expr>`
- `py -v VAR ...`
- `py -N` / `py -N-` (read script from file descriptor N; close for `-N-`)

### 3.1.2 Required options

- `-e`: evaluate expression mode
- `-x`: structured exception mode
- `-v VAR`: capture Python stdout into shell variable
- `-r VAR`: capture expression/call return value (`repr` or canonical stringify)
- `-N` / `-N-`: source from fd N (optional close)
- `-t VAR`: tie shell variable to Python bridge callbacks
- `-u VAR`: untie shell variable
- `--no-dedent`: disable dedent for block/fd sourced script

### 3.1.3 Exit status

- `0` success
- `1` Python exception/error
- `130` interrupted (SIGINT/cancel)

## 3.2 `PYTHON ... END_PYTHON` block

### 3.2.1 Grammar/behavior

- Start token: command `PYTHON` (may include options and redirections)
- End token: exact zero-indented line `END_PYTHON`
- Block body passed as raw Python text
- Dedent default: **on**
- `--no-dedent`: disable
- Same-line options accepted: `PYTHON -x -r out ...`
- Redirections and pipelines MUST work as normal command syntax around the block command

## 4. Structured exception contract (`-x`)

When `-x` is active and Python raises:

Set shell variables instead of printing traceback:

- `PYTHON_EXCEPTION` = exception type name
- `PYTHON_EXCEPTION_MSG` = message
- `PYTHON_EXCEPTION_TB` = array of traceback frames
- `PYTHON_EXCEPTION_LANG` = `python`

Status still non-zero (`1` unless interrupted).

## 5. Injected Python `sh` object

## 5.1 Constants

- `sh.PIPE`
- `sh.STDOUT`
- `sh.DEVNULL`

## 5.2 `sh.vars` (live shell vars mapping)

Required operations:

- `sh.vars[name]`
- `sh.vars[name] = value`
- `del sh.vars[name]`
- `name in sh.vars`
- iteration
- length
- `attrs(name)`
- `set_attrs(name, **flags)`
- `declare(name, value="", **flags)`

Type mapping (ash mode):
- scalar -> scalar var
- integer -> integer-attribute scalar var
- `list`/`tuple` and `dict` are deferred to Bash-compat mode and are out-of-scope in this milestone

Flags:
`exported`, `integer`, `readonly`, `uppercase`, `lowercase`, `nameref`, `trace`

## 5.3 `sh.env` (exported env only)

- same mapping interface as `vars`
- write implies set+export

## 5.4 `sh.fn` (shell functions)

- get/set/delete by name
- iteration/membership
- callable dispatch: `sh.fn.myfunc("a", "b")`
- setting callable SHOULD generate wrapper equivalent to `py` callable invocation

## 5.5 `sh.stack`

Read-only list/iterable of frames with:

- `kind` (`python`, `function`, `command_subst`, `source`, `subshell`, `trap`, `script`)
- `source`
- `lineno`
- `funcname`

Ordering:

- `sh.stack[0]` is the innermost active frame.

## 5.6 `sh.shared`

Mapping for shared-backed variables (see section 9).

## 6. Python -> Shell callbacks

## 6.1 `sh(*args)`

- runs shell command
- returns stdout string (strip trailing newline)
- non-zero raises `ShellCalledProcessError`

`ShellCalledProcessError` SHOULD expose:
- `.returncode`
- `.cmd`
- `.stdout`
- `.stderr`

## 6.2 `sh.run(...)`

Subprocess-style API returning `Completed` object:

- `.args`, `.returncode`, `.stdout`, `.stderr`

Supported args (minimum):
- `capture_output`
- `stdout`, `stderr` with `PIPE/STDOUT/DEVNULL`
- `check`
- `input`
- `shell`
- `cwd`
- `env`
- `timeout` (implement if possible; if not, fail explicitly/documented)

`check=True` non-zero MUST raise `ShellCalledProcessError`.

## 6.3 `sh.popen(...)`

Streaming process API:

- `.stdin`, `.stdout`, `.stderr`, `.pid`, `.returncode`
- `.poll()`, `.wait()`, `.communicate(input=None)`
- context manager support

## 7. Cross-language function bridge

## 7.1 Shell calls Python

Two paths:

1. explicit: `py func arg1 arg2`
2. optional ergonomic dispatch: unresolved shell command name maps to Python dotted callable (`a.b.c`)

Argument conversion SHOULD be predictable (strings by default; explicit coercion only where required).

## 7.2 Python calls shell function

- `sh.fn.name(args...)` executes shell function and returns captured stdout or raises on failure.

## 7.3 `from ... import ... as ...` shell syntax

Provide shell-native import wrapper creation for Python callables.

Examples to support:

- `from math import factorial`
- `from math import factorial as fac`
- `from ./file.py import greet`
- `from ./mod.py import "*"`

Generated wrappers MUST be real shell functions visible to function introspection (`declare -F` equivalent).

## 8. Ties (live two-way variable hooks)

## 8.1 Shell-initiated

- `py -t name`: tie shell var read/write through Python-backed hook
- `py -u name`: untie

## 8.2 Python-initiated

- `sh.tie(name, getter, setter=None, type=None)`
- `sh.untie(name)`

Types (ash mode):
- `scalar`, `integer`
- `array`, `assoc` are deferred to Bash-compat mode
- auto-detect if `type=None` SHOULD resolve only to in-scope ash-mode types

Reads invoke getter; writes invoke setter (if absent and write attempted -> error).

## 9. Shared variables

Provide shell builtin `shared` and Python mapping `sh.shared`.

Ash-mode baseline shell commands:
- `shared name=value`
- `shared name`
- `shared` (list all)

Deferred to Bash-compat mode:
- `shared -a name`
- `shared -A name`
- `shared -i name=0`
- `shared -d name`

Semantics:
1. Shared across subshells and pipeline elements.
2. Writes from one process become visible to others.
3. Backing may use shared memory region or a file-backed store with locking.

Compatibility-critical behavior:

```sh
shared x=0
(x=42)
echo "$x"   # must print 42
```

## 10. Status/return semantics summary

1. Shell command status communicates success/failure (`py`, `PYTHON`, generated wrappers).
2. Python callback APIs use exceptions for non-zero when configured (`check=True` or `sh()` always).
3. Structured exceptions (`-x`) expose machine-readable shell vars.

## 11. Parsing requirements

1. `PYTHON` block terminator detection occurs at shell parse level, not alias expansion tricks.
2. Block parser must not break on `)`/quotes inside Python body.
3. Redirections/pipelines attached to `PYTHON` command line must remain valid shell syntax.

## 12. Recommended conformance tests

Implement a test suite that verifies:

1. `py` modes: stmt, expr, callable, fd-source
2. `-v`/`-r` capture combinations
3. `-x` variable population
4. `PYTHON` block parse with nested `)`/quotes
5. `sh.vars/env/fn/stack/shared` CRUD + iteration
6. tie round-trip (shell write -> python read, python write -> shell read)
7. `sh()`/`run`/`popen` non-zero and `check` behavior
8. shared visibility across subshell/pipeline/background
9. import wrapper generation and invocation
10. SIGINT behavior (`130`)
