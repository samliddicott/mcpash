# Plan 009: Man-Page Detail Processing Discipline

Date: 2026-03-06

Goal:

- Prevent false `covered` status caused by surface-only checks.
- Convert bash man-page prose into behavior-level requirements with executable evidence.

## Process Defect Identified

Previous processing over-weighted variable presence/surface checks and bucket-level pass status.  
Behavioral clauses in prose (for example, "is expanded", "is displayed", "is treated as") were not consistently converted into explicit matrix rows with dedicated tests.

## Corrected Process

For each man-page section and each requirement row:

1. Sentence extraction:
   - Extract normative or behavior-bearing sentences.
   - Trigger words: `is expanded`, `is displayed`, `is treated`, `is ignored`, `is caught`, `returns`, `prints`, `waits`, `times out`.

2. Requirement decomposition:
   - Split each feature into:
     - `surface` (existence/listing)
     - `semantic` (runtime behavior)
     - `mode` (`bash` vs `--posix`)
     - `interactive` (PTY-required behavior)

3. Evidence rule:
   - A row cannot be `covered` unless at least one dedicated behavior test exists for that row class.
   - Surface-only evidence can yield at most `partial`.

4. Comparator rule:
   - Differential tests must declare comparator lane (`bash`, `bash --posix`, ash-family).
   - Dynamic outputs (timing/order/non-contractual text) may be normalized only with explicit rationale in test comments.

5. Reporting rule:
   - Regenerate gap/compliance reports after row status changes.
   - `compliance-truth-check` must fail on report contradictions.

## Initial Application Scope

Applied now to:

- `Shell Variables`
- `PROMPTING`
- `SIGNALS`

## Immediate Execution Board

1. Add missing rows discovered from prose:
   - `TIMEFORMAT`
2. Reclassify rows that only had surface evidence:
   - `${v@op}` transformation operators
   - `BASH_XTRACEFD`
   - `HISTTIMEFORMAT`
   - `TMOUT`
   - prompt escape row (`PS2`/`PS4` depth)
3. Add dedicated tests where practical:
   - `bash-man-param-transform-ops.sh`
   - `bash-man-timeformat.sh`
   - `bash-man-bash_xtracefd.sh`
   - `run_interactive_tmout_matrix.sh`
4. Publish a gap report with newly surfaced partial rows and evidence.
