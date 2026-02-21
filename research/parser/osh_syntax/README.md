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

## Git History Checks
Fetched commit history for each file via GitHub API:
- `frontend/syntax.asdl`
  - Oldest commit: `1d388653f303` (2024-10-17) “\[ysh] Multi-line strings passed to <<< don't have newline appended”
- `frontend/types.asdl`
  - Oldest commit: `a621db31c927` (2018-11-18) “\[cleanup] Use the new ASDL style in oil_parse.py.”
- `core/runtime.asdl`
  - Oldest commit: `f4a83929846a` (2023-10-16) “\[refactor] proc to ParamGroup”
- `core/value.asdl`
  - Oldest commit: `a146fd95e1e6` (2024-08-09) “\[ysh] Use separate value.Obj for methods, not Dict”

Note: These were retrieved from `https://api.github.com/repos/oilshell/oil/commits?path=<file>`.
