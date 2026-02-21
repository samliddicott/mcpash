# Mctash LST (Lossless Syntax Tree) Notes

The LST captures **lossless** source details (whitespace, comments, exact syntax) while still structuring code for analysis and translation. The PoC does not yet implement LST, but this file defines the intent and shape.

## Design Intent
- Preserve *original source text* via span references.
- Attach span IDs to significant tokens (operators, words) in the AST.
- Keep all original text reconstructible without reformatting.

## Proposed Shape (Sketch)
- `Arena`: list of spans that concatenate to the original input.
- AST nodes reference span IDs for significant tokens.
- Non-significant spans (whitespace/comments) are preserved in the arena only.

## Next Steps
- Define a span representation aligned with the lexer.
- Annotate AST nodes with span IDs.
- Build round-trip tests to ensure lossless reconstruction.
