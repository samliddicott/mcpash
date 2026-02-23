# Strategy: Mctash

## Goal
Deliver a Python 3 Bash implementation with bidirectional Bash ↔ Python interop while preserving real-world Bash compatibility and enabling lossless tooling.

## Strategic Principles
- Compatibility is earned by **parser fidelity** and **execution semantics**, not by partial syntax.
- Interop must be **explicit** and **predictable**; avoid invisible type coercions.
- A **lossless syntax representation** is required for safe translation, refactoring, and tooling.
- Keep the core **minimal and testable**; expand via staged milestones.
- Prioritize behavior against POSIX shell spec/rationale, then reconcile with `man ash` and BusyBox ash tests.

## Architecture Strategy
### 1) Front End: Lexer, Parser, LST, AST
- Implement a Bash-aware lexer with explicit **lexer modes** to match contextual parsing behavior.
- Build a **Lossless Syntax Tree (LST)** that preserves span metadata for comments and formatting.
- Define **ASDL schemas** for the executable AST and for interop-aware constructs.
- Keep LST and AST separate so execution stays lean while tooling remains faithful.

### 2) Runtime: Execution Core
- Implement a tree interpreter in Python 3 for the initial runtime.
- Separate evaluation of **commands** vs **expressions** to reduce ambiguity and enable interop.
- Model file descriptors and process semantics explicitly (pipes, redirections, subshells, status codes).
- **Threaded execution model**: consider threads in places Bash would fork, with explicit handling for per-thread CWD, per-thread file handles (potentially via `unshare`), and shared vs isolated data.

### 3) Interop Boundary
- Provide an **interop layer** that is opt-in and isolated from pure Bash semantics.
- **Python block execution**: `python { ... }` runs a sequence of Python statements.
- **Direct callable resolution**: `python:` is a pseudo-function prefix.
  - If the token after `python:` resolves to a Python callable, invoke it.
  - If it does not resolve to a callable (e.g., `import`, `from`), interpret the remainder as a `python { ... }` block.
- Define a **stable conversion table**:
  - Strings and argv arrays are the default.
  - Explicit casts for `int`, `float`, `json`, `path`, and `bool`.
  - Errors map to non-zero status codes and surfaced diagnostics.
- Make Python calls from Bash and Bash calls from Python symmetric in capabilities and error handling.

## Milestone Strategy
### Milestone 1: Parser + LST + Minimal Executor
- Target **ash compliance** as the initial shell subset.
- Produce LST spans and a basic AST.
- Execute simple commands, pipelines, redirections, variables, and functions.

### Milestone 2: Interop MVP
- Add explicit interop syntax: `python { ... }` and `python:` callable resolution.
- Support Python call-outs with controlled casting and automatic interposing arguments.
- Support Python calling Bash commands with status and output capture.

### Milestone 3: Compatibility Expansion
- Expand Bash grammar coverage and runtime semantics.
- Add broader builtins and advanced redirection edge cases.
- Validate against real-world scripts and curated test suites.

### Milestone 4: Tooling and Translation
- Implement formatting- and style-preserving tooling using LST spans.
- Provide linting/analysis hooks for modernization and interop adoption.

## Testing Strategy
- Build a **test corpus** with:
  - Minimal unit tests for lexer modes and parse edge cases.
  - Integration tests for pipelines, redirection, and status propagation.
  - Real-world scripts under a compatibility harness.
- Treat parser failures as **high-severity**; regressions must be caught early.
- Use spec-driven debugging order:
  - POSIX shell spec (normative): https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/V3_chap02.html
  - POSIX rationale (intent/edge cases): https://pubs.opengroup.org/onlinepubs/9699919799/xrat/V4_xcu_chap02.html
  - `man ash` behavior notes
  - BusyBox `ash_test` failing case

## Licensing and Legal Strategy
- Avoid direct code reuse from GPL Bash unless explicitly intended.
- Use the Oil/OSH material as conceptual references, not code sources.
- Verify licensing of any external test fixtures before inclusion.
- If we target a permissive license (MIT/BSD/Apache), evaluate permissive shells (e.g., `dash`/`ash` derivatives, `toysh`) for reference or selective reuse under compatible terms.

## References and Rationale (from Oil Blog)
- ASDL enables concise, structured AST definitions and serialization workflows.
- Lossless Syntax Trees preserve comments and formatting through span metadata.
- ASTs are lossy and unsuitable for translation or style-preserving tooling.

## Standards References
- POSIX Shell Command Language (Issue 8, 2024 edition): https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/V3_chap02.html
- POSIX Shell Command Language Rationale (XCU): https://pubs.opengroup.org/onlinepubs/9699919799/xrat/V4_xcu_chap02.html

## Next Decisions
- Define the exact **interop syntax** for the MVP.
- Choose a **Bash subset** for Milestone 1.
- Select the **initial test corpus** and success criteria.
