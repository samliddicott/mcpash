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

### Bash POSIX Parity Matrix (New)

To close parity for `mctash --posix` against `bash --posix`, we now maintain a man-page-driven matrix:

- Coverage map: `tests/compat/bash_posix_man_coverage.tsv`
- Runner: `tests/compat/run_bash_posix_man_matrix.sh`
- Make target: `make bash-posix-man-matrix`
- Latest report: `docs/reports/bash-posix-man-matrix-latest.md`

This matrix tracks all bash man-page builtins as:
- `covered` (has case and currently executed)
- `partial` (known gap, case still needed)
- `out_of_scope` (bash extension not in current POSIX-lane target)

Online corpus source for expansion:
- GNU bash upstream tests index: `https://git.savannah.gnu.org/cgit/bash.git/tree/tests`
- Fetch helper: `tests/bash/fetch_upstream_tests.sh` (`make bash-tests-fetch`)
- Fetched artifacts (ignored by git): `tests/bash/upstream/`
- Reproducibility:
  - pin ref with `BASH_UPSTREAM_REF=<tag|branch|commit>`
  - cache by ref under `tests/bash/upstream/<safe_ref>/`
  - lock metadata in `fetch-lock.json` (ref/time/count/source URLs)

License note:
- Upstream bash tests are GPL-licensed; we keep fetched corpus as external test input and avoid copying test bodies into tracked project sources unless explicitly approved.

Local conformance gate (no external CI required):
- `make regressions`
  - Runs targeted regression checks for fragile semantics:
    - `read` + mixed `IFS` edge behavior
    - pipeline status/control-flow (`pipefail`, negation, pipeline `exit`)
    - redirection/exec error mapping (`126/127`, bad fd)
- `make read-matrix`
  - Runs `read` differential matrix across ash-family comparators and bash comparator lane.
  - Includes bash-mode `read` option surface (`-a -d -e -i -n -N -p -r -s -t -u`).
- `make jobs-interactive-matrix`
  - Runs PTY-based interactive jobs/fg/bg compatibility probes (`STRICT=1` enforces parity checks).
- `make trap-noninteractive-matrix`
  - Runs non-interactive trap delivery matrix across a catchable signal set (`STRICT=1` enforces parity checks).
- `make trap-interactive-matrix`
  - Runs PTY-based interactive trap subset probes (`STRICT=1` enforces parity checks).
- `make trap-variant-matrix`
  - Generates comparator-by-signal report at `docs/reports/trap-variant-matrix-latest.md`.
- `make conformance`
  - Runs targeted regressions, then BusyBox ash corpus, then Oil subset corpus.
  - Enforces baseline thresholds to catch regressions during local development.

## Open Decisions
- Exact ash compliance criteria and test suite selection.
- Final interop syntax ergonomics and error semantics.
- Long-term plan for full Bash compatibility.

## POSIX + `BASH_COMPAT` Policy (Planned)
- `--posix` remains the baseline POSIX/ash behavior mode.
- `BASH_COMPAT` is the explicit selector for Bash-compat extension gates.
- In `--posix` mode, selected Bash-compatible features may be enabled only when `BASH_COMPAT` is set to a supported level.
- Feature rollout will be per-feature (`declare -a`, then `declare -A`, then bridge list/dict and tie `array`/`assoc`).
- Policy details and rationale are tracked in `docs/bash-compat-mode-policy.md`.
- `mctash` extension: `shopt -s read_interruptible` allows signal-interruptible blocking `read` behavior (opt-in; non-POSIX).

## Diagnostics/I18N Precursor

- Introduced diagnostic key routing as a prerequisite for ash-vs-bash stderr parity work:
  - `src/mctash/diagnostics.py`
  - `src/mctash/i18n.py`
- Runtime now emits several common diagnostics through keyed templates instead of inline literal strings.
- Active mode is now exported as `MCTASH_MODE` during startup mode resolution, so diagnostics can be selected by mode policy.
- Current templates are intentionally behavior-preserving; follow-up parity work will adjust bash-mode templates without rewriting runtime logic.
- Localization path is standard gettext-based (`locale/` catalog support via `get_translator()`), staged for later translation catalogs.

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

## Bash Parity Gap Tracking (BASH_COMPAT Mode)

Dual-lane approach:
- keep ash parity and bash parity independent, with mode-pinned runners.
- ash lane: `MCTASH_MODE=posix` against ash baseline.
- bash lane: `MCTASH_MODE=bash` with mirrored `BASH_COMPAT` against bash baseline.

Primary tooling:
- `make diff-parity-matrix`
- report output: `docs/reports/bash-gap-latest.md`

Current tracked bash-lane gaps (2026-03-03):
1. `bash-compat-array-append`: stdout mismatch
2. `bash-compat-array-append`: stderr mismatch
3. `bash-compat-assoc-keys`: stdout mismatch

Immediate closure plan:
1. `arr+=(...)` compatibility fixes
2. `${!assoc[@]}` key expansion parity
3. strict matrix rerun and report update

## Subscript Evaluation Semantics (Bash-Compat Requirement)

Requirement to track explicitly:
- Indexed arrays (`declare -a`): subscript expression is evaluated with arithmetic semantics before indexing.
- Associative arrays (`declare -A`): subscript is treated as a string key.

Current implementation note:
- Runtime currently branches by detected type (`array` vs `assoc`) but still treats many subscripts as literal text for lookup/coercion.
- This can diverge from bash behavior for arithmetic expressions in indexed subscripts.

Planned closure:
1. Add an explicit subscript-evaluator path for indexed arrays:
   - evaluate index expression using arithmetic rules
   - preserve bash-like error behavior for invalid index expressions
2. Keep associative subscripts on string-key path:
   - no arithmetic coercion in assoc mode
3. Apply consistently across:
   - assignment (`name[sub]=value`)
   - read/expansion (`${name[sub]}`)
   - unset (`unset 'name[sub]'`)
4. Validate with bash-diff matrix cases that cover:
   - literal numeric subscripts
   - arithmetic expressions (`i+1`, `2*3`, nested vars)
   - quoted and unquoted subscript text where behavior differs
   - assoc keys that look numeric but must remain string keys

Acceptance criteria:
- New `tests/diff/cases/bash-compat-subscript-eval*.sh` pass against bash baseline with `BASH_COMPAT` mirrored.
- `make diff-parity-matrix` remains green for ash lane and bash lane.
- No regression in existing array/assoc operator cases.

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

Current progress (2026-03-02):
1. Assignment-word quote-removal parity: `in progress`
2. Native ASDL assignment RHS now covers safe subsets:
   - literals without quote/backslash escapes
   - `word_part.SimpleVarSub` for named variables
   - `word_part.BracedVarSub` for `${name}`, `${#name}`, and simple default/alt/error ops with literal-only args
   - `word_part.ArithSub`
   - `word_part.CommandSub` (including structured child execution path)
3. Double-quoted backslash/parameter parity for global argv-word native path: `pending` (legacy path retained to preserve ash/POSIX behavior)
4. Structured command substitution execution: `partial` (uses `word_part.CommandSub.child` when available; text fallback retained)

Step-2 note:
1. A guarded argv-native attempt (literal-only words) was evaluated and rolled back after ash-vars regressions.
2. Current conclusion: global argv-native rollout needs stronger word-part fidelity guarantees before reattempt.

## Expansion Engine Transition: Sentinels -> Structured Data
Goal: remove sentinel-character transport from expansion internals and use typed expansion segments end-to-end.

Why:
1. Sentinel markers (`\ue001`... etc.) can collide with real user input.
2. Semantics become implicit in text and harder to reason about.
3. Structured expansion is the safer foundation for ASDL-native execution and future compile-to-Python mode.

Scope:
1. Word expansion (argv, assignment RHS, case patterns, redirection targets).
2. Quote-removal, field-splitting, pathname expansion, pattern escaping.
3. Existing sentinel helper paths remain only behind transition adapters until removed.

Phased plan:
1. Define typed expansion model:
   - `ExpansionSegment(text, quoted, glob_active, split_active, source_kind)`
   - `ExpansionField(segments, preserve_boundary)`
2. Build adapters:
   - ASDL `word_part.*` -> typed segments.
   - legacy text parser -> typed segments (temporary bridge).
3. Replace expansion stages:
   - quote-removal operates on flags, not text rewriting.
   - field splitting uses segment metadata.
   - globbing runs only where `glob_active=true`.
4. Remove sentinel reliance:
   - eliminate `\ue00x` marker transport in runtime paths.
   - keep compatibility shim only for legacy parser paths; then delete.
5. Expand differential tests:
   - add cases containing literal private-use chars (e.g. `U+E001`) to prove no collision.
   - add mixed quoted/unquoted glob tests and case-pattern quoting tests.

Guardrails:
1. No new sentinel markers introduced in runtime/expansion code.
2. Any temporary adapter must be explicitly documented and time-bounded.
3. Every phase must keep `tests/regressions/run.sh` and parity matrix green.

Exit criteria:
1. No sentinel-marker based semantic transport in core expansion engine.
2. ASDL-native command/assignment/case expansion paths are fully structured.
3. Collision tests with literal private-use Unicode pass under ash/bash differential harnesses.

## Conformance Snapshot
- Current conformance status matrix: `docs/conformance-matrix.md`
- POSIX requirement-to-test trace table: `docs/posix-trace-table.md`
- Threaded-runtime deviation register: `docs/threaded-runtime-deviations.md`
- OSH ASDL adoption and migration history: `docs/ASDL-adoption-history.md`

## Semantic Master Matrix (Cross-Baseline)
Goal: use one canonical matrix to prevent ash-vs-bash drift and avoid mode-specific patch churn.

Canonical artifacts:
1. Matrix data: `tests/compat/semantic_matrix.tsv`
2. Runner: `tests/compat/run_semantic_matrix.sh`
3. Report: `docs/reports/semantic-matrix-latest.md`

Execution baselines per row:
1. `ash` (POSIX-oriented ash behavior)
2. `bash --posix` (POSIX behavior under bash)
3. `bash` (full bash behavior)
4. `mctash --posix`
5. `mctash` (default/bash mode)

Row classification:
1. `posix-required`:
   - `ash` and `bash --posix` must agree (otherwise `conflict`)
   - `mctash --posix` must match POSIX baselines
2. `extension-bash`:
   - `mctash` default mode must match `bash` default mode
3. `extension-ash`:
   - `mctash --posix` must match `ash` for ash-specific extensions
4. `posix-unspecified`:
   - tracked informationally until policy is pinned

Policy:
1. This semantic matrix is the master/sole behavior matrix for new parity closure.
2. Existing lane-specific harnesses (BusyBox, upstream bash lanes, diff suites) remain feeder corpora and diagnostics, not competing truth tables.
3. Upstream heavy corpus rows are imported as feeder rows (`@upstream:*`) and start as `posix-unspecified` until split into smaller `posix-required` requirements with explicit POSIX anchors.

Current feeder imports:
1. `posix2.tests`
2. `posixexp.tests`
3. `posixexp2.tests`
4. `posixpat.tests`
5. `posixpipe.tests`
6. `ifs-posix.tests`
7. `comsub-posix.tests`
8. `set-e.tests`
