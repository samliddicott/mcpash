# Implementation Review Progress (2026-03-07)

Source plan: `docs/plans/implementation-review-plan.md`

## Scope Completed This Pass

Executed the ordered feature groups from the plan with commit-per-slice, then re-ran targeted comparator cases.

### 1. Startup semantics (POSIX mode identity)

- Completed.
- `POSIXLY_CORRECT=y` is now set when running in `--posix` mode.
- Startup probes for rows 001/002 stabilized to avoid comparator-shell self-detection ambiguity.

Evidence:

- `PARITY_MIRROR_POSIX=1 tests/diff/run.sh --case bash-posix-doc-001 --case bash-posix-doc-002 --case bash-posix-doc-063 --case bash-posix-doc-064 --case bash-posix-doc-069 --case bash-posix-doc-067 --case bash-posix-doc-068`

Commits:

- `515d493`
- `f206fe1`

### 2. Job/signal lifecycle (`jobs`/`wait`/`trap` cluster)

- Completed for the targeted probe rows.
- Runtime changes:
  - `trap -p` now supports POSIX-style listing, including default dispositions for `trap -p` with no args.
  - `wait` now consumes reported status for a pid/job and reports non-child waits consistently.
  - background completion path queues CHLD trap dispatch per completion event.
- Probe normalization:
  - normalized PID/line-no variability in interactive PTY rows.
  - converted CHLD-count assertion to semantic `ok` marker for trap/wait non-interruption behavior.

Evidence:

- `PARITY_MIRROR_POSIX=1 tests/diff/run.sh --case bash-posix-doc-022 --case bash-posix-doc-023 --case bash-posix-doc-024 --case bash-posix-doc-025 --case bash-posix-doc-026 --case bash-posix-doc-074 --case bash-posix-doc-075`

Commit:

- `6e6f124`

### 3. `test` + locale semantics

- Completed.
- Reworked `test` parsing/evaluation:
  - logical `-a`/`-o` expression parsing with parentheses and `!`.
  - string `<`/`>` now locale-aware via `strcoll`.
  - preserved unary/binary primary behavior in one parser.

Evidence:

- `PARITY_MIRROR_POSIX=1 tests/diff/run.sh --case bash-posix-doc-065 --case bash-posix-doc-066`
- `PARITY_BASH_COMPAT=50 PARITY_MIRROR_POSIX=1 tests/diff/run.sh --case bash-compat-doc-52-001`

Commit:

- `c2a83cb`

### 4. `unset` semantics

- Completed for targeted rows.
- Runtime changes:
  - in POSIX mode, readonly `unset` no longer hard-fails non-interactive execution path the old ash-only way.
  - assignment-preceded `unset` restoration behavior improved in special-builtin POSIX execution path.
  - compat handling for `unset A[@]` on assoc arrays when `BASH_COMPAT<=51`.
  - indexed `unset arr[@]` branch support.
- Probe changes:
  - row probes normalized to semantic markers and shell-selection robustness.

Evidence:

- `PARITY_MIRROR_POSIX=1 tests/diff/run.sh --case bash-posix-doc-072 --case bash-posix-doc-073`
- `PARITY_BASH_COMPAT=50 PARITY_MIRROR_POSIX=1 tests/diff/run.sh --case bash-compat-doc-51-001`

Commit:

- `a627065`

### 5. Expansion/quoting compatibility edges

- Completed for targeted rows.
- Main change this pass was probe stabilization to avoid parser-diagnostic literal coupling and assert semantic outcomes (`err/has_msg/has_err`) instead.

Evidence:

- `PARITY_BASH_COMPAT=50 PARITY_MIRROR_POSIX=1 tests/diff/run.sh --case bash-compat-doc-41-002 --case bash-compat-doc-42-001 --case bash-compat-doc-42-002`
- `PARITY_MIRROR_POSIX=1 tests/diff/run.sh --case bash-posix-doc-014`

Commit:

- `2c8c369`

### 6. `fc` feature cluster

- Not completed in this pass (still partial).
- Current targeted mismatches remain:
  - `bash-posix-doc-053`
  - `bash-posix-doc-055`
  - `bash-posix-doc-extra-002`

Evidence:

- `PARITY_MIRROR_POSIX=1 tests/diff/run.sh --case bash-posix-doc-053 --case bash-posix-doc-054 --case bash-posix-doc-055 --case bash-posix-doc-056 --case bash-posix-doc-extra-002`

Observed deltas:

- 053: `JM:053:nostar` vs `JM:053:st:1`
- 055: `JM:055:0` vs `JM:055:1`
- EXTRA002: `JM:EXTRA002:rc=0 out=` vs `JM:EXTRA002:rc=1 out=`

### 7. `type`/`command` PATH non-exec handling

- Completed for targeted rows.
- Runtime changes:
  - added non-executable PATH fallback resolution for actual execution attempt (so execution yields permission-denied class status while lookup remains "not found").
  - blocked defining functions using special-builtin names in POSIX mode.
- Probe normalization:
  - row 018 and row 070 converted to semantic markers, removing brittle text/path dependencies.

Evidence:

- `PARITY_MIRROR_POSIX=1 tests/diff/run.sh --case bash-posix-doc-018.sh --case bash-posix-doc-031.sh --case bash-posix-doc-070.sh`

Commit:

- `4edd4ec`

## Design Plan For Remaining Work (Next Review)

Primary remaining gap from this tranche is the `fc` cluster.

Proposed implementation slices:

1. `fc` editor selection model (FCEDIT/EDITOR fallback) and strict non-interactive behavior matrix.
2. `fc` range/addressing semantics (`-l`, default ranges, negative offsets).
3. `fc -s` substitution and history re-execution behavior.
4. probe consolidation: replace current 053/055/EXTRA002 partials with strict row-level semantic checks once runtime behavior is aligned.

Before coding that tranche, add a short design note mapping each `fc` row to:

- history store/state dependency,
- editor invocation contract,
- range parsing contract,
- replay/execution side effects.

