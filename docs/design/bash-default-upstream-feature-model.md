# Bash Default Upstream Feature Model

Date: 2026-03-11

Scope:

- Non-`--posix` upstream bash differential lane from
  `tests/compat/run_bash_default_upstream_matrix.sh`.
- Current failing core cases (14/14) in
  `docs/reports/bash-default-upstream-gap-latest.md`.

## Objective

Define per-feature runtime ownership, state model, invariants, and comparator
evidence before further implementation changes.

## Current Failing Features

1. `alias.tests`
2. `appendop.tests`
3. `arith.tests`
4. `array.tests`
5. `assoc.tests`
6. `builtins.tests`
7. `case.tests`
8. `comsub.tests`
9. `cond.tests`
10. `coproc.tests`
11. `errors.tests`
12. `exp.tests`
13. `exportfunc.tests`
14. `extglob.tests`

## Feature Models

### 1) Alias Expansion (`alias.tests`)

- Ownership:
  - `src/mctash/lexer.py` token stream integrity
  - `src/mctash/runtime.py` alias expansion (`_expand_aliases`)
  - parser command-position gating
- State model:
  - command-position token -> alias lookup -> replacement lex/parse -> continue
  - quoted/newline-heavy alias body must preserve lexical boundaries
- Invariants:
  - No alias expansion outside command position.
  - Alias expansion must not crash lexer/parser.
  - Unterminated alias text must surface shell diagnostic, never traceback.
- Comparator evidence:
  - upstream `alias.tests`
  - local lane: `run_bash_default_upstream_matrix.sh` / case `alias.tests`

### 2) Append Ops (`appendop.tests`)

- Ownership:
  - assignment parser + runtime typed assignment path
- State model:
  - lhs variable type discovery -> append coercion -> mutation
- Invariants:
  - `+=` respects scalar/indexed/assoc semantics.
  - Integer attributes coerce per bash arithmetic rules.
- Comparator evidence:
  - upstream `appendop.tests`

### 3) Arithmetic (`arith.tests`)

- Ownership:
  - parser (arith syntactic forms) + runtime evaluator
- State model:
  - distinguish `(( ))`, `$(( ))`, `let`, `for (( ; ; ))`
- Invariants:
  - Syntax errors and runtime arithmetic errors map to bash statuses.
  - Nested/empty forms do not desynchronize parse context.
- Comparator evidence:
  - upstream `arith.tests`

### 4) Indexed Arrays (`array.tests`)

- Ownership:
  - variable store + expansion engine
- State model:
  - declared indexed array -> element mutation -> expansion projection
- Invariants:
  - `${a[@]}` vs `${a[*]}` quote behavior matches bash.
  - Sparse indices and unset elements retain bash-observable behavior.
- Comparator evidence:
  - upstream `array.tests`

### 5) Assoc Arrays (`assoc.tests`)

- Ownership:
  - assoc variable store + subscript evaluator + expansion
- State model:
  - key expression -> string-key resolution -> map read/write/unset
- Invariants:
  - Key evaluation is string-oriented for assoc vars.
  - Assoc print ordering is treated non-contractual unless a test requires order.
- Comparator evidence:
  - upstream `assoc.tests`

### 6) Builtins Universe (`builtins.tests`)

- Ownership:
  - builtin dispatch + option parser + state mutation
- State model:
  - parse builtin options -> mutate shell/runtime state -> status/diagnostics
- Invariants:
  - Special builtin error semantics and continuation rules match bash mode.
  - Diagnostics use shell path, not Python exception surface.
- Comparator evidence:
  - upstream `builtins.tests`

### 7) Case Grammar (`case.tests`)

- Ownership:
  - parser case production + pattern runtime matching
- State model:
  - `case WORD [sep] in` -> pattern items -> action list -> `;;`/`esac` close
- Invariants:
  - Newline/semicolon separators before `in` are accepted as in bash.
  - Empty/invalid items fail with shell parse diagnostics.
- Comparator evidence:
  - upstream `case.tests`

### 8) Command Substitution (`comsub.tests`)

- Ownership:
  - word parser + substitution evaluator + nested parse context
- State model:
  - parse `$()` subtree -> eval subcommand -> capture -> trim -> substitute
- Invariants:
  - Nested substitutions preserve parser context and line accounting.
  - Output trimming/field behavior matches bash mode.
- Comparator evidence:
  - upstream `comsub.tests`

### 9) Conditional Expressions (`cond.tests`)

- Ownership:
  - parser/runtime for `[[ ... ]]`
- State model:
  - tokenize conditional operators -> evaluate in conditional mode
- Invariants:
  - Operator precedence and regex/pattern semantics match bash.
  - Expansion behavior differs correctly from `[` builtin rules.
- Comparator evidence:
  - upstream `cond.tests`

### 10) Coprocess (`coproc.tests`)

- Ownership:
  - runtime process/job management + fd plumbing
- State model:
  - spawn coproc job -> create endpoint fds -> maintain lifecycle + wait
- Invariants:
  - No deadlock/hang on coproc orchestration paths.
  - Coproc status/FD visibility matches bash-observable behavior.
- Comparator evidence:
  - upstream `coproc.tests`

### 11) Error Semantics (`errors.tests`)

- Ownership:
  - parser/lexer/runtime error normalization + diagnostics
- State model:
  - detect error -> normalize text/status -> emit -> continue/abort as required
- Invariants:
  - No Python traceback in user-visible stderr.
  - Exit status class matches bash category (syntax/runtime/not found/etc.).
- Comparator evidence:
  - upstream `errors.tests`

### 12) Expansion Core (`exp.tests`)

- Ownership:
  - expansion pipeline engine
- State model:
  - brace -> tilde -> parameter -> command -> arithmetic -> split -> glob
- Invariants:
  - Expansion ordering and quoting boundaries match bash default mode.
  - Guarded legacy fallbacks are reduced and behaviorally equivalent.
- Comparator evidence:
  - upstream `exp.tests`

### 13) Function Export (`exportfunc.tests`)

- Ownership:
  - env marshalling + function serialization/import policy
- State model:
  - function export request -> env encoding -> child/import behavior
- Invariants:
  - Exported functions appear in expected scope with bash-compatible behavior.
  - Invalid encodings fail with shell diagnostics, not crashes.
- Comparator evidence:
  - upstream `exportfunc.tests`

### 14) Extended Globs (`extglob.tests`)

- Ownership:
  - parser extglob grammar + matcher + shopt mode toggles
- State model:
  - extglob enabled/disabled -> parse pattern -> match expansion/runtime tests
- Invariants:
  - `shopt -s/-u extglob` consistently gates parse+match behavior.
  - Nested extglob forms behave per bash default mode.
- Comparator evidence:
  - upstream `extglob.tests`

## Implementation Tranche Order

1. Parser/diagnostic safety tranche:
   - `alias.tests`, `case.tests`, `comsub.tests`, `errors.tests`
2. Expansion grammar/eval tranche:
   - `exp.tests`, `arith.tests`, `extglob.tests`
3. Data-model tranche:
   - `array.tests`, `assoc.tests`, `appendop.tests`
4. Runtime/process/builtin tranche:
   - `cond.tests`, `coproc.tests`, `builtins.tests`, `exportfunc.tests`

## Design Deltas From Evidence

- 2026-03-11:
  - Added lexer error catch path in `main.py` to prevent traceback leaks in
    upstream default lane.
  - Adjusted `case` parser to accept separators before `in`.
  - Established dedicated default-mode upstream gate/report to drive feature
    closure without conflating with `--posix` lane.

