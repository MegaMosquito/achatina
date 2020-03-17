# A simple Makefile for the achatina examples

help:
	@echo "Please see the \"README.md\" file for instructions."

test: test-yolocpu

test-shared-services:
	@echo "Building all of the shared services..."
	make -C shared test

publish-services:
	@echo "Building and publishing the shared services..."
	make -C shared publish-services
	@echo "Building and publishing all the services..."
	make -C yolocpu publish-services
	make -C yolocuda publish-services

clean:
	make -C shared clean
	make -C yolocpu clean
	make -C yolocuda clean

deep-clean:
	-docker rm -f `docker ps -aq` 2>/dev/null || :
	-docker network rm mqtt-net 2>/dev/null || :
	-docker rmi -f `docker images -aq` 2>/dev/null || :

.PHONY: help test test-shared-services publish-services clean deep-clean

# YOLO for CPU
test-yolocpu: test-shared-services
	@echo "Performing  local test (outside of Horizon) for YOLOv3 (CPU)..."
	make -C yolocpu test
register-yolocpu:
	make -C yolocpu register
.PHONY: test-yolocpu register-yolocpu

# YOLO for CUDA
test-yolocuda: test-shared-services
	@echo "Performing  local test (outside of Horizon) for YOLO (CUDA)..."
	make -C yolocuda test
register-yolocuda:
	make -C yolocuda register
.PHONY: test-yolocuda register-yolocuda



