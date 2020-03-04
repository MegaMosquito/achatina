# A simple Makefile for the achatina YOLOv3 GPU example

help:
	@echo "Please see the \"README.md\" file for instructions."

test:
	@echo "Performing  local test (outside of Horizon)..."
	@if [ -z "${DOCKERHUB_ID}" ]; \
          then { echo "***** ERROR: \"DOCKERHUB_ID\" is not set!"; exit 1; }; \
          else echo "  NOTE: Using DockerHubID: \"${DOCKERHUB_ID}\""; \
        fi
	@if [ -z "${CAM_URL}" ]; \
	  then echo "  Warning: \"CAM_URL\" is not set! Using default."; \
	  else echo "  NOTE: Using camera URL: ${CAM_URL}"; \
	fi
	@if [ -z "${EVENTSTREAMS_BROKER_URLS}" ] || \
	  [ -z "${EVENTSTREAMS_API_KEY}" ] || \
	  [ -z "${EVENTSTREAMS_PUB_TOPIC}" ]; \
	  then echo "  Warning: No EventStreams credentials found! Kafka publication is disabled."; \
	  else echo "  NOTE: Publishing to topic: ${EVENTSTREAMS_PUB_TOPIC}"; \
	fi
	@echo "  NOTE: Building and starting the shared services..."
	make -C ../shared test
	@echo "  NOTE: Building and starting the local services..."
	make -C restyolov3gpu
	make -C restyolov3gpu test
	make -C yv3g
	make -C yv3g test

publish-services:
	@echo "Building and publishing the local services..."
	@if [ -z "${DOCKERHUB_ID}" ]; \
          then { echo "***** ERROR: \"DOCKERHUB_ID\" is not set!"; exit 1; }; \
          else echo "  NOTE: Using DockerHubID: \"${DOCKERHUB_ID}\""; \
        fi
	@if [ -z "${HZN_ORG_ID}" ]; \
	  then { echo "***** ERROR: \"HZN_ORG_ID\" is not set!"; exit 1; }; \
	  else echo "  NOTE: Using Exchange Org ID: \"${HZN_ORG_ID}\""; \
	fi
	@sleep 2
	make -C restyolov3gpu
	make -C restyolov3gpu push
	make -C restyolov3gpu publish-service
	make -C yv3g
	make -C yv3g push
	make -C yv3g publish-service
	@echo "  NOTE: the shared services must also be published (restcam, mqtt, monitor)."
	@echo "  NOTE: after this, also please publish a pattern or policies."

publish-pattern:
	@echo "Publishing a pattern for the shared and local services..."
	@if [ -z "${DOCKERHUB_ID}" ]; \
          then { echo "***** ERROR: \"DOCKERHUB_ID\" is not set!"; exit 1; }; \
          else echo "  NOTE: Using DockerHubID: \"${DOCKERHUB_ID}\""; \
        fi
	hzn exchange pattern publish -f patterns/pattern-yv3.json

register:
	hzn register --pattern "${HZN_ORG_ID}/pattern-yv3" --input-file ./input.json

clean:
	make -C restyolov3gpu clean
	make -C yv3g clean

deep-clean:
	-docker rm -f `docker ps -aq` 2>/dev/null || :
	-docker network rm mqtt-net 2>/dev/null || :
	-docker rmi -f `docker images -aq` 2>/dev/null || :

.PHONY: help test publish-services publish-pattern register clean deep-clean

