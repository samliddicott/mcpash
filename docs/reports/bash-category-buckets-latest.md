# Bash Category Buckets Matrix

Generated: 2026-03-06

| Bucket | Name | Status | Gate | Notes |
|---|---|---|---|---|
| 1 | Invocation/startup/mode | covered | `/home/sam/Projects/pybash/tests/compat/run_startup_mode_matrix.sh` + `/home/sam/Projects/pybash/tests/compat/run_bash_invocation_option_matrix.sh` | Startup and invocation-option matrices are green. |
| 2 | Grammar/parser | covered | `/home/sam/Projects/pybash/tests/diff/run.sh --case man-ash-grammar-negative --case man-ash-grammar-reserved --case man-ash-grammar-word-matrix --case man-ash-prefix-suffix` |  |
| 3 | Expansion engine | covered | `/home/sam/Projects/pybash/tests/diff/run.sh --case man-ash-var-ops --case man-ash-var-ops-matrix --case man-ash-word-nesting --case man-ash-word-nesting-matrix --case man-ash-glob-matrix --case man-ash-glob-full-matrix --case bash-man-param-transform-ops --case bash-man-param-transform-ops-variants --case bash-man-param-transform-prompt --case bash-man-param-transform-prompt-escapes` | `${v@op}` scalar/positional/array/prompt-transform lanes are now covered with dedicated bash-compat differential evidence. |
| 4 | Redirection/FD | covered | `/home/sam/Projects/pybash/tests/diff/run.sh --case man-ash-redir --case man-ash-heredoc-edges --case man-ash-redir-heredoc-matrix` |  |
| 5 | Builtins | covered | `STRICT=1 /home/sam/Projects/pybash/tests/compat/run_bash_builtin_matrix.sh` + `/home/sam/Projects/pybash/tests/compat/run_bash_posix_upstream_matrix.sh` | Builtin matrix and upstream POSIX core lane are green. |
| 6 | Variables/state | partial | `MCTASH_DIAG_STYLE=bash PARITY_MIRROR_POSIX=1 /home/sam/Projects/pybash/tests/diff/run.sh --case man-bash-posix-01-core-state --case man-bash-posix-14-env-exec-flow --case bash-man-timeformat --case bash-man-bash_xtracefd && /home/sam/Projects/pybash/tests/compat/run_interactive_tmout_matrix.sh` | TIMEFORMAT is now covered; BASH_XTRACEFD and TMOUT remain explicit partial rows. |
| 7 | Interactive UX | partial | `/home/sam/Projects/pybash/tests/compat/run_completion_interactive_matrix.sh && /home/sam/Projects/pybash/tests/compat/run_interactive_ux_matrix.sh` | PS1 path is covered; PS2/PS4 escape depth remains a partial row (`C7.INT.01`). |
| 8 | Jobs/traps/signals | partial | `STRICT=1 /home/sam/Projects/pybash/tests/compat/run_jobs_interactive_matrix.sh && STRICT=1 /home/sam/Projects/pybash/tests/compat/run_trap_noninteractive_matrix.sh && STRICT=1 /home/sam/Projects/pybash/tests/compat/run_trap_interactive_matrix.sh && /home/sam/Projects/pybash/tests/compat/run_interactive_sigint_matrix.sh` | Interactive SIGINT continuation row (`C8.JOB.13`) remains partial. |
| 9 | Compatibility/restricted | covered | `/home/sam/Projects/pybash/tests/compat/run_startup_mode_matrix.sh` |  |
