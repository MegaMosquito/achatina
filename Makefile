# A simple Makefile for the achatina examples

help:
	@echo "Please see the \"README.md\" file for instructions."

test: test-yologpu

test-shared-services:
	@echo "Building all of the shared services..."
	make -C shared test

publish-services:
	@echo "Building and publishing the shared services..."
	make -C shared publish-services
	@echo "Building and publishing all the services..."
	make -C yologpu publish-services
	make -C yolocpu publish-services

clean:
	make -C shared clean
	make -C yologpu clean
	make -C yolocpu clean

deep-clean:
	-docker rm -f `docker ps -aq` 2>/dev/null || :
	-docker network rm mqtt-net 2>/dev/null || :
	-docker rmi -f `docker images -aq` 2>/dev/null || :

.PHONY: help test test-shared-services publish-services clean deep-clean

# YOLOv3 for GPU
test-yologpu: test-shared-services
	@echo "Performing  local test (outside of Horizon) for YOLOv3 (GPU)..."
	make -C yologpu test
register-yologpu:
	make -C yologpu register
.PHONY: test-yologpu register-yologpu

# YOLOv3 for CPU
test-yolocpu: test-shared-services
	@echo "Performing  local test (outside of Horizon) for YOLOv3 (CPU)..."
	make -C yolocpu test
register-yolocpu:
	make -C yolocpu register
.PHONY: test-yolocpu register-yolocpu



