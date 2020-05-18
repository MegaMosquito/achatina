# A simple Makefile for the achatina shared services

test:
	@echo "Building and starting the shared services..."
	make -C mqtt
	make -C mqtt test
	make -C restcam
	make -C restcam test
	make -C monitor
	make -C monitor test

build-local-services:
	@echo "Building the shared services for this architecture only..."
	make -C mqtt build
	make -C restcam build
	make -C monitor build

push-local-services:
	@echo "Docker-pushing the shared services for this architecture only..."
	make -C mqtt push
	make -C restcam push
	make -C monitor push

publish-local-services:
	@echo "Publishing the shared services for this architecture only..."
	make -C mqtt publish-service
	make -C restcam publish-service
	make -C monitor publish-service

publish-all-services:
	@echo "Building, pushing and publishing all of the shared services for all architectures..."
	make -C mqtt publish-all-services
	make -C restcam publish-all-services
	make -C monitor publish-all-services

clean:
	make -C mqtt clean
	make -C restcam clean
	make -C monitor clean

deep-clean:
	-docker rm -f `docker ps -aq` 2>/dev/null || :
	-docker network rm mqtt-net 2>/dev/null || :
	-docker rmi -f `docker images -aq` 2>/dev/null || :

.PHONY: help test publish-services clean deep-clean

