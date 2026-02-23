# Vision: Mctash (Python 3 Bash with Python Interop)

## Purpose
Build a Python 3 implementation of Bash that preserves Bash compatibility while enabling **bidirectional interop** between Bash scripts and Python functions. Bash should be able to call Python functions directly, and Python code should be able to invoke Bash commands and functions with a clear, minimal data model.

This project is inspired by the Oil/OSH work (Python-based shell front end with a strong AST/ASDL foundation), but it diverges by making **Python interop** a first-class design goal rather than a secondary runtime detail.

## Vision Summary
- **Compatibility first**: Execute real-world Bash scripts in Python 3 with high fidelity.
- **Interop by design**: Make Python functions callable from Bash with predictable data conversions, and make Bash commands invocable from Python without shell-quoting pitfalls.
- **Lossless representation**: Preserve enough source structure (formatting, comments, exact syntax) to support source-to-source tooling and safe transformations.
- **Typed-ish core**: Use ASDL to define structured ASTs; add lossless syntax metadata so translation and tooling remain faithful.

## What We Want to Build
### 1) A Python 3 Bash Interpreter
- Lexer, parser, and executor in Python 3.
- Parity with Bash behavior where feasible (subtle parsing and runtime rules).
- Feature flagging for non-portable or high-risk constructs.

### 2) First-Class Bash ↔ Python Interop
- **Bash → Python**: Call Python functions as if they were builtins or commands.
  - `python:` is a pseudo-function prefix.
  - If the token after `python:` resolves to a Python callable, invoke it.
  - If it does not resolve to a callable (e.g., `import`, `from`), interpret the remainder as if it were in a `python { ... }` block.
- **Python block execution**: `python { ... }` runs a sequence of Python statements.
- **Python → Bash**: Run Bash functions/commands and access their status and output.
- **Data model constraints**:
  - Bash is string- and argv-based; Python expects richer types.
  - Provide **explicit casting rules** (e.g., `int`, `float`, `json`, `path`) and **safe defaults**.
  - Avoid implicit, lossy conversions when ambiguity exists.

### 3) Lossless Syntax Tree (LST) + ASDL AST
- Use **ASDL** to define AST schemas for Bash and for interop-aware constructs.
- Maintain **lossless syntax metadata** (spans) so translation and formatting can preserve comments and exact syntax.
- This follows the pattern described in the Oil project:
  - A lossless tree sits between the AST and the parse tree, preserving details irrelevant to execution but important for translation and tooling.

### 4) Source-to-Source Tools
- With a lossless representation, support tools like:
  - Bash-to-Mctash linting/modernization.
  - Auto-formatting without semantic drift.
  - Optional translation paths (e.g., Bash + Python interop “dialect” output).

## Why ASDL and Lossless Trees Are Central
From the referenced Oil posts:
- **ASDL defines a data structure, not a language grammar**, and enables concise, typed-ish representations suitable for tooling and serialization.
- **ASTs are lossy**, which is fine for execution but not for translation or high-fidelity tooling.
- **Lossless Syntax Trees** preserve formatting and comments by storing span metadata and binding significant tokens to tree nodes.

These ideas are foundational for Mctash because **interop and tooling require stable, faithful representations** of the original Bash source.

## Core Requirements (High-Level)
- **Parser correctness**: Must parse real-world Bash (including tricky lexer modes and grammar edge cases).
- **Lossless spans**: Span IDs for significant tokens; span array preserves full source text.
- **Clear interop boundary**:
  - Define what data types are allowed to cross the boundary.
  - Define how errors and exceptions propagate (e.g., Python exception → Bash non-zero status).
- **Testable semantics**: A portable, reproducible test suite to validate compatibility.
- **Normative grounding**: align behavior to POSIX Shell Command Language and use rationale text for ambiguous cases.
  - Spec: https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/V3_chap02.html
  - Rationale: https://pubs.opengroup.org/onlinepubs/9699919799/xrat/V4_xcu_chap02.html

## Assumptions and Constraints
- **Compatibility will be staged**: we will start with a well-defined subset (Milestone 1 = ash compliance) and grow toward Bash.
- **Interop is opt-in**: Python interop features should not alter semantics of pure Bash scripts unless explicitly used.
- **Minimal Python object exposure**: Python access from Bash is deliberately constrained to avoid a leaky, unsafe object model.
- **Threaded execution model**: where Bash would fork, this implementation may use threads. We must handle per-thread CWD, per-thread file handles (potentially via `unshare` or equivalent isolation), and per-thread data with shared state carefully.

## Risks and Unknowns
- **Bash parsing complexity**: Bash is notoriously tricky (lexer modes, ambiguous constructs, contextual parsing).
- **Execution model gaps**: process model, file descriptor quirks, and signal semantics will be hard to replicate in pure Python.
- **Interop security and isolation**: calling Python from Bash can be powerful but dangerous without clear sandboxing boundaries.

## Licensing and Legal Considerations (To Verify)
- **No code copying from Bash** unless we accept GPL obligations. Reimplementation by clean-room design is likely required.
- **Oil/OSH references** are for ideas, not direct code reuse unless their licenses are compatible and explicitly adopted.
- **Test fixtures and scripts** must be checked for licensing before inclusion.
- **Candidate permissive sources**: if we choose MIT/BSD/Apache licensing, evaluate permissive shells (e.g., `dash`/`ash` derivatives, `toysh`) for references or selective reuse under compatible terms.

## References (Blog Sources)
- “ASDL Implementation and Use Cases” (2017-01-06): ASDL pipeline, multiple tree representations, and lossless needs.
- “From AST to Lossless Syntax Tree” (2017-02-11): LST structure, spans, preserving formatting/comments.
- “What is Zephyr ASDL?” (2016-12-11): ASDL describes data structures (AST), not grammar; ADTs and serialization.
- “Translating Shell to Oil” (2017-02-05) and “Part Two” (2017-02-06): style-preserving translation and language evolution rationale.

## Standards References
- POSIX Shell Command Language (Issue 8, 2024 edition): https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/V3_chap02.html
- POSIX Shell Command Language Rationale (XCU): https://pubs.opengroup.org/onlinepubs/9699919799/xrat/V4_xcu_chap02.html

## Open Questions (Next for Strategy)
- What exact Bash subset is our first milestone?
- What interop syntax is acceptable and least disruptive?
- Should we define a new ASDL schema for interop nodes, or extend a Bash schema?
- What test corpus do we adopt first (e.g., POSIX tests, real-world script suites)?
