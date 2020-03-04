# A simple Makefile for the achatina examples

help:
	@echo "Please see the \"README.md\" file for instructions."

test: test-yv3g

test-shared-services:
	@echo "Building all of the shared services..."
	make -C shared test

publish-services:
	@echo "Building and publishing the shared services..."
	make -C shared publish-services
	@echo "Building and publishing all the services..."
	make -C yv3g publish-services
	make -C yv3c publish-services

clean:
	make -C shared clean
	make -C yv3g clean
	make -C yv3c clean

deep-clean:
	-docker rm -f `docker ps -aq` 2>/dev/null || :
	-docker network rm mqtt-net 2>/dev/null || :
	-docker rmi -f `docker images -aq` 2>/dev/null || :

.PHONY: help test test-shared-services publish-services clean deep-clean

# YOLOv3 for GPU
test-yv3g: test-shared-services
	@echo "Performing  local test (outside of Horizon) for YOLOv3 (GPU)..."
	make -C yv3g test
register-yv3g:
	make -C yv3g register
.PHONY: test-yv3g register-yv3g

# YOLOv3 for CPU
test-yv3c: test-shared-services
	@echo "Performing  local test (outside of Horizon) for YOLOv3 (CPU)..."
	make -C yv3c test
register-yv3c:
	make -C yv3c register
.PHONY: test-yv3c register-yv3c



