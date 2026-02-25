RUN_TIMEOUT ?= 1200
BUSYBOX_MIN_OK ?= 357
BUSYBOX_MAX_FAIL ?= 0
OIL_MIN_PASS ?= 245
OIL_MAX_FAIL ?= 0

.PHONY: regressions conformance conformance-full conformance-quick

regressions:
	@./tests/regressions/run.sh

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
