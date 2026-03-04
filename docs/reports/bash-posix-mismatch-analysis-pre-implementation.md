# Bash POSIX Mismatch Analysis (Pre-Implementation)

Date: 2026-03-04

Purpose:

- Record the current stdout/stderr mismatch causes before any new runtime/parser implementation changes.
- Use this as the baseline for parity fixes against `bash --posix`.

Sources analyzed:

- Man-page matrix report: `docs/reports/bash-posix-man-matrix-latest.md`
- Man-matrix diffs: `tests/diff/logs/bash-posix-man/diff/*.diff`
- Upstream subset report: `docs/reports/bash-posix-upstream-gap-latest.md`
- Upstream subset diffs: `tests/bash/upstream/baserock-bash-5.1-testing/run2/diff/`

Notes on corpus:

- Upstream tests were fetched from `https://git.baserock.org/cgit/delta/bash.git/tree/tests?h=bash-5.1-testing`.
- That mirror currently has an expired certificate; fetch required `wget --no-check-certificate`.

## Executive Summary

Two mismatch tiers are present:

1. Differential formatting/diagnostic parity mismatches:
- Error strings, prefixes, and some status codes differ even where behavior is close.

2. Semantic/runtime mismatches:
- Expansion, field splitting, parser acceptance of complex quoting/command-sub forms, and `set -e` control-flow behavior diverge substantially.

For the upstream subset run (9 cases):

- Full parity: `0/9`
- Exit-status mismatches: `7`
- Stdout mismatches: `9`
- Stderr mismatches: `7`

## Man-Page Matrix Mismatch Causes

### `man-bash-posix-01-core-state.sh`

Observed:

- Exit status mismatch (`bash=0`, `mctash=2`).
- Missing trailing stdout lines from `mctash` (`env`, `getopts` outputs absent).
- Stderr wording/format differs for readonly `unset`.

Cause assessment:

- `mctash` exits early after readonly `unset` failure in this script path; bash continues under `set +e` style flow in this test.
- Diagnostic formatter differs (`script: builtin: line N` style and wording).

### `man-bash-posix-02-path-command.sh`

Observed:

- `command -v echo`: output differs (`echo` vs `/usr/bin/echo`).
- `type` miss status differs (`1` vs `127`).
- Stderr includes different prefix formatting.

Cause assessment:

- Command resolution presentation policy differs between bash and current `mctash` implementation.
- Missing-command status normalization for `type` is not bash-aligned in this path.
- Diagnostic formatter not yet bash-compatible.

### `man-bash-posix-04-misc-builtins.sh`

Observed:

- `times` output format differs (`0m0.000s 0m0.000s` vs `0.33 0.03` style).
- Additional stderr line for alias miss (`ll: not found`) differs from comparator run.

Cause assessment:

- `times` builtin output formatter does not emulate bash format.
- Alias invocation after `unalias` is currently surfacing a diagnostic path not matching comparator behavior for this case.

## Upstream Subset Mismatch Causes

### 1) `posix2.tests` (`rc 2/6`, stdout+stderr mismatch)

Observed:

- Bash reports expected parser error near `esac` in an eval test.
- `mctash` reports different syntax error location/text.
- `mctash` additionally reports multiple conformance test failures (`$@`, positional >9, `test -x`, `OPTIND`, quoting).

Root cause:

- Multiple core POSIX-semantics divergences (not only diagnostics): positional expansion, option parser init behavior, and quoting logic.
- Parser error reporting path diverges from bash tokenization/context handling.

### 2) `posixexp.tests` (`rc 2/2`, stdout+stderr mismatch)

Observed:

- Both shells fail with missing `recho`, but stderr strings differ (`command not found` vs `not found`).
- Output numbering and many expansion rows diverge.

Root cause:

- Expansion semantics in `${...}` with `$*`/`$@` under varied `IFS` differ.
- Additional diagnostic/traceback path appears in `mctash` in this run lane.

### 3) `posixexp2.tests` (`rc 0/2`, stdout+stderr mismatch)

Observed:

- `mctash` errors: invalid `shopt xpg_echo`, then unterminated quote parse error.
- Bash completes case successfully.

Root cause:

- Parser cannot currently accept one or more quoting constructs exercised by this file.
- Bash extension option handling (`xpg_echo`) currently hard-errors instead of compatible no-op/acceptance behavior in this context.

### 4) `posixpat.tests` (`rc 0/0`, stdout mismatch only)

Observed:

- Return code matches, stderr matches.
- Many `ok` lines become `bad/oops` in `mctash` output.

Root cause:

- Pattern matching/bracket/newline pattern semantics diverge while still yielding overall case exit 0.
- Indicates semantic mismatch in glob/pattern engine rather than immediate parse failure.

### 5) `posixpipe.tests` (`rc 0/2`, stdout+stderr mismatch)

Observed:

- Bash executes and prints expected pipeline/time/type outputs.
- `mctash` fails early with syntax error near newline.

Root cause:

- Parser gap on constructs exercised in this test (pipeline + function/time formatting context).
- Downstream stdout is absent due to early parse failure.

### 6) `ifs-posix.tests` (`rc 0/124`, stdout+stderr mismatch)

Observed:

- Bash reports complete pass summary (`# tests 6856 passed 6856 failed 0`).
- `mctash` emits many split mismatches and times out at safety cap (`124`, `Terminated`).

Root cause:

- Major field-splitting divergence for IFS edge cases (empty fields, delimiter adjacency, whitespace interactions).
- Performance/termination risk in this workload (requires optimization after semantic correction).

### 7) `comsub-posix.tests` (`rc 0/2`, stdout+stderr mismatch)

Observed:

- Bash executes broad command-substitution corpus.
- `mctash` exits early on unterminated quote parse error in test body.

Root cause:

- Command-substitution parser and nested quote handling are incomplete for POSIX torture cases.

### 8) `set-e.tests` (`rc 0/1`, stdout mismatch)

Observed:

- Bash runs full matrix of `set -e` control-flow exceptions.
- `mctash` output truncates after early segments.

Root cause:

- `set -e` suppression/propagation logic is incomplete across compound/list contexts.

### 9) `builtins.tests` (`rc 2/1`, stdout+stderr mismatch)

Observed:

- `mctash` lacks/partially supports multiple bash builtins/options used by this corpus (`builtin`, `enable`, some `declare` flags, `shopt` options, `exec` options).
- Additional parser errors in later sections.

Root cause:

- This file includes many bash-extension behaviors beyond strict POSIX lane.
- For POSIX parity tracking, this case must be split into POSIX-in-scope slice vs extension slice to avoid mixed-signal gating.

## Cross-Cutting Mismatch Categories

Category A: Diagnostic formatting mismatch

- Error prefix shape and wording differ (`not found` style, line placement, builtin labels).

Category B: Status-code mismatch

- `type` miss, readonly/unset flow, and some parse-failure exits differ from bash.

Category C: Expansion semantics mismatch

- `$@`/`$*` with IFS, braced-parameter behaviors, quote-removal and field-splitting interactions.

Category D: Parser acceptance mismatch

- Unterminated quote and command-sub nested constructs accepted by bash but rejected by current parser.

Category E: Builtin surface mismatch

- Missing/partial options and command forms in bash-centric tests (some out of strict POSIX scope).

Category F: Runtime robustness mismatch

- Long IFS workload can hit timeout; current behavior indicates both correctness and efficiency issues.

## Pre-Implementation Actionability

Before writing runtime/parser code, this analysis implies:

1. Split upstream lanes into:
- POSIX-core strict lane (gate)
- Bash-extension informational lane

2. Normalize diagnostics/status policy for POSIX lane first:
- avoids noisy diffs masking semantic regressions.

3. Prioritize semantic fixes in this order:
- field splitting/IFS
- parser quote/command-sub acceptance
- `set -e` control-flow suppression matrix
- `type/command/times` formatting/status parity.
