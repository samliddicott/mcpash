RUN_TIMEOUT ?= 120

.PHONY: busybox-fetch busybox-ash-test busybox-clean test

test:	busybox-ash-test

busybox-fetch:
	@./run_busybox_ash.sh fetch

busybox-ash-test:
	@RUN_TIMEOUT=$(RUN_TIMEOUT) ./run_busybox_ash.sh run

busybox-clean:
	@rm -rf ../../tests/busybox
	@echo "Removed ../../tests/busybox"
