# A monitor program for the achatina examples

SERVICE_NAME:="monitor"
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

dev: validate-dockerhubid
	-docker rm -f $(SERVICE_NAME) 2>/dev/null || :
	docker run -it -v `pwd`:/outside \
           -p 0.0.0.0:5200:5200 \
           --name ${SERVICE_NAME} \
           --network mqtt-net --network-alias ${SERVICE_NAME} \
           $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) /bin/sh

test: validate-dockerhubid
	-docker rm -f $(SERVICE_NAME) 2>/dev/null || :
	docker run -d \
           -p 0.0.0.0:5200:5200 \
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

.PHONY: build dev test clean publish-service publish-all-services validate-dockerhubid

