# Bash/Brush <-> Python Bridge: Implementation Checklist Matrix

This companion document turns the bridge spec into a phased build checklist.

Status values you can use while implementing:

- `todo`
- `in-progress`
- `done`
- `deferred`

## Phase 1: Shell entry points and status model

| Feature | Required behavior | Conformance tests | Implementation hints | Status |
|---|---|---|---|---|
| `py` statement execution | Execute inline Python statements | `py 'print("ok")'` prints `ok`; status `0` | Keep persistent Python runtime + globals | todo |
| `py -e` | Evaluate expression and print result text | `py -e '1+2'` -> `3` | Route through eval path | todo |
| `-v VAR` stdout capture | Capture stdout to shell var and suppress terminal output | Python print lands in var | Redirect Python stdout to buffer | todo |
| `-r VAR` return capture | Capture callable/expr result in shell var | result lands in var | stringify with stable policy (`repr`/string) | todo |
| Exit status contract | `0` success, `1` exception, `130` interrupt | unit tests for each path | map runtime exceptions to shell status | todo |
| `-x` structured exceptions | Populate `MCBASH_EXCEPTION*` vars instead of traceback | validate all 4 vars + status | convert traceback frames into shell array | todo |

## Phase 2: `PYTHON ... END_PYTHON` parser integration

| Feature | Required behavior | Conformance tests | Implementation hints | Status |
|---|---|---|---|---|
| Block parsing | Zero-indented `END_PYTHON` terminator | multiline code with `)` and quotes | parser-level block collection, not alias tricks | todo |
| Dedent default | Dedent enabled by default | indented block executes | use textwrap-like dedent rules | todo |
| `--no-dedent` | Preserve raw indentation | indented block fails/preserves as expected | add per-command option flag | todo |
| Same-line options | `PYTHON -x -r out` works | capture + structured exception tests | reuse `py` option parser | todo |
| Shell syntax integration | redirection and pipeline still valid | `PYTHON 2>e`; `echo x | PYTHON | cat` | treat block command as normal command node | todo |

## Phase 3: Injected `bash` object core mappings

| Feature | Required behavior | Conformance tests | Implementation hints | Status |
|---|---|---|---|---|
| `bash.vars` mapping | live get/set/del/iter/contains/len | CRUD and iteration tests | map directly to shell var store APIs | todo |
| `bash.env` mapping | exported env view with set+export on write | read exported vars; write exports | filter by export attr | todo |
| attrs/declare APIs | attrs read/write and declare flags | integer/readonly/exported flag tests | use shell declare internals | todo |
| type conversion | list->array, dict->assoc, scalar->scalar | roundtrip for each type | canonical conversion helpers | todo |

## Phase 4: Function bridge and import wrappers

| Feature | Required behavior | Conformance tests | Implementation hints | Status |
|---|---|---|---|---|
| `bash.fn` map | get/set/del/iter/contains | body read/write/delete tests | hook into shell function table | todo |
| `bash.fn.call` | callable namespace invocation | `bash.fn.foo("x")` returns stdout | invoke shell func with captured stdout | todo |
| callable assignment | Python callable -> shell wrapper | assigned callable callable from shell | wrapper delegates to `py` callable path | todo |
| `from ... import ... as ...` | create shell wrappers from module/file imports | alias and wildcard examples | parse command and generate shell function defs | todo |

## Phase 5: Callback APIs (`bash`, `run`, `popen`)

| Feature | Required behavior | Conformance tests | Implementation hints | Status |
|---|---|---|---|---|
| `bash()` | run shell command, return stdout, raise on non-zero | success + failure metadata tests | lightweight wrapper over run/check/capture | todo |
| `bash.run()` core | completed object with args/returncode/stdout/stderr | check modes + capture flags | model after `subprocess.run` | todo |
| `check=True` | raise `BashCalledProcessError` on non-zero | exit 7 raises | include returncode/cmd/stdout/stderr | todo |
| stdio routing | support PIPE/STDOUT/DEVNULL | routing correctness tests | normalize stream config object | todo |
| `bash.popen()` | process handle with poll/wait/communicate + context manager | lifecycle tests | retain child handle + IO endpoints | todo |

## Phase 6: Ties (two-way live hooks)

| Feature | Required behavior | Conformance tests | Implementation hints | Status |
|---|---|---|---|---|
| `py -t/-u` | shell-side tie and untie | shell write reflected in Python, and reverse | install/remove variable hooks | todo |
| `bash.tie/untie` | python-side getter/setter ties | getter invoked on read, setter on write | tie registry keyed by var name | todo |
| tie types | `scalar`, `integer`, `array`, `assoc`, auto-detect | each tie type roundtrip | explicit converters per tie type | todo |

## Phase 7: Shared variables

| Feature | Required behavior | Conformance tests | Implementation hints | Status |
|---|---|---|---|---|
| `shared` builtin | create/read/update/delete typed shared vars | scalar/array/assoc/integer tests | shared backend + shell builtin wiring | todo |
| `bash.shared` mapping | Python access to shared backend | read/write/delete from Python | expose same storage via mapping API | todo |
| fork visibility | subshell/pipeline/background see same value | `(x=42)` after `shared x=0` -> `42` | shared memory + locking recommended | todo |

## Phase 8: Stack and diagnostics

| Feature | Required behavior | Conformance tests | Implementation hints | Status |
|---|---|---|---|---|
| `bash.stack` | iterable frames with source/lineno/funcname | stack depth and field validity tests | expose current shell frame list read-only | todo |
| traceback frame shaping | `MCBASH_EXCEPTION_TB[]` useful frame strings | compare expected frame entries | normalize format once and document it | todo |

## Phase 9: Parser hardening and edge compatibility

| Feature | Required behavior | Conformance tests | Implementation hints | Status |
|---|---|---|---|---|
| block robustness | `)`/quotes inside Python body do not terminate shell parse | regression fixtures | dedicated embedded-block lexer state | todo |
| command substitution interaction | status and output semantics stable inside `$()` | `$({ PYTHON ...; })` style tests | ensure command node behavior is consistent | todo |
| interrupt path | SIGINT returns `130` and unwinds cleanly | ctrl-c integration tests | map interrupts distinctly from exceptions | todo |

## Phase 10: Compatibility suite and release gate

| Feature | Required behavior | Conformance tests | Implementation hints | Status |
|---|---|---|---|---|
| bridge conformance suite | all sections above covered by automated tests | CI matrix across OS/Python versions | group tests by feature area | todo |
| docs parity | user docs align with actual behavior | doc snippets run as tests where possible | use doctest-style harness for examples | todo |
| known limitations register | explicit list of deferred items | release note includes deferred list | keep a single source-of-truth doc table | todo |

## Minimum acceptance gate

Before declaring bridge parity baseline complete:

1. All Phase 1-4 rows are `done`.
2. At least one end-to-end test covers each of Phases 5-8.
3. `PYTHON ... END_PYTHON` parse regressions are gated in CI.
4. Structured exception variables and status code behavior are documented and tested.
5. Shared visibility across subshell/pipeline is demonstrated by automated tests.
