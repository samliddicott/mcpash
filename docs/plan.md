# Plan: Mctash

## Milestone 1: Ash Compliance (Core Shell)
Goal: deliver a Python 3 interpreter that passes a minimal **ash-compliant** subset and establishes LST + ASDL foundations.

Deliverables
- Lexer with explicit modes for Bash/Ash contextual parsing.
- Parser for ash grammar subset.
- Lossless Syntax Tree with span metadata.
- ASDL schema for executable AST.
- Minimal executor: commands, pipelines, redirections, variables, functions.
- Test harness and ash compliance suite: `ash-shell/test`.

Exit Criteria
- Pass the `ash-shell/test` suite with reproducible results.
- Stable LST + AST output with span fidelity for round-trip tests.

## Milestone 2: Interop MVP
Goal: enable explicit, opt-in Python interop without changing pure shell semantics.

Deliverables
- `python { ... }` block execution.
- `python:` callable resolution:
  - Invoke callable if resolved.
  - Fallback to block semantics when not callable (e.g., `import`, `from`).
- Conversion table with explicit casts (`int`, `float`, `json`, `path`, `bool`).
- Error/exception mapping to shell status codes.

Exit Criteria
- Demonstrate Bash → Python calls with deterministic casting.
- Demonstrate Python → Bash calls with status + output capture.

## Milestone 3: Compatibility Expansion
Goal: broaden Bash feature coverage and runtime fidelity.

Deliverables
- Expanded grammar coverage and lexer modes.
- Builtins and redirection edge cases.
- Process model correctness (signals, subshells, pipes).
- Larger test corpus from real scripts.

Exit Criteria
- Documented coverage map with passing tests for key Bash features.

## Milestone 4: Tooling + Translation
Goal: leverage LST for tooling and source-to-source workflows.

Deliverables
- Style-preserving formatter.
- Lint/analysis hooks.
- Optional translation path for interop-aware dialect.

Exit Criteria
- Stable tooling output on representative scripts.

## Cross-Cutting Workstreams
- Licensing review for any borrowed tests or fixtures.
- CI setup with deterministic test runs.
- Performance profiling of parsing and execution paths.
- Threading model investigation (threads vs fork), with per-thread CWD and FD isolation requirements.

## Open Decisions
- Exact ash compliance criteria and test suite selection.
- Final interop syntax ergonomics and error semantics.
- Long-term plan for full Bash compatibility.
