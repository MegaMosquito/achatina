# A simple Makefile for the achatina shared services

help:
	@echo "Please see the \"README.md\" file for instructions."

test:
	@echo "Performing  local test (outside of Horizon)..."
	@if [ -z "${DOCKERHUB_ID}" ]; \
          then { echo "***** ERROR: \"DOCKERHUB_ID\" is not set!"; exit 1; }; \
          else echo "  NOTE: Using DockerHubID: \"${DOCKERHUB_ID}\""; \
        fi
	@echo "  NOTE: Building and starting the shared services..."
	make -C mqtt
	make -C mqtt test
	make -C restcam
	make -C restcam test
	make -C monitor
	make -C monitor test

publish-services:
	@echo "Building and publishing the shared services..."
	@if [ -z "${DOCKERHUB_ID}" ]; \
          then { echo "***** ERROR: \"DOCKERHUB_ID\" is not set!"; exit 1; }; \
          else echo "  NOTE: Using DockerHubID: \"${DOCKERHUB_ID}\""; \
        fi
	@if [ -z "${HZN_ORG_ID}" ]; \
	  then { echo "***** ERROR: \"HZN_ORG_ID\" is not set!"; exit 1; }; \
	  else echo "  NOTE: Using Exchange Org ID: \"${HZN_ORG_ID}\""; \
	fi
	make -C mqtt
	make -C mqtt push
	make -C mqtt publish-service
	make -C restcam
	make -C restcam push
	make -C restcam publish-service
	make -C monitor
	make -C monitor push
	make -C monitor publish-service

clean:
	make -C mqtt clean
	make -C restcam clean
	make -C monitor clean

deep-clean:
	-docker rm -f `docker ps -aq` 2>/dev/null || :
	-docker network rm mqtt-net 2>/dev/null || :
	-docker rmi -f `docker images -aq` 2>/dev/null || :

.PHONY: help test publish-services clean deep-clean

