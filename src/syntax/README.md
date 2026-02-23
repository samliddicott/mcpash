# Syntax Schemas

## Canonical ASDL (Adopted)

Mctash now treats Oil/OSH ASDL as the canonical syntax schema foundation.

Canonical files:

- `src/syntax/osh/syntax.asdl`
- `src/syntax/osh/types.asdl`
- `src/syntax/osh/runtime.asdl`
- `src/syntax/osh/value.asdl`
- `src/syntax/osh/LICENSE.txt`

Source project and URLs:

- Project: Oil Shell (`oilshell/oil`)
- `frontend/syntax.asdl`:
  - `https://raw.githubusercontent.com/oilshell/oil/master/frontend/syntax.asdl`
- `frontend/types.asdl`:
  - `https://raw.githubusercontent.com/oilshell/oil/master/frontend/types.asdl`
- `core/runtime.asdl`:
  - `https://raw.githubusercontent.com/oilshell/oil/master/core/runtime.asdl`
- `core/value.asdl`:
  - `https://raw.githubusercontent.com/oilshell/oil/master/core/value.asdl`
- License:
  - `https://raw.githubusercontent.com/oilshell/oil/master/LICENSE.txt`

## Legacy Local Schema

- `src/syntax/pybash.asdl` is legacy and retained only as historical reference.
- New parser/runtime alignment work must target OSH ASDL node shapes.

## Implementation Note

Current parser emits LST and maps into OSH-shaped ASDL dictionaries (`src/mctash/asdl_map.py`) in strict mode; the runtime executes through an adapter (`src/mctash/osh_adapter.py`) while full native OSH-node execution is being completed.
