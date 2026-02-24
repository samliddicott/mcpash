RUN_TIMEOUT ?= 120

.PHONY: busybox-fetch busybox-ash-test busybox-clean oil-fetch oil-subset-test oil-clean test

test:	busybox-ash-test

busybox-fetch:
	@./run_busybox_ash.sh fetch

busybox-ash-test:
	@RUN_TIMEOUT=$(RUN_TIMEOUT) ./run_busybox_ash.sh run

busybox-clean:
	@rm -rf ../../tests/busybox
	@echo "Removed ../../tests/busybox"

oil-fetch:
	@./run_oil_subset.sh fetch

oil-subset-test:
	@MAX_CASES=$(MAX_CASES) ./run_oil_subset.sh run

oil-clean:
	@rm -rf ../../tests/oil
	@echo "Removed ../../tests/oil"
