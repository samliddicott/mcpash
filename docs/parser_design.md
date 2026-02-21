# Parser Design Note (WIP)

This note captures how the parser/lexer should be structured to stay aligned
with the research in `research/parser/` and to map cleanly to the Oil/OSH ASDL.

## Goals
- A parser-driven lexer (token reader) with explicit parser context.
- A distinct word parser that builds word parts for later expansion.
- Parallel LST construction that maps to Oil/OSH ASDL/LST types.

## Background (Why this structure)
The POSIX shell spec and the Morbig paper show that shell lexing is
parsing-dependent: newlines, token boundaries, and reserved words depend on
parsing context and nesting. A standard regex-lexer + parser pipeline is not
enough; we need a prelexer that can be guided by the parser.

## Proposed Stages
1. **Token Reader (Prelexer)**
   - Input: raw source + parser context.
   - Output: tokens of `OP`, `WORD`, `HEREDOC`.
   - Responsibilities:
     - Newline significance (emit or ignore).
     - Reserved-word tagging (optional, context-sensitive).
     - Here-doc queueing and capture after delimiter parse.

2. **Word Parser**
   - Input: raw `WORD` text.
   - Output: structured word parts (literal, parameter, command subst, etc.).
   - Starts minimal (literal + `$var`) and grows to quotes/expansion rules.

3. **Grammar Parser**
   - Produces LST nodes in parallel to AST nodes.
   - LST types match Oil/OSH ASDL structure; AST can remain a simplified view.

## Key Constraints
- Reserved words are contextual (e.g., `in`, `do`, `then`).
- Newlines can be either token delimiters or whitespace depending on state.
- Here-doc bodies are parsed as a post-tokenization step and depend on delimiter
  quoting rules (`<<`, `<<-`, quoted delimiter).

## Next Steps
- Introduce a token reader layer that the parser drives.
- Add a minimal word parser for `$var` and `${var}`.
- Emit LST nodes alongside AST to align with Oil/OSH ASDL early.
