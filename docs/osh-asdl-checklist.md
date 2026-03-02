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
3. Execute command lists directly from OSH-shaped ASDL in runtime (`src/mctash/runtime.py`)
4. Use legacy AST compatibility only where explicit fallback remains (`src/mctash/runtime.py`)

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

## Guarded Native Expansion Coverage (Current)

Native (guarded) paths with parity evidence:

- `argv`:
  - literal-only words
  - single-quoted parts
  - safe scalar `$name` subset
  - safe scalar `${name...}` subset
- `case`:
  - safe scalar value/pattern words (`Literal`, `SingleQuoted`, `SimpleVarSub`, constrained `BracedVarSub`)
- `assignment rhs`:
  - literal/single-quoted parts
  - arithmetic and command substitution
  - safe scalar braced-operator subset
- `redirection target`:
  - guarded native scalar path using ASDL `target_word` metadata
  - fallback preserved for unsafe forms

Guarded fallback remains required for:

- `argv` words that can trigger nuanced IFS splitting/globbing/quote-removal differences
- command/arithmetic/process-substitution forms in contexts where parity has not yet been proven
- complex braced operators and mutation forms where ash behavior still needs side-by-side evidence

## Remaining gaps to full native OSH adoption

- Replace dict-based mapping with generated typed nodes from OSH ASDL.
- Remove remaining runtime AST compatibility fallbacks (notably multi-command pipeline path).
- Complete missing word_part and redirection variants from OSH syntax.
- Expand grammar coverage until strict mapping never encounters unsupported variants for target corpus.
