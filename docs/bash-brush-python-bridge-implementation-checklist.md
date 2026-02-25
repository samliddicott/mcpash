# Shell/Brush <-> Python Bridge: Implementation Checklist Matrix

This companion document turns the bridge spec into a phased build checklist.

Status values you can use while implementing:


## Naming baseline

- Canonical API object in new code/tests: `sh`
- Compatibility alias to support legacy scripts: `bash`

All checklist rows should be implemented as `sh.*` and mirrored via `bash.*` alias.

- `todo`
- `in-progress`
- `done`
- `deferred`

## Phase 1: Shell entry points and status model

| Feature | Required behavior | Conformance tests | Implementation hints | Status |
|---|---|---|---|---|
| `py` statement execution | Execute inline Python statements | `py 'print("ok")'` prints `ok`; status `0` | Keep persistent Python runtime + globals | done |
| `py -e` | Evaluate expression and print result text | `py -e '1+2'` -> `3` | Route through eval path | done |
| `-v VAR` stdout capture | Capture stdout to shell var and suppress terminal output | Python print lands in var | Redirect Python stdout to buffer | done |
| `-r VAR` return capture | Capture callable/expr result in shell var | result lands in var | stringify with stable policy (`repr`/string) | done |
| Exit status contract | `0` success, `1` exception, `130` interrupt | unit tests for each path | map runtime exceptions to shell status | done |
| `-x` structured exceptions | Populate `PYTHON_EXCEPTION*` vars instead of traceback | validate all 4 vars + status | convert traceback frames into shell array | done |

## Phase 2: `PYTHON ... END_PYTHON` parser integration

| Feature | Required behavior | Conformance tests | Implementation hints | Status |
|---|---|---|---|---|
| Block parsing | Zero-indented `END_PYTHON` terminator | multiline code with `)` and quotes | parser-level block collection, not alias tricks | done |
| Dedent default | Dedent enabled by default | indented block executes | use textwrap-like dedent rules | done |
| `--no-dedent` | Preserve raw indentation | indented block fails/preserves as expected | add per-command option flag | done |
| Same-line options | `PYTHON -x -r out` works | capture + structured exception tests | reuse `py` option parser | done |
| Shell syntax integration | redirection and pipeline still valid | `PYTHON 2>e`; `echo x | PYTHON | cat` | treat block command as normal command node | done |

## Phase 3: Injected `sh` object core mappings

| Feature | Required behavior | Conformance tests | Implementation hints | Status |
|---|---|---|---|---|
| `sh.vars` mapping | live get/set/del/iter/contains/len | CRUD and iteration tests | map directly to shell var store APIs | done |
| `sh.env` mapping | exported env view with set+export on write | read exported vars; write exports | filter by export attr | done |
| attrs/declare APIs | attrs read/write and declare flags | integer/readonly/exported flag tests | use shell declare internals | done |
| type conversion | list->array, dict->assoc, scalar->scalar | roundtrip for each type | canonical conversion helpers | in-progress |

## Phase 4: Function bridge and import wrappers

| Feature | Required behavior | Conformance tests | Implementation hints | Status |
|---|---|---|---|---|
| `sh.fn` map | get/set/del/iter/contains | body read/write/delete tests | hook into shell function table | done |
| `sh.fn.call` | callable namespace invocation | `sh.fn.foo("x")` returns stdout | invoke shell func with captured stdout | done |
| callable assignment | Python callable -> shell wrapper | assigned callable callable from shell | wrapper delegates to `py` callable path | done |
| `from ... import ... as ...` | create shell wrappers from module/file imports | alias and wildcard examples | parse command and generate shell function defs | done |

## Phase 5: Callback APIs (`sh`, `run`, `popen`)

| Feature | Required behavior | Conformance tests | Implementation hints | Status |
|---|---|---|---|---|
| `sh()` | run shell command, return stdout, raise on non-zero | success + failure metadata tests | lightweight wrapper over run/check/capture | done |
| `sh.run()` core | completed object with args/returncode/stdout/stderr | check modes + capture flags | model after `subprocess.run` | done |
| `check=True` | raise `ShellCalledProcessError` on non-zero | exit 7 raises | include returncode/cmd/stdout/stderr | done |
| stdio routing | support PIPE/STDOUT/DEVNULL | routing correctness tests | normalize stream config object | done |
| `sh.popen()` | process handle with poll/wait/communicate + context manager | lifecycle tests | retain child handle + IO endpoints | done |

## Phase 6: Ties (two-way live hooks)

| Feature | Required behavior | Conformance tests | Implementation hints | Status |
|---|---|---|---|---|
| `py -t/-u` | shell-side tie and untie | shell write reflected in Python, and reverse | install/remove variable hooks | done |
| `sh.tie/untie` | python-side getter/setter ties | getter invoked on read, setter on write | tie registry keyed by var name | done |
| tie types | `scalar`, `integer`, `array`, `assoc`, auto-detect | each tie type roundtrip | explicit converters per tie type | in-progress |

## Phase 7: Shared variables

| Feature | Required behavior | Conformance tests | Implementation hints | Status |
|---|---|---|---|---|
| `shared` builtin | create/read/update/delete typed shared vars | scalar/array/assoc/integer tests | shared backend + shell builtin wiring | in-progress |
| `sh.shared` mapping | Python access to shared backend | read/write/delete from Python | expose same storage via mapping API | done |
| fork visibility | subshell/pipeline/background see same value | `(x=42)` after `shared x=0` -> `42` | shared memory + locking recommended | done |

## Phase 8: Stack and diagnostics

| Feature | Required behavior | Conformance tests | Implementation hints | Status |
|---|---|---|---|---|
| `sh.stack` | iterable frames with source/lineno/funcname | stack depth and field validity tests | expose current shell frame list read-only | done |
| traceback frame shaping | `PYTHON_EXCEPTION_TB[]` useful frame strings | compare expected frame entries | normalize format once and document it | done |

## Phase 9: Parser hardening and edge compatibility

| Feature | Required behavior | Conformance tests | Implementation hints | Status |
|---|---|---|---|---|
| block robustness | `)`/quotes inside Python body do not terminate shell parse | regression fixtures | dedicated embedded-block lexer state | done |
| command substitution interaction | status and output semantics stable inside `$()` | `$({ PYTHON ...; })` style tests | ensure command node behavior is consistent | done |
| interrupt path | SIGINT returns `130` and unwinds cleanly | ctrl-c integration tests | map interrupts distinctly from exceptions | done |

## Phase 10: Compatibility suite and release gate

| Feature | Required behavior | Conformance tests | Implementation hints | Status |
|---|---|---|---|---|
| bridge conformance suite | all sections above covered by automated tests | CI matrix across OS/Python versions | group tests by feature area | in-progress |
| docs parity | user docs align with actual behavior | doc snippets run as tests where possible | use doctest-style harness for examples | in-progress |
| known limitations register | explicit list of deferred items | release note includes deferred list | keep a single source-of-truth doc table | done |

## Minimum acceptance gate

Before declaring bridge parity baseline complete:

1. All Phase 1-4 rows are `done`.
2. At least one end-to-end test covers each of Phases 5-8.
3. `PYTHON ... END_PYTHON` parse regressions are gated in CI.
4. Structured exception variables and status code behavior are documented and tested.
5. Shared visibility across subshell/pipeline is demonstrated by automated tests.

Known limitations register: `docs/bridge-limitations.md`.
Requirement-to-test trace: `docs/bridge-test-trace.md`.
