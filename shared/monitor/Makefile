#
# monitor
#
# This container was originally intended to simply be a debugging utility
# for achatina, but people seem to like it so now it's a fully fledged
# shared service. It is really only useful in the context of achatina
# since it is only able to consume, parse and render MQTT publications
# that have the JSON format that achatina produces.
#
# This container provides a web server on port 5200. This service is also
# exposed on all host interfaces so it can be easily viewed locally or
# remotely.
#
# Written by Glen Darling, Oct 2020.
#

# Include the make file containing all the check-* targets
include ../../checks.mk

# Give this service a name and version number
SERVICE_NAME:="monitor"
SERVICE_VERSION:="1.1.0"

# These statements automatically configure some environment variables
ARCH:=$(shell ../../helper -a)

build: check-dockerhubid
	docker build -t $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) -f ./Dockerfile.$(ARCH) .

run: check-dockerhubid
	-docker network create mqtt-net 2>/dev/null || :
	-docker rm -f $(SERVICE_NAME) 2>/dev/null || :
	docker run -d \
           -p 0.0.0.0:5200:5200 \
           --name ${SERVICE_NAME} \
           --network mqtt-net --network-alias ${SERVICE_NAME} \
           $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION)

dev: build check-dockerhubid
	-docker network create mqtt-net 2>/dev/null || :
	-docker rm -f $(SERVICE_NAME) 2>/dev/null || :
	docker run -it -v `pwd`:/outside \
           -p 0.0.0.0:5200:5200 \
           --name ${SERVICE_NAME} \
           --network mqtt-net --network-alias ${SERVICE_NAME} \
           $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) /bin/sh

stop: check-dockerhubid
	@docker rm -f ${SERVICE_NAME} 2>/dev/null || :

clean: check-dockerhubid
	@docker rm -f ${SERVICE_NAME} 2>/dev/null || :
	@docker rmi $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) 2>/dev/null || :

.PHONY: build run dev stop clean

