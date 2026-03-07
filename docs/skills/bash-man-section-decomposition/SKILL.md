# Skill: Bash Man Section -> Requirements/Matrix Decomposition

## Purpose
Turn one `man bash` section (e.g., `JOB CONTROL`) into explicit, testable requirement rows in:
- `docs/specs/bash-man-requirements.tsv`
- `docs/specs/bash-man-implementation-matrix.tsv`

This skill is for **spec decomposition first**. Runtime implementation is separate.

## Inputs
- Source text from `man bash` (plain text via `col -b`).
- Existing requirement/matrix TSV files.
- Existing comparator tests and harnesses in `tests/`.

## Outputs
- New or refined `C*.***` requirement rows, one behavior per row.
- Matching matrix rows with test IDs and honest status (`covered`/`partial`/`out_of_scope`).
- A design-model note that maps requirement rows to runtime components/state transitions.
- No grouped shorthand like “etc”.

## Process
1. Extract section text with stable formatting.
2. Split section into numbered paragraphs (or semantic chunks).
3. For each paragraph, derive atomic behaviors:
   - one observable behavior per row
   - each row must be executable/testable
4. Assign deterministic IDs in the category namespace.
5. Write requirement row:
   - `req_id, category, subcategory, feature_type, feature, posix_mode_status, bash_man_section, notes`
6. Write matrix row with initial evidence/status:
   - `req_id, ... , mctash_default, mctash_posix, tests, notes`
   - if no strict case exists yet, mark `partial` and add planned case ID(s)
7. Reconcile existing broad rows:
   - keep if still useful, but avoid overlap ambiguity
   - prefer specific rows over one broad “covered” row
8. Validate TSV consistency:
   - each new requirement has matching matrix row
   - test IDs are explicit
   - statuses match real evidence
9. Produce implementation design model (before runtime coding):
   - write a short design note (e.g. `docs/design/<section>-runtime-model.md`)
   - map each requirement row to:
     - runtime ownership (module/function boundary)
     - state model (states + transitions)
     - invariants/preconditions
     - comparator test case(s)
   - explicitly call out rows blocked on architecture changes
10. Re-review the design model during implementation:
   - after each non-trivial test result or regression, compare observed behavior to the design note
   - if implementation pressure reveals missing state/event modeling, update the design note first, then code
   - keep a short "design deltas from evidence" log in the design note so test-driven changes remain explicit

## Evidence Rules
- `covered` only if comparator-backed behavior case exists and passes.
- `partial` if behavior is not fully asserted, ambiguous, or only surface-tested.
- Planned tests may be listed in `tests` column as future case IDs, but status stays `partial`.

## Recommended Commands
```bash
MANWIDTH=120 man bash | col -b > /tmp/man_bash.txt
rg -n "^JOB CONTROL$|^SIGNALS$" /tmp/man_bash.txt
sed -n '2140,2202p' /tmp/man_bash.txt
```

```bash
python3 - <<'PY'
import csv
for p in ['docs/specs/bash-man-requirements.tsv','docs/specs/bash-man-implementation-matrix.tsv']:
    with open(p) as f:
        for row in csv.reader(f, delimiter='\t'):
            if row and row[0].startswith('C8.JOB'):
                print('\t'.join(row))
PY
```

## Quality Checklist
- [ ] Every paragraph statement is represented by >=1 atomic row.
- [ ] No “etc”/grouped requirement rows for behavior details.
- [ ] Every new requirement row has a matrix row.
- [ ] Matrix `tests` column contains concrete case IDs.
- [ ] Status values are conservative and evidence-based.
- [ ] Notes mention comparator basis and remaining uncertainty.
- [ ] Design note has been re-reviewed after initial implementation/test runs.
- [ ] Any architecture-level behavior changes discovered during testing are reflected in the design note before further coding.

## Implementation Hand-off Template
After decomposition, produce an implementation plan in this order:
1. Add/update design model mapping each row to runtime semantics.
2. Add missing comparator tests for the new rows.
3. Implement runtime semantics row-by-row (by subsystem slices), re-checking the design after each slice.
4. Reclassify row statuses from evidence.
5. Re-run matrix gates and close rows.

## Notes
- Decomposition is a requirements activity, not a claim of compliance.
- Keep row naming stable; prefer adding rows to mutating IDs.
- If a row cannot be implemented without deeper architecture work, keep it `partial` and record the blocker in the design-model note.
