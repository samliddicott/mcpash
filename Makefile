RUN_TIMEOUT ?= 1200
BUSYBOX_MIN_OK ?= 357
BUSYBOX_MAX_FAIL ?= 0
OIL_MIN_PASS ?= 245
OIL_MAX_FAIL ?= 0
SUMMARY_FILE ?= docs/reports/parity-summary.json

.PHONY: regressions bridge-conformance diff-conformance diff-parity-matrix read-matrix semantic-matrix jobs-interactive-matrix trap-noninteractive-matrix trap-interactive-matrix trap-variant-matrix completion-interactive-matrix interactive-ux-matrix interactive-sigint-matrix interactive-tmout-matrix man-detail-audit startup-mode-matrix bash-invocation-option-matrix category-buckets-matrix bash-builtin-matrix busybox-conformance parity-summary parity-summary-validate perf-baseline perf-compare perf-variation stress-race stress-bridge compat-posix-bash compat-posix-bash-strict bash-posix-man-matrix bash-posix-upstream-matrix bash-tests-fetch compliance-truth-check compliance-truth-gate conformance conformance-full conformance-quick test-all

regressions:
	@./tests/regressions/run.sh

bridge-conformance:
	@./tests/bridge/run.sh

diff-conformance:
	@./tests/diff/run.sh

diff-parity-matrix:
	@./tests/diff/run_parity_matrix.sh

read-matrix:
	@./tests/diff/run_read_matrix.sh

semantic-matrix:
	@./tests/compat/run_semantic_matrix.sh

jobs-interactive-matrix:
	@./tests/compat/run_jobs_interactive_matrix.sh

trap-noninteractive-matrix:
	@./tests/compat/run_trap_noninteractive_matrix.sh

trap-interactive-matrix:
	@./tests/compat/run_trap_interactive_matrix.sh

trap-variant-matrix:
	@./tests/compat/run_trap_variant_matrix.sh

completion-interactive-matrix:
	@./tests/compat/run_completion_interactive_matrix.sh

interactive-ux-matrix:
	@./tests/compat/run_interactive_ux_matrix.sh

interactive-sigint-matrix:
	@./tests/compat/run_interactive_sigint_matrix.sh

interactive-tmout-matrix:
	@./tests/compat/run_interactive_tmout_matrix.sh

man-detail-audit:
	@./tests/diff/run.sh --case bash-man-param-transform-ops --case bash-man-timeformat --case bash-man-bash_xtracefd
	@./tests/compat/run_interactive_ux_matrix.sh
	@./tests/compat/run_interactive_tmout_matrix.sh
	@./tests/compat/run_interactive_sigint_matrix.sh

startup-mode-matrix:
	@./tests/compat/run_startup_mode_matrix.sh

bash-invocation-option-matrix:
	@./tests/compat/run_bash_invocation_option_matrix.sh

category-buckets-matrix:
	@./tests/compat/run_bash_category_bucket_matrix.sh

bash-builtin-matrix:
	@./tests/compat/run_bash_builtin_matrix.sh

busybox-conformance:
	@RUN_TIMEOUT=$(RUN_TIMEOUT) RUN_MODULE_TIMEOUT=$(RUN_TIMEOUT) ./src/tests/run_busybox_ash.sh run

parity-summary:
	@RUN_TIMEOUT=$(RUN_TIMEOUT) RUN_MODULE_TIMEOUT=$(RUN_TIMEOUT) ./scripts/run_parity_summary.sh "$(SUMMARY_FILE)"

parity-summary-validate: parity-summary
	@./scripts/validate_parity_summary.py "$(SUMMARY_FILE)"

perf-baseline:
	@./scripts/benchmark_parity.sh docs/reports/perf-baseline.json

perf-compare:
	@./scripts/compare_perf_baseline.sh docs/reports/perf-baseline.json

perf-variation:
	@./scripts/analyze_perf_variation.sh docs/reports/perf-variation.json

stress-race:
	@./tests/stress/race.sh

stress-bridge:
	@./tests/stress/bridge.sh

compat-posix-bash:
	@./tests/compat/run_posix_bash_compat_matrix.sh

compat-posix-bash-strict:
	@STRICT=1 ./tests/compat/run_posix_bash_compat_matrix.sh

bash-posix-man-matrix:
	@./tests/compat/run_bash_posix_man_matrix.sh

bash-posix-upstream-matrix:
	@./tests/compat/run_bash_posix_upstream_matrix.sh

bash-tests-fetch:
	@./tests/bash/fetch_upstream_tests.sh

compliance-truth-check:
	@python3 ./scripts/check_compliance_truth.py

compliance-truth-gate:
	@$(MAKE) bash-invocation-option-matrix
	@$(MAKE) bash-posix-man-matrix
	@$(MAKE) bash-posix-upstream-matrix
	@$(MAKE) bash-builtin-matrix
	@$(MAKE) compliance-truth-check

conformance: conformance-full

conformance-full:
	@RUN_TIMEOUT=$(RUN_TIMEOUT) \
	RUN_MODULE_TIMEOUT=$(RUN_TIMEOUT) \
	BUSYBOX_MIN_OK=$(BUSYBOX_MIN_OK) \
	BUSYBOX_MAX_FAIL=$(BUSYBOX_MAX_FAIL) \
	OIL_MIN_PASS=$(OIL_MIN_PASS) \
	OIL_MAX_FAIL=$(OIL_MAX_FAIL) \
	./scripts/check_conformance.sh

conformance-quick:
	@./tests/regressions/run.sh
	@./src/tests/run_oil_subset.sh run shell-grammar command-parsing

test-all:
	@$(MAKE) diff-parity-matrix
	@$(MAKE) compat-posix-bash-strict
	@$(MAKE) bash-builtin-matrix
	@$(MAKE) bash-posix-man-matrix
	@$(MAKE) conformance-full
