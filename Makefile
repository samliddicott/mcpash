RUN_TIMEOUT ?= 1200
BUSYBOX_MIN_OK ?= 357
BUSYBOX_MAX_FAIL ?= 0
OIL_MIN_PASS ?= 245
OIL_MAX_FAIL ?= 0
SUMMARY_FILE ?= docs/reports/parity-summary.json

.PHONY: regressions bridge-conformance diff-conformance diff-parity-matrix read-matrix busybox-conformance parity-summary parity-summary-validate perf-baseline perf-compare perf-variation stress-race stress-bridge compat-posix-bash compat-posix-bash-strict conformance conformance-full conformance-quick test-all

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
	@$(MAKE) conformance-full
