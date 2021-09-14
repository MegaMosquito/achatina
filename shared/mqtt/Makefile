#
# mqtt
#
# This container provides a basic MQTT broker that I use for *insecure*
# local (within a host only) inter-service communication.i
#
# Here I expose the *insecure* MQTT broker service port (1883) on the host
# loopback interface only (127.0.0.1). This broker is therefore accessible
# only by locally running host processes. I also bind this service to an
# interface on the Docker bridge network named "mqtt-net". You can therefore
# use this broker for inter-service communication on the host, by adding your
# containers to the "mqtt-net" bridge network. Once you do that you will be
# able to use the network name "mqtt" to access the broker on this network.
#
# NOTE: If you wish to use this broker for communication between hosts, and
# you therefore plan to expose service ports on the host network, then you
# would be wise to require user authentication, and expose only the MQTT
# broker's secure port (8883).
#
# Written by Glen Darling, Oct 2020.
#

# Include the make file containing all the check-* targets
include ../../checks.mk

# Give this service a name and version number
SERVICE_NAME:="mqtt"
SERVICE_VERSION:="1.1.0"

# These statements automatically configure some environment variables
ARCH:=$(shell ../../helper -a)

build: check-dockerhubid
	docker build -t $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) -f ./Dockerfile.$(ARCH) .

run: check-dockerhubid
	-docker network create mqtt-net 2>/dev/null || :
	-docker rm -f $(SERVICE_NAME) 2>/dev/null || :
	docker run --rm -d \
           -p 127.0.0.1:1883:1883 \
           --name $(SERVICE_NAME) \
           --network mqtt-net --network-alias $(SERVICE_NAME) \
           $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION)

dev: run


# =============================================================================
# To perform a quick self-test of the "mqtt" service:
#    0. Install the "mosquito-clients" package on the local host. E.g.:
#       sudo apt update && sudo apt install -y mosquitto-clients
#    1. start an "mqtt" service instance: `make run`
#    2. in one terminal on the host, subscribe with: `make test-sub`
#    3. then in another termninal on the host, publish with: `make test-pub`
#    4. you should see `Hello, world.` appear in the subscribed terminal
#    5. terminate the subscriber with Ctrl-C, then: `make stop`
# =============================================================================
test: test-sub
test-sub:
	mosquitto_sub -h 127.0.0.1 -p 1883 -t /detect
test-pub:
	mosquitto_pub -h 127.0.0.1 -p 1883 -t /detect -m 'Hello, world.'


stop: check-dockerhubid
	-docker rm -f ${SERVICE_NAME} 2>/dev/null || :

clean: check-dockerhubid
	-docker rm -f ${SERVICE_NAME} 2>/dev/null || :
	-docker rmi $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) 2>/dev/null || :
	-docker network rm mqtt-net 2>/dev/null || :

.PHONY: build run test test-sub test-pub stop clean

