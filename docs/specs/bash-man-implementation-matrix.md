# Bash Man Requirements Implementation Matrix

Source inventory: `docs/specs/bash-man-requirements.tsv`

Matrix file: `docs/specs/bash-man-implementation-matrix.tsv`

Status meanings:

- `covered`: implemented and tied to explicit test case(s).
- `partial`: implemented surface exists but behavior/options not complete.
- `missing`: not implemented.
- `out_of_scope`: intentionally excluded from that lane (typically posix-only lane for interactive-only items).
- `unknown`: requirement is listed but not yet conclusively classified by comparator evidence.

Total requirements: 398
- Rows with test/harness IDs: 398/398

## Current Counts

### mctash default lane

- covered: 68
- partial: 1
- missing: 9
- out_of_scope: 0
- unknown: 320

### mctash --posix lane

- covered: 68
- partial: 1
- missing: 9
- out_of_scope: 14
- unknown: 306

## Row-Level Evidence Coverage by Category

- Category 1: 78/78 rows mapped to explicit test/harness IDs
- Category 2: 28/28 rows mapped to explicit test/harness IDs
- Category 3: 31/31 rows mapped to explicit test/harness IDs
- Category 4: 21/21 rows mapped to explicit test/harness IDs
- Category 5: 61/61 rows mapped to explicit test/harness IDs
- Category 6: 79/79 rows mapped to explicit test/harness IDs
- Category 7: 10/10 rows mapped to explicit test/harness IDs
- Category 8: 12/12 rows mapped to explicit test/harness IDs
- Category 9: 7/7 rows mapped to explicit test/harness IDs
- Category 10: 6/6 rows mapped to explicit test/harness IDs
- Category 11: 58/58 rows mapped to explicit test/harness IDs
- Category 12: 7/7 rows mapped to explicit test/harness IDs

## Remaining Explicit Missing/Partial Features

- `C1.OPT.SHORT.s`: default=partial posix=partial feature=`-s` evidence=`run_bash_invocation_option_matrix.sh`
- `C1.OPT.SHORT.D`: default=missing posix=missing feature=`-D` evidence=`run_bash_invocation_option_matrix.sh`
- `C1.OPT.LONG.DUMP_PO_STRINGS`: default=missing posix=missing feature=`--dump-po-strings` evidence=`run_bash_invocation_option_matrix.sh`
- `C1.OPT.LONG.DUMP_STRINGS`: default=missing posix=missing feature=`--dump-strings` evidence=`run_bash_invocation_option_matrix.sh`
- `C1.OPT.LONG.VERBOSE`: default=missing posix=missing feature=`--verbose` evidence=`run_bash_invocation_option_matrix.sh`
- `C2.GRAM.019`: default=missing posix=missing feature=`select NAME in ...; do ... done` evidence=`bash-man-grammar-select-coproc.sh`
- `C2.GRAM.024`: default=missing posix=missing feature=`coproc command` evidence=`bash-man-grammar-select-coproc.sh`
- `C3.EXP.001`: default=missing posix=missing feature=`brace expansion {a,b}` evidence=`bash-man-expansion-brace-locale.sh`
- `C3.EXP.029`: default=missing posix=missing feature=`locale translation quoting $"..."` evidence=`bash-man-expansion-brace-locale.sh`
- `C4.REDIR.012`: default=missing posix=missing feature=`here-string <<<word` evidence=`bash-man-redir-here-string.sh`

## Notes

- This pass removed broad category-scope evidence placeholders and replaced them with strict row-level IDs (single-case or focused harness mapping per requirement family).
- New dedicated cases/harnesses were added for previously uncovered feature families (`select/coproc`, brace + `$"..."`, here-string, invocation option matrix, set-o/shopt/variable surface probes).
