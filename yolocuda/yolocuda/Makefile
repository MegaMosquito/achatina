# An app that calls the yolo detector, and pushes data to mqtt and kafka

SERVICE_NAME:="yolocuda"
SERVICE_VERSION:="1.0.0"

#
# Targets for building, developing, testing and cleaning this service
#

ARCH:=arm
_ARCH:=$(shell uname -p)
ifeq ($(_ARCH),'aarch64')
  ARCH:=arm64
endif
ifeq ($(_ARCH),'i386')
  ARCH:=amd64
endif

build: validate-dockerhubid
	docker build -t $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) -f ./Dockerfile.$(ARCH) .

# If HZN_DEVICE_ID is not set, use the hostname
HZN_DEVICE_ID := $(or $(HZN_DEVICE_ID),$(shell sh -c 'host `hostname`'))

# Get a host routed IP address (used only if CAM_URL not set)
HOST_IP:=$(word 4, $(shell sh -c 'host `hostname`'))

dev: validate-dockerhubid check-cam-url
	-docker rm -f ${SERVICE_NAME} 2>/dev/null || :
	docker run -it -v `pwd`:/outside \
	   -e HZN_DEVICE_ID="${HZN_DEVICE_ID}" \
	   -e HOST_IP="${HOST_IP}" \
	   -e CAM_URL="${CAM_URL}" \
	   -e EVENTSTREAMS_BROKER_URLS="${EVENTSTREAMS_BROKER_URLS}" \
	   -e EVENTSTREAMS_API_KEY="${EVENTSTREAMS_API_KEY}" \
	   -e EVENTSTREAMS_PUB_TOPIC="${EVENTSTREAMS_PUB_TOPIC}" \
	   --name ${SERVICE_NAME} \
	   --network mqtt-net --network-alias ${SERVICE_NAME} \
	   $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) /bin/sh

test: validate-dockerhubid check-cam-url
	-docker rm -f ${SERVICE_NAME} 2>/dev/null || :
	docker run --rm -d \
	   -e HZN_DEVICE_ID="${HZN_DEVICE_ID}" \
	   -e HOST_IP="${HOST_IP}" \
	   -e CAM_URL="${CAM_URL}" \
	   -e EVENTSTREAMS_BROKER_URLS="${EVENTSTREAMS_BROKER_URLS}" \
	   -e EVENTSTREAMS_API_KEY="${EVENTSTREAMS_API_KEY}" \
	   -e EVENTSTREAMS_PUB_TOPIC="${EVENTSTREAMS_PUB_TOPIC}" \
	   --name ${SERVICE_NAME} \
	   --network mqtt-net --network-alias ${SERVICE_NAME} \
	   $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION)

clean: validate-dockerhubid
	@docker rm -f ${SERVICE_NAME} 2>/dev/null || :
	@docker rmi $(DOCKERHUB_ID)/$(SERVICE_NAME):$(SERVICE_VERSION) 2>/dev/null || :
	@docker rmi $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) 2>/dev/null || :

#
# Targets for publishing this service to an Open-Horizon Exhange
#
# NOTE: You must install the Open-Horizon CLI in order to use these targets!
#

publish-service: validate-dockerhubid
	ARCH=$(shell hzn architecture) docker build -t $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) -f ./Dockerfile.$(ARCH) .
	ARCH=$(shell hzn architecture) DOCKER_IMAGE_BASE="$(DOCKERHUB_ID)/$(SERVICE_NAME)" hzn exchange service publish -f service.json --pull-image

publish-all-services: validate-dockerhubid
	ARCH=arm SERVICE_NAME="$(SERVICE_NAME)" SERVICE_VERSION="$(SERVICE_VERSION)"  docker build -t $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) -f ./Dockerfile.$(ARCH) .
	ARCH=arm SERVICE_NAME="$(SERVICE_NAME)" SERVICE_VERSION="$(SERVICE_VERSION)"  DOCKER_IMAGE_BASE="$(DOCKERHUB_ID)/$(SERVICE_NAME)" hzn exchange service publish -f service.json
	ARCH=arm64 SERVICE_NAME="$(SERVICE_NAME)" SERVICE_VERSION="$(SERVICE_VERSION)"  docker build -t $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) -f ./Dockerfile.$(ARCH) .
	ARCH=arm64 SERVICE_NAME="$(SERVICE_NAME)" SERVICE_VERSION="$(SERVICE_VERSION)"  DOCKER_IMAGE_BASE="$(DOCKERHUB_ID)/$(SERVICE_NAME)" hzn exchange service publish -f service.json
	ARCH=amd64 SERVICE_NAME="$(SERVICE_NAME)" SERVICE_VERSION="$(SERVICE_VERSION)"  docker build -t $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) -f ./Dockerfile.$(ARCH) .
	ARCH=amd64 SERVICE_NAME="$(SERVICE_NAME)" SERVICE_VERSION="$(SERVICE_VERSION)"  DOCKER_IMAGE_BASE="$(DOCKERHUB_ID)/$(SERVICE_NAME)" hzn exchange service publish -f service.json

#
# Sanity check targets
#

validate-dockerhubid:
	@if [ -z "${DOCKERHUB_ID}" ]; \
          then { echo "***** ERROR: \"DOCKERHUB_ID\" is not set!"; exit 1; }; \
          else echo "  NOTE: Using DockerHubID: \"${DOCKERHUB_ID}\""; \
        fi
	@sleep 1

check-cam-url:
	@if [ -z "${CAM_URL}" ]; \
          then echo "  Warning: \"CAM_URL\" is not set! Using default."; \
          else echo "  NOTE: Using camera URL: ${CAM_URL}"; \
        fi
	@sleep 1

check-kafka-creds:
	@if [ -z "${EVENTSTREAMS_BROKER_URLS}" ] || \
          [ -z "${EVENTSTREAMS_API_KEY}" ] || \
          [ -z "${EVENTSTREAMS_PUB_TOPIC}" ]; \
          then echo "  Warning: No EventStreams credentials found! Kafka publication is disabled."; \
          else echo "  NOTE: Publishing to topic: ${EVENTSTREAMS_PUB_TOPIC}"; \
        fi

.PHONY: build dev test clean publish-service publish-all-services validate-dockerhubid check-cam-url check-kafka-creds

