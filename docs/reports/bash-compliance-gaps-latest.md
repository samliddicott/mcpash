# Bash Compliance Gap Report (From Man Requirements Matrix)

Source: `docs/specs/bash-man-implementation-matrix.tsv`

## Explicit Missing/Partial Features

### Category 1

- `C1.OPT.SHORT.s` `-s`: default=`partial` posix=`partial`
  evidence: `run_bash_invocation_option_matrix.sh`
  note: -s recognized; trailing args currently mis-handled in CLI split path.
- `C1.OPT.SHORT.D` `-D`: default=`missing` posix=`missing`
  evidence: `run_bash_invocation_option_matrix.sh`
  note: -D currently rejected as illegal option.
- `C1.OPT.LONG.DUMP_PO_STRINGS` `--dump-po-strings`: default=`missing` posix=`missing`
  evidence: `run_bash_invocation_option_matrix.sh`
  note: --dump-po-strings currently rejected as illegal option.
- `C1.OPT.LONG.DUMP_STRINGS` `--dump-strings`: default=`missing` posix=`missing`
  evidence: `run_bash_invocation_option_matrix.sh`
  note: --dump-strings currently rejected as illegal option.
- `C1.OPT.LONG.VERBOSE` `--verbose`: default=`missing` posix=`missing`
  evidence: `run_bash_invocation_option_matrix.sh`
  note: --verbose currently rejected as illegal option; -v exists.

### Category 2

- `C2.GRAM.019` `select NAME in ...; do ... done`: default=`missing` posix=`missing`
  evidence: `bash-man-grammar-select-coproc.sh`
  note: select is currently not parsed/executed as shell keyword.
- `C2.GRAM.024` `coproc command`: default=`missing` posix=`missing`
  evidence: `bash-man-grammar-select-coproc.sh`
  note: coproc is currently not parsed/executed as shell keyword.

### Category 3

- `C3.EXP.001` `brace expansion {a,b}`: default=`missing` posix=`missing`
  evidence: `bash-man-expansion-brace-locale.sh`
  note: brace expansion currently literal.
- `C3.EXP.029` `locale translation quoting $"..."`: default=`missing` posix=`missing`
  evidence: `bash-man-expansion-brace-locale.sh`
  note: $"..." locale translation quoting currently not implemented.

### Category 4

- `C4.REDIR.012` `here-string <<<word`: default=`missing` posix=`missing`
  evidence: `bash-man-redir-here-string.sh`
  note: here-string <<< currently parse-error path.

## Unknown-Classified Rows (Need Evidence Narrowing/Execution)

- Category 1: 73 rows
- Category 2: 26 rows
- Category 3: 29 rows
- Category 4: 20 rows
- Category 6: 79 rows
- Category 7: 10 rows
- Category 8: 12 rows
- Category 9: 7 rows
- Category 10: 6 rows
- Category 11: 58 rows

## Dedicated Cases Added In This Pass

- `tests/compat/run_bash_invocation_option_matrix.sh`
- `tests/diff/cases/bash-man-grammar-core.sh`
- `tests/diff/cases/bash-man-grammar-select-coproc.sh`
- `tests/diff/cases/bash-man-expansion-core.sh`
- `tests/diff/cases/bash-man-expansion-brace-locale.sh`
- `tests/diff/cases/bash-man-expansion-process-subst.sh`
- `tests/diff/cases/bash-man-redir-here-string.sh`
- `tests/diff/cases/bash-man-redir-bash-ext.sh`
- `tests/diff/cases/bash-man-seto-surface.sh`
- `tests/diff/cases/bash-man-shopt-surface.sh`
- `tests/diff/cases/bash-man-variables-surface.sh`
