# Bridge Test Trace (Milestone-2)

This table links bridge requirements to concrete regression cases in `tests/regressions/run.sh`.

| Area | Requirement slice | Regression cases |
|---|---|---|
| Phase 1 | `py` statement/expr/call/capture/status | `py_statement_exec`, `py_eval_print`, `py_callable_dispatch`, `py_stdout_capture_var`, `py_return_capture_var`, `py_exception_status` |
| Phase 1 | Structured exception vars (`-x`) | `py_structured_exception` |
| Phase 2 | `PYTHON ... END_PYTHON` block parse | `python_block_basic`, `python_block_missing_terminator` |
| Phase 2 | Dedent / no-dedent | `python_block_dedent_default`, `python_block_no_dedent` |
| Phase 2/9 | Embedded parse robustness and shell integration | `python_block_parser_robust_parens_quotes`, `python_block_in_command_substitution`, `python_block_pipeline`, `python_block_inline_end_pipeline` |
| Phase 3 | `sh.vars` / attrs / declare / env mapping | `py_sh_vars_mapping`, `py_sh_vars_attrs`, `py_sh_vars_declare_integer`, `py_sh_env_exported` |
| Phase 3 | Typed Python-side list/dict projections | `py_sh_vars_list_roundtrip`, `py_sh_vars_dict_roundtrip`, `py_sh_vars_typed_cleared_on_shell_write` |
| Phase 4 | `sh.fn` + `from ... import ...` wrappers | `py_sh_fn_callable_from_shell`, `py_sh_fn_assignment_declare_wrapper`, `py_from_import_callable_wrapper` |
| Phase 5 | `sh()` / `run` / `popen` | `py_sh_call_basic`, `py_sh_run_capture_output`, `py_sh_run_check_error`, `py_sh_popen_capture` |
| Phase 6 | ties (`py -t/-u`, `sh.tie`) | `py_tie_scalar_roundtrip`, `py_tie_integer_cast`, `py_tie_readonly_write_error` |
| Phase 7 | `shared` + `sh.shared` + cross-process visibility | `shared_builtin_basic`, `shared_cross_process_visibility` |
| Phase 8 | `sh.stack` frame presence and ordering | `py_sh_stack_contains_function`, `py_sh_stack_innermost_is_python`, `py_sh_stack_contains_command_subst_frame` |
| Phase 9 | interrupt path | `py_interrupt_status_130` |

Related full-suite gates:

- BusyBox ash corpus via `src/tests/run_busybox_ash.sh`
- Oil subset via `src/tests/run_oil_subset.sh`
- Combined gate via `scripts/check_conformance.sh`
