# Parser Research Notes

This directory tracks parser/lexer research relevant to mctash and summarizes
how those sources affect our design.

## Sources
- `research/parser/sources/regis_gianas_pps2018.pdf`
- `research/parser/sources/fosdem_posix_shell_parsing.pdf`
- `research/parser/sources/sciencedirect_shell_parsing.pdf`
- `research/parser/sources/lobsters_formally_verified_shell.html`
- `research/parser/osh_syntax/` (Oil/OSH ASDL/LST files, Apache 2.0)
- `research/parser/mrsh/` (mrsh parser sources, MIT)

## Key Findings
- POSIX shell lexing is parsing-dependent. Newlines, reserved words, and token
  boundaries depend on parser state and nesting (quotes, substitutions, here-docs).
- The usual "regex lexer then parser" pipeline is not sufficient; a prelexer
  that cooperates with the parser is needed for reliable token recognition.
- Word parsing (quote/expansion structure) is its own problem and should be
  separated from pretokenization.
- Here-doc capture must be triggered by parsing (redirection operators and
  their delimiters), not by reading stdin opportunistically.
- Some constructs are inherently dynamic (alias/eval). Static parsing needs a
  defined subset and explicit rules for what is rejected or deferred to runtime.
- Using an ASDL/LST (from Oil/OSH) gives a stable target shape for the parse
  tree and reduces ambiguity about what structures we should emit.

## Design Implications (for mctash)
- Build a token reader that accepts parser context (reserved words, newline
  significance) and maintains a here-doc queue.
- Split word parsing into a dedicated phase that produces word parts.
- Parse into LST nodes alongside the current AST, then convert LST -> AST
  as the implementation matures.

## Coverage Report
- `research/parser/asdl_coverage.py` generates a status report against the
  Oil/OSH ASDL: `research/parser/asdl_coverage_report.md`.
