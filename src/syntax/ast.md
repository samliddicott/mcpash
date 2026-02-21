# Mctash AST (PoC)

This directory holds the **schema-level** definition of the Mctash AST. The in-code AST in `src/mctash/ast_nodes.py` mirrors this structure for the current PoC.

## Core Nodes
- `Script`: top-level program with a list of `AndOr` items.
- `AndOr`: list of `Pipeline` nodes and `&&`/`||` operators.
- `Pipeline`: list of `Command` nodes with optional negation.
- `Command`: argv, assignments, and redirects.
- `Word`: a word token with quoting preserved for expansion.
- `Assignment`: `NAME=value` pairs.
- `Redirect`: `op`, `target`, optional `fd`, and optional `here_doc` content.

## Notes
- This AST is intentionally small for the PoC. As grammar coverage expands, more node types will be introduced (functions, compound commands, `if/while`, etc.).
