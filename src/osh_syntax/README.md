# Oil/OSH ASDL + LST References

These files are copied from the Oil/OSH project to serve as canonical schema references for PyBash/Mctash.

Sources (retrieved via `wget`):
- `frontend/syntax.asdl` → `frontend.syntax.asdl`
  - `https://raw.githubusercontent.com/oilshell/oil/master/frontend/syntax.asdl`
- `frontend/types.asdl` → `frontend.types.asdl`
  - `https://raw.githubusercontent.com/oilshell/oil/master/frontend/types.asdl`
- `core/runtime.asdl` → `core.runtime.asdl`
  - `https://raw.githubusercontent.com/oilshell/oil/master/core/runtime.asdl`
- `core/value.asdl` → `core.value.asdl`
  - `https://raw.githubusercontent.com/oilshell/oil/master/core/value.asdl`
- License:
  - `https://raw.githubusercontent.com/oilshell/oil/master/LICENSE.txt`

## LST (Lossless Syntax Tree)
The Oil project describes its Lossless Syntax Tree (LST) in this post:
- `https://www.oilshell.org/blog/2017/02/11.html`

The LST combines an ASDL tree with span metadata that allows reconstructing the original source text. We will implement the same concept when we integrate span tracking into our lexer and parser.

## Provenance Checks Performed
- Read Oil’s `LICENSE.txt` to confirm the main license and exceptions.
  - `https://raw.githubusercontent.com/oilshell/oil/master/LICENSE.txt`
  - Noted explicit exceptions: Python 2.7.13 license and py-yajl/yajl licenses are listed there.
- Checked the top of each copied ASDL file for embedded license headers or provenance notes.
  - No per-file license headers were found in the file headers we inspected.
- Searched the repository tree for a `NOTICE` or `NOTICE.txt` file (none found).

These checks support the assumption that the copied ASDL files fall under Oil’s main Apache 2.0 license, with no additional per-file exceptions declared in those locations. If deeper provenance is required, we should inspect the git history of each ASDL file (first commit and commit message) for origin notes.
