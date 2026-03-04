# mctash Lexer Modes and Context Rules

This is the companion specification to `docs/specs/mctash-grammar.ebnf`.

Purpose:

- Define context-sensitive lexical behavior that EBNF alone cannot encode.
- Stabilize tokenization/closure behavior for tricky shell constructs.
- Provide explicit contracts for parser + ASDL mapping.

Primary implementation anchors:

- `src/mctash/lexer.py` (`TokenReader`, `_scan_braced_sub`, command/arith/backtick scanners)
- `src/mctash/parser.py` (`LexContext`, heredoc queue handling, reserved-word dispatch)

## 1. Core Modes

Mode stack (conceptual):

1. `PLAIN` (default command lexing)
2. `SINGLE_QUOTE`
3. `DOUBLE_QUOTE`
4. `BRACED_PARAM` (`${...}` scanner context)
5. `COMMAND_SUB` (`$(...)`)
6. `ARITH_SUB` (`$((...))`)
7. `BACKTICK_SUB` (`` `...` ``)
8. `HEREDOC_BODY` (captured post-newline from pending queue)

State data carried alongside mode:

- line/column/index
- nested depth (`${...}`, `$(...)`, arithmetic depth)
- heredoc pending queue (delimiter, strip-tabs, quoted-delimiter flag)
- parser context flags (`allow_reserved`, `allow_newline`)

## 2. Token Classes

Top-level tokens produced for parser:

- `WORD`
- `RESERVED` (contextualized by parser-provided reserved set + command position)
- `OP` (operators, separators, grouping tokens)
- `HEREDOC` (queued body token, with quoted/strip metadata)

## 3. Reserved Words and Alias Interaction

Rules:

- Reserved words are recognized only when `allow_reserved=true` and command-position rules permit.
- Alias expansion occurs in parser stage and may inject syntax-relevant tokens.
- Syntax-affecting alias expansion is attempted before compound-command dispatch.

## 4. Newline and Separator Significance

Rules:

- Newline can be either tokenized as `OP("\n")` or consumed as whitespace depending on parser context.
- Newline is significant for:
  - list terminators,
  - heredoc capture start,
  - certain parse recovery/error boundaries.

## 5. Comment Eligibility (`#`)

Rules:

- `#` starts a comment in unquoted command context when lexically eligible.
- Inside quoted or substitution contexts, `#` is data unless grammar context explicitly re-enters comment eligibility.
- Incorrect quote-state transitions around `${...}` can wrongly classify trailing `#`; this is a tracked parity-sensitive area (`E005` class).

## 6. `${...}` Closure Rules (Critical)

Contract:

- The lexer must return the full lexical span of braced parameter substitution as one word-part chunk boundary.
- `}` closes current `${...}` only when:
  - nested `${...}` depth reaches zero, and
  - current quote-mode permits brace closure.

Quote handling requirements in `BRACED_PARAM`:

- Track quote state transitions robustly for single and double quote glyphs in operator-word content.
- Support nested command/arithmetic/backtick substitutions inside braced operator words.
- Distinguish literal quote characters from quote delimiters where shell semantics require it.

Known edge corpus:

- `docs/reports/param-brace-quote-edge-matrix-latest.md`
- `docs/reports/param-brace-quote-rule-groups.md`

## 7. Heredoc Queue and Capture

Rules:

- `<<` / `<<-` records pending heredoc descriptors during command lex/parse.
- Delimiter quoting is tracked at delimiter-token time.
- Capture occurs after the controlling newline boundary, not by consuming parser stdin token stream ad-hoc.
- Body expansion policy depends on quoted delimiter flag.

## 8. Escape and Line Continuation

Rules:

- Backslash-newline joins physical lines in contexts where continuation applies.
- In double quotes, only the standard escaped set is special (`\"`, `\\`, `\$`, ``\` ``, and newline continuation).
- In single quotes, backslash has no escape semantics for quote termination.

## 9. Error Classes

Lexical errors:

- unterminated quoted string
- missing block terminator for verbatim block capture

Parser errors:

- missing expected separators/terminators (`)`, `fi`, `done`, etc.)
- unexpected token in context

Expansion/runtime errors:

- bad substitution
- unbound variable diagnostics

Constraint:

- Error class/timing should match comparator behavior envelopes (`ash`, `bash --posix`) for in-scope rows.

## 10. Spec Update Rule

Whenever parser/lexer behavior changes for a syntax edge case:

1. Update this file with the rule delta.
2. Update `docs/specs/mctash-grammar.ebnf` if production-level shape changed.
3. Add/update case evidence in matrix or corpus report.
