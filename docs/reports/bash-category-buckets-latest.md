# Bash Category Buckets Matrix

Generated: 2026-03-11 09:35:31Z

| Bucket | Name | Status | Gate |
|---|---|---|---|
| 1 | Invocation/startup/mode | covered | `/home/sam/Projects/pybash/tests/compat/run_startup_mode_matrix.sh` |
| 2 | Grammar/parser | covered | `/home/sam/Projects/pybash/tests/diff/run.sh --case man-ash-grammar-negative --case man-ash-grammar-reserved --case man-ash-grammar-word-matrix --case man-ash-prefix-suffix` |
| 3 | Expansion engine | covered | `/home/sam/Projects/pybash/tests/diff/run.sh --case man-ash-var-ops --case man-ash-var-ops-matrix --case man-ash-word-nesting --case man-ash-word-nesting-matrix --case man-ash-glob-matrix --case man-ash-glob-full-matrix` |
| 4 | Redirection/FD | covered | `/home/sam/Projects/pybash/tests/diff/run.sh --case man-ash-redir --case man-ash-heredoc-edges --case man-ash-redir-heredoc-matrix` |
| 5 | Builtins | covered | `STRICT=1 /home/sam/Projects/pybash/tests/compat/run_bash_builtin_matrix.sh` |
| 6 | Variables/state | covered | `MCTASH_DIAG_STYLE=bash PARITY_MIRROR_POSIX=1 /home/sam/Projects/pybash/tests/diff/run.sh --case man-bash-posix-01-core-state --case man-bash-posix-14-env-exec-flow` |
| 7 | Interactive UX | covered | `/home/sam/Projects/pybash/tests/compat/run_completion_interactive_matrix.sh && /home/sam/Projects/pybash/tests/compat/run_interactive_ux_matrix.sh` |
| 8 | Jobs/traps/signals | covered | `STRICT=1 /home/sam/Projects/pybash/tests/compat/run_jobs_interactive_matrix.sh && STRICT=1 /home/sam/Projects/pybash/tests/compat/run_trap_noninteractive_matrix.sh && STRICT=1 /home/sam/Projects/pybash/tests/compat/run_trap_interactive_matrix.sh` |
| 9 | Compatibility/restricted | covered | `/home/sam/Projects/pybash/tests/compat/run_startup_mode_matrix.sh` |

