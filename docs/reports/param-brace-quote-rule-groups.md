# Parameter Brace/Quote Rule Groups

Source corpus: `docs/reports/param-brace-quote-edge-matrix-latest.md`

This file groups edge rows into parser/execution rule classes so fixes can be done in deterministic order.

## Group G0: Shell Defaults / Pre-parse Preconditions

- Symptom: `${IFS+word}` rows collapse to empty output when `IFS` is not explicitly set.
- Rows: `E002`, `E003`, `E004`, `E006`, `E007`, `E008`, `E010`, `E011`, `E012`, `E013`, `E014`, `E015`.
- Required behavior:
  - POSIX shell startup initializes `IFS` to `<space><tab><newline>`.
  - Parameter operators that depend on “set/unset” (`+`, `:+`, `-`, `:-`) observe that default.
- Fix point:
  - Runtime initialization (`Runtime.__init__`).

## Group G1: `${...}` Brace-Close Eligibility Under Mixed Quotes

- Symptom: scanner closes too early or too late around `}` when quote-state toggles are ambiguous.
- Rows: `E002`, `E003`, `E004`, `E005`, `E014`, `E015`.
- Required behavior:
  - `}` closes current `${...}` only when current lexical state permits closure.
  - Unmatched quote characters in operator-word contexts must not necessarily poison the remainder of the command.
- Fix point:
  - Lexer `${...}` scanner (`_scan_braced_sub`).

## Group G2: Operator Word Content Semantics (Nested Substitutions)

- Symptom: operator word loses nested content (expands to empty or truncated fields).
- Rows: `E006`, `E007`, `E008`, `E012`, `E013`.
- Required behavior:
  - `${name+word}` preserves command substitution and nested `${...}` behavior in `word`.
  - line-continuations inside operator words keep shell-consistent logical tokens.
- Fix points:
  - Lexer capture of whole `${...}` span.
  - Runtime expansion of braced operator argument words.

## Group G3: Malformed Form Detection/Classification

- Symptom: mismatch in rc/error class for malformed forms (`bad substitution`, unterminated quotes).
- Rows: `E016`, `E017`, `E018`, and later `posixexp.tests` tail failures.
- Required behavior:
  - Error class (parse-vs-expansion and non-zero status) should match bash-posix behavior envelope.
  - Exact wording can remain style-dependent (`ash`/`bash`) but class and timing should align.
- Fix points:
  - Lexer hard-fail conditions vs deferred expansion errors.
  - Runtime `bad substitution` classification.

## Group G4: Quote Characters as Data in Replacement/Pattern Context

- Symptom: mismatches where quote glyphs should survive as data inside pattern/removal operators.
- Rows: `E009` (already parity), plus relevant `posixexp*` follow-on cases.
- Required behavior:
  - Preserve quote chars as data where syntax permits.
  - Do not re-tokenize replacement/pattern mini-languages as full shell grammar.
- Fix points:
  - Structured arg handling in braced parameter operator path.

## Fix Order

1. `G0` (default env correctness): remove false negatives immediately.
2. `G1` (brace-close/quote-state): stabilize lexer token boundaries.
3. `G2` (nested word semantics): restore operator-word content behavior.
4. `G3` (malformed classification): align rc/error timing envelope.
5. `G4` (quote-as-data consistency): close remaining semantic tails.
