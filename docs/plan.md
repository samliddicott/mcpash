# Plan: Mctash

## Milestone 1: Ash Compliance (Core Shell)
Goal: deliver a Python 3 interpreter that passes a minimal **ash-compliant** subset and establishes LST + ASDL foundations.

Primary references for correctness:
- POSIX Shell Command Language (spec): https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/V3_chap02.html
- POSIX Shell Command Language Rationale: https://pubs.opengroup.org/onlinepubs/9699919799/xrat/V4_xcu_chap02.html
- `man ash`

Deliverables
- Lexer with explicit modes for Bash/Ash contextual parsing.
- Parser for ash grammar subset.
- Lossless Syntax Tree with span metadata.
- ASDL schema for executable AST.
- Minimal executor: commands, pipelines, redirections, variables, functions.
- Test harness and ash compliance suite: `ash-shell/test`.
- Runnable target: `scripts/run-ash-test.sh` to execute the ash test harness with `mctash`.

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
- License-aligned research: if MIT/BSD/Apache is chosen, evaluate permissive shell implementations (e.g., `dash`/`ash` derivatives, `toysh`) for reusable components or reference.

## Testing
There are usable corpora, but they differ in fit and licensing.

Best candidates:

1. BusyBox shell tests (`shell/ash_test` and `shell/hush_test`)
- Repo: `https://github.com/mirror/busybox`
- Pros: very large, real ash-family behavior coverage, includes expected-output pairs.
- Cons: GPLv2 project; vendoring tests may affect licensing posture.

2. Oil shell spec tests (`spec/*.test.sh`, especially `posix.test.sh`, `shell-grammar.test.sh`, `redirect*.test.sh`, `word-split.test.sh`)
- Repo: `https://github.com/oilshell/oil`
- Pros: broad shell semantics coverage, easy to run incrementally, good diagnostics.
- Cons: not "ash official"; includes bash/ysh-focused files you must filter.

3. `ash-shell/test` framework
- Repo: `https://github.com/ash-shell/test`
- Pros: already integrated in this repo.
- Cons: it is a test framework, not a language compliance corpus by itself.

Recommended path:

1. Use Oil spec filtered to POSIX/ash-relevant files as primary corpus (fast progress, clearer failures).
2. Add selected BusyBox `ash_test` cases as secondary parity checks once core semantics stabilize.
3. Keep `ash-shell/test` for project-local unit tests.

Execution policy while iterating failures:
1. Reproduce in BusyBox `ash_test`.
2. Confirm intended semantics in POSIX spec and rationale.
3. Check `man ash` for implementation-specific behavior.
4. Add/adjust parser/runtime behavior and rerun the failing test set.

Additional independent check:
- Oil POSIX-oriented subset runner: `src/tests/run_oil_subset.sh`
  - Initial target files: `smoke`, `redirect`, `word-split`
  - Purpose: independent semantics checks without replacing BusyBox ash corpus as primary gate.

Local conformance gate (no external CI required):
- `make regressions`
  - Runs targeted regression checks for fragile semantics:
    - `read` + mixed `IFS` edge behavior
    - pipeline status/control-flow (`pipefail`, negation, pipeline `exit`)
    - redirection/exec error mapping (`126/127`, bad fd)
- `make conformance`
  - Runs targeted regressions, then BusyBox ash corpus, then Oil subset corpus.
  - Enforces baseline thresholds to catch regressions during local development.

## Open Decisions
- Exact ash compliance criteria and test suite selection.
- Final interop syntax ergonomics and error semantics.
- Long-term plan for full Bash compatibility.

## Remaining Ash Parity Gaps (man ash aligned)
- Builtins not yet implemented to ash-man-page level:
  - `fc` baseline list/re-exec added; full editor/history parity remains open
  - `hash`, `times`, `ulimit`, `umask`, `jobs`, `fg`, `bg` baseline support added; full man-page flag parity remains open
- Interactive shell behavior not yet complete:
  - true interactive REPL prompt loop
  - login-shell startup file flow (`/etc/profile`, `~/.profile`)
  - interactive `ENV` file processing
  - vi/emacs command-line editing behavior (`-V` / `-E`)
- Parsed-vs-effective option parity gap for interactive/job-control options:
  - `-i`, `-I`, `-m`, `-b`, `-V`, `-E`

## Word Expansion Parity (POSIX-First, Ash-Checked)
Goal: remove remaining ASDL-word execution divergences without regressing ash parity.

Classification for every divergence:
- `POSIX required`: behavior mandated by POSIX (`shall` language)
- `POSIX unspecified`: implementation choice permitted by POSIX
- `ash extension`: behavior outside POSIX but required for ash compatibility target

Tracking fields per divergence row:
- case id and failing test(s)
- current `mctash` behavior
- target behavior
- authority source (`POSIX spec`, `POSIX rationale`, `man ash`, ash test evidence)
- implementation path (`native ASDL` vs temporary fallback)
- closure evidence (regression test + BusyBox module rerun)

Implementation order:
1. Assignment-word quote-removal parity (`name=value` contexts)
2. Double-quoted backslash/parameter parity
3. Structured command-substitution expansion in ASDL execution (remove text round-trips incrementally)

Validation gates for each step:
1. `tests/regressions/run.sh` must pass
2. BusyBox modules must pass: `ash-quoting`, `ash-vars`, `ash-parsing`
3. No memory-cap override during debug runs (`MCTASH_MAX_VMEM_KB` policy remains in force)

## Conformance Snapshot
- Current conformance status matrix: `docs/conformance-matrix.md`
- POSIX requirement-to-test trace table: `docs/posix-trace-table.md`
- Threaded-runtime deviation register: `docs/threaded-runtime-deviations.md`
- OSH ASDL adoption and migration history: `docs/ASDL-adoption-history.md`
