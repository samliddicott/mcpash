# OSH ASDL Adoption Checklist

Status: strict OSH-first migration in progress.

## Canonical Schema

Adopted canonical files:

- `src/syntax/osh/syntax.asdl`
- `src/syntax/osh/types.asdl`
- `src/syntax/osh/runtime.asdl`
- `src/syntax/osh/value.asdl`

## Parser Output Path (Current)

1. Parse source -> LST (`src/mctash/parser.py`)
2. LST -> OSH-shaped ASDL mapping (`src/mctash/asdl_map.py`, strict mode)
3. OSH-shaped ASDL -> runtime AST adapter (`src/mctash/osh_adapter.py`)
4. Execute via existing interpreter (`src/mctash/runtime.py`)

This makes OSH-shaped ASDL the mandatory intermediate representation in execution paths.

## Implemented command.* mappings

- `command.CommandList`
- `command.AndOr`
- `command.Pipeline`
- `command.Simple`
- `command.Redirect`
- `command.BraceGroup`
- `command.If`
- `command.WhileUntil`
- `command.ShFunction`
- `command.Subshell`
- `command.ForEach`
- `command.Case`
- `command.ControlFlow`
- `command.ShAssignment`
- `command.Sentence`

## Strictness Guard

- Strict mapper raises on fallback `command.NoOp`.
- This prevents silently executing parser shapes that are not represented in OSH mapping.

## Remaining gaps to full native OSH adoption

- Replace dict-based mapping with generated typed nodes from OSH ASDL.
- Remove adapter back to legacy runtime AST; execute OSH nodes directly.
- Complete missing word_part and redirection variants from OSH syntax.
- Expand grammar coverage until strict mapping never encounters unsupported variants for target corpus.
