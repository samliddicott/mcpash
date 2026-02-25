RUN_TIMEOUT ?= 1200
BUSYBOX_MIN_OK ?= 357
BUSYBOX_MAX_FAIL ?= 0
OIL_MIN_PASS ?= 245
OIL_MAX_FAIL ?= 0

.PHONY: regressions conformance

regressions:
	@./tests/regressions/run.sh

conformance:
	@RUN_TIMEOUT=$(RUN_TIMEOUT) \
	BUSYBOX_MIN_OK=$(BUSYBOX_MIN_OK) \
	BUSYBOX_MAX_FAIL=$(BUSYBOX_MAX_FAIL) \
	OIL_MIN_PASS=$(OIL_MIN_PASS) \
	OIL_MAX_FAIL=$(OIL_MAX_FAIL) \
	./scripts/check_conformance.sh
