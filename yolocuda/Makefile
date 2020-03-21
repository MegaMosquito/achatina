# A simple Makefile for the achatina YOLO (CUDA) example

test: validate-dockerhubid check-cam-url
	@echo "Performing local test of the YOLO (for CUDA) example..."
	$(MAKE) -C ../shared test
	$(MAKE) -C restyolocuda
	$(MAKE) -C restyolocuda test
	$(MAKE) -C yolocuda
	$(MAKE) -C yolocuda test

clean:
	$(MAKE) -C restyolocuda clean
	$(MAKE) -C yolocuda clean

ANAX_CONTAINER:=$(word 1, $(shell sh -c "docker ps | grep 'openhorizon/amd64_anax'"))
stop:
	@echo "Stopping and removing Docker containers."
	-docker rm -f `docker ps -aq | grep -v "${ANAX_CONTAINER}"` 2>/dev/null || :

ANAX_IMAGE:=$(word 3, $(shell sh -c "docker images | grep 'openhorizon/amd64_anax'"))
foo:
deep-clean: clean stop
	@echo "Removing Docker container images."
	-docker rmi -f `docker images -aq | grep -v "${ANAX_IMAGE}"` 2>/dev/null || :
	@echo "Removing the Docker network used for testing."
	-docker network rm mqtt-net 2>/dev/null || :

#
# Targets for publishing this service to an Open-Horizon Exhange and for registering edge devices with Open-Horizon
#
# NOTE: You must install the Open-Horizon CLI in order to use these targets!
#

publish-all-services: validate-dockerhubid validate-org
	@echo "Building and publishing the local services for all architectures..."
	ARCH=arm $(MAKE) -C restyolocuda
	ARCH=arm64 $(MAKE) -C restyolocuda
	ARCH=amd64 $(MAKE) -C restyolocuda
	$(MAKE) -C restyolocuda publish-all-services
	ARCH=arm $(MAKE) -C yolocuda
	ARCH=arm64 $(MAKE) -C yolocuda
	ARCH=amd64 $(MAKE) -C yolocuda
	$(MAKE) -C yolocuda publish-all-services
	@echo "  NOTE: the shared services must also be published (restcam, mqtt, monitor)."
	@echo "  NOTE: after this, also please publish a pattern or policies."

publish-all-patterns: validate-org
	@echo "Publishing all supported deployment patterns for this example..."
	hzn exchange pattern publish -f deployment/pattern-yolocuda.json

publish-all-policies: validate-org
	@echo "Publishing business/deployment policies for this example..."
	hzn exchange business addpolicy -f ./deployment/example-business-policy.json

register-pattern: check-cam-url
	hzn register --pattern "${HZN_ORG_ID}/pattern-yolocuda --input-file ./deployment/example-input-file.json

register-policy:
	hzn register --policy ./deployment/example-node-policy.json

#
# Sanity check targets
#

validate-dockerhubid:
	@if [ -z "${DOCKERHUB_ID}" ]; \
          then { echo "***** ERROR: \"DOCKERHUB_ID\" is not set!"; exit 1; }; \
          else echo "  NOTE: Using DockerHubID: \"${DOCKERHUB_ID}\""; \
        fi
	@sleep 1

validate-org:
	@if [ -z "${HZN_ORG_ID}" ]; \
	  then { echo "***** ERROR: \"HZN_ORG_ID\" is not set!"; exit 1; }; \
	  else echo "  NOTE: Using Exchange Org ID: \"${HZN_ORG_ID}\""; \
	fi
	@sleep 1

check-cam-url:
	@if [ -z "${CAM_URL}" ]; \
	  then echo "  Warning: \"CAM_URL\" is not set! Using default."; \
	  else echo "  NOTE: Using camera URL: ${CAM_URL}"; \
	fi
	@sleep 1

.PHONY: test clean deep-clean publish-all-services publish-all-patterns publish-all-policies register-pattern register-policy validate-dockerhubid validate-org check-cam-url

