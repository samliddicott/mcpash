# 001: Milestone 1 PoC — Python 3 Ash

## Goal
Deliver a Python 3 proof-of-concept shell that is **ash-compliant enough to pass `ash-shell/test`**, using a real lexer, parser, and executor.

## Scope (PoC)
- Non-interactive execution (run scripts, read stdin).
- Core command language: simple commands, pipelines, lists (`;`, `&&`, `||`), subshells `(...)`, grouping `{ ...; }`, functions.
- Redirections: `<`, `>`, `>>`, `<<`, `<<-`, `>&`, `<&` (as required by tests).
- Word expansions: parameter expansion, command substitution, arithmetic expansion, field splitting, pathname expansion, quote removal (as required by tests).
- Minimal builtin set to satisfy the test suite.

## References (Spec Guidance)
- POSIX Shell Command Language (tokenization, grammar, expansions, redirections, pipelines). Source: `https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html`.
- `dash` man page (ash-like behavior, reserved words, expansions, redirections). Source: `https://manpages.debian.org/bookworm/dash/dash.1.en.html`.
- Ash test framework (acceptance target). Source: `https://github.com/ash-shell/test` (README via raw GitHub).

## Architecture Overview
### Lexer
- **Two-phase tokenization** guided by POSIX rules:
  1. Character-level scanning to recognize operators vs words.
  2. Token classification (reserved words, assignment words, IO numbers) based on parser context.
- **Lexer modes** (per POSIX and shell reality):
  - `NORMAL`: unquoted token recognition, operators, words, reserved words.
  - `SINGLE_QUOTE`: literal mode until `'`.
  - `DOUBLE_QUOTE`: allow `$` expansions and backslash escapes.
  - `COMMAND_SUBST`: parse `$()` with nested balancing.
  - `ARITH`: parse `$(( ))` with nested parentheses.
  - `HERE_DOC`: deferred reading after `<<` / `<<-` delimiter resolution.
- **Operator tokens**: `|`, `||`, `&`, `&&`, `;`, `(`, `)`, `{`, `}`, `
`, redirection operators.

### Parser
- Recursive descent parser using POSIX shell grammar as the guide.
- Parser responsibilities:
  - Build a minimal AST: `CommandList`, `AndOr`, `Pipeline`, `SimpleCommand`, `Assignment`, `Redirect`, `FunctionDef`, `Subshell`, `Group`, `If`, `While`, `Until`, `For`, `Case` (add only if needed by tests).
  - Convert `WORD` tokens into `ASSIGNMENT_WORD` and reserved words based on grammar position.
  - Attach redirections to the correct command nodes.

### Expander
- Implement expansion phases in POSIX order:
  1. Tilde expansion
  2. Parameter expansion
  3. Command substitution
  4. Arithmetic expansion
  5. Field splitting
  6. Pathname expansion
  7. Quote removal
- Use explicit AST nodes for words, with sub-parts that preserve quoting and substitution boundaries.

### Executor
- Tree-walk interpreter:
  - **SimpleCommand**: apply assignments, expand words, then resolve to builtin/function/external.
  - **Pipeline**: connect subprocess pipes; capture status of last command.
  - **Lists**: `&&` / `||` short-circuit based on exit status.
  - **Subshell**: fork a new process context with separate environment and positional parameters.
  - **Group**: execute in current environment.
- Redirections applied before command execution (and restored after for builtins/functions).

## Implementation Plan
### Step 1: Skeleton & Inputs
- CLI entry point: `mctash <script>` or stdin.
- Read input into a single buffer with line tracking.
- Add minimal error reporting (line/column).

### Step 2: Lexer Core
- Implement operator recognition and word scanning.
- Implement single and double quote handling.
- Implement here-doc collection after the parse stage determines delimiters.

### Step 3: Parser Core
- Implement grammar for:
  - `command_list` / `and_or` / `pipeline` / `simple_command`.
  - function definitions `name() { ...; }`.
  - `if` / `while` / `until` as needed.
- Produce AST nodes with stable structure for execution.

### Step 4: Expansions
- Parameter expansion `${var}` and `$var`.
- Command substitution `$()` with nested parsing.
- Arithmetic expansion `$((...))` (start with integer-only).
- Field splitting on IFS, pathname expansion via `glob`.

### Step 5: Executor
- Builtins: start minimal and grow based on `ash-shell/test` failures.
- External commands via `subprocess`.
- Pipeline and redirection mechanics with `os.pipe`, `os.dup2`.

### Step 6: Ash Test Suite Integration
- Wire test runner to execute `ash-shell/test`.
- Iterate on failures to fill gaps in grammar, expansion, and builtins.

## Commencement Proposal
1. **Define a minimal AST** and token set aligned with POSIX shell grammar.
2. Implement lexer and parser for simple commands + pipelines + lists.
3. Add a minimal executor with `echo`, `cd`, `exit`, `:` and external execution.
4. Begin running `ash-shell/test`, expanding builtins and grammar as failures demand.

## Risks
- Token classification is context-sensitive and easy to mis-handle.
- Here-doc parsing requires deferring body capture until after delimiter parsing.
- Bash/ash quirks may require targeted compatibility hacks.
