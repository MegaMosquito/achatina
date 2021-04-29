#
# Achatina V2
#
# This container uses an image source URL (empty, HTTP Image, or RTSP stream).
# It sends that URL to a visual inferencing plugin (cpu-only, cuda, openvino),
# then it normally publishes the results to an MQTT broker. If appropriately
# configured, it can also publish the results to a remote Kafka broker.
#
# Written by Glen Darling, Oct 2020.
#

# Include the make file containing all the check-* targets
include ../checks.mk

# Give this achatina service a name and version number
SERVICE_NAME:="achatina"
SERVICE_VERSION:="2.0.0"

# Optionally configure for MQTT publication. By default it publishes to a
# local MQTT broker using the URL, "mqtt", and publishes to the topic,
# "achatina". These configurations support the shared mqtt broker service
# and the shared "monitor" service.
# To send to a different MQTT broker or topic, set these variables:
#   MQTT_BROKER_URL, MQTT_BROKER_PORT, MQTT_PUB_TOPIC

# Optionally configure for Kafka publication. By defaltt it will not publish
# to any Kafka broker.
# To send to a MQTT broker, set these variables:
#   KAFKA_BROKER_URLS, KAFKA_API_KEY, KAFKA_PUB_TOPIC
# Note that KAFKA_BROKER_URLS is a string containing a comma-separated list
# of broker URLs in your Kafka broker pool.

# Optionally configure an INPUT_URL in your environment. You have 3 choices:
#   1. Don't set it and the restcam service or a static image will be used
#   2. Provide a valid HTTP image URL. E.g.:
#          https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Einstein_1921_by_F_Schmutzer_-_restoration.jpg/780px-Einstein_1921_by_F_Schmutzer_-_restoration.jpg
#   3. Provide a valid RTSP stream URL. E.g.:
#           rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov

# These statements automatically configure some environment variables
ARCH:=$(shell ../helper -a)
NODE:=$(shell ../helper -n)
HOST_IP:=$(shell ../helper -i)

# ***************************************************************************
#          IMPORTANT NOTEs REGARDING THE SHARED CAMERA SERVICES
# ***************************************************************************
# The shared camera services are optional. You can use any camera that can
# be exposed an HTTP image URL. The shared services, "restcam" for any
# Video for Linux v2 (V4L2) cameras, and "nvcsirestcam" for NVIDIA Jetson
# "CSI" (thin ribbon cable) cameras, are provided as a convenience. Feel
# free to use any other HTTP image URL and omit these containers
# The URL below sets the default input to be the restcam service, which binds
# by default binds itself to port 80 on docker bridge network "cam-net" with
# network alias "restcam". It also binds to the host loopback address at
# port 8888. One might think that one could use "http://localhost:8888" as
# the camera URL here in that case, but this would *not* work within any
# container because each container has its own loopback (distinct from the
# host loopback)! You can safely use "http://localhost:8888" in a host shell
# but to use the restcam service within a container you need to first attach
# the container to "cam-net" and then use “http://restcam:80/”. This is what
# the plug-in container do. This "achatina" container doe not do that because
# it never directly connects to the camera. Instead, it passed this URL to
# the plugin and the plugin connects to the camera. This is complex to
# understand but I think it is the best design for this plugin architecture.
DEFAULT_INPUT_URL:=“http://restcam:80/”

build: check-dockerhubid
	docker build -t $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) -f ./Dockerfile.$(ARCH) .

run: check-dockerhubid check-input-url
	-docker rm -f ${SERVICE_NAME} 2>/dev/null || :
	docker run --rm -d \
           -e ACHATINA_PLUGIN=$(or ${ACHATINA_PLUGIN},cpu-only) \
           -e HOST_IP="${HOST_IP}" \
           -e NODE="${NODE}" \
           -e MQTT_BROKER_URL="${MQTT_BROKER_URL}" \
           -e MQTT_BROKER_PORT="${MQTT_BROKER_PORT}" \
           -e MQTT_PUB_TOPIC="${MQTT_PUB_TOPIC}" \
           -e KAFKA_BROKER_URLS="${KAFKA_BROKER_URLS}" \
           -e KAFKA_API_KEY="${KAFKA_API_KEY}" \
           -e KAFKA_PUB_TOPIC="${KAFKA_PUB_TOPIC}" \
           -e INPUT_URL=$(or ${INPUT_URL},${DEFAULT_INPUT_URL}) \
           --name ${SERVICE_NAME} \
           --network mqtt-net --network-alias ${SERVICE_NAME} \
           $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION)

# This target mounts this code dir in the container, useful for development.
dev: check-dockerhubid check-input-url
	-docker rm -f ${SERVICE_NAME} 2>/dev/null || :
	docker run -it -v `pwd`:/outside \
           -e ACHATINA_PLUGIN=$(or ${ACHATINA_PLUGIN},cpu-only) \
           -e HOST_IP="${HOST_IP}" \
           -e NODE="${NODE}" \
           -e MQTT_BROKER_URL="${MQTT_BROKER_URL}" \
           -e MQTT_BROKER_PORT="${MQTT_BROKER_PORT}" \
           -e MQTT_PUB_TOPIC="${MQTT_PUB_TOPIC}" \
           -e KAFKA_BROKER_URLS="${KAFKA_BROKER_URLS}" \
           -e KAFKA_API_KEY="${KAFKA_API_KEY}" \
           -e KAFKA_PUB_TOPIC="${KAFKA_PUB_TOPIC}" \
           -e INPUT_URL=$(or ${INPUT_URL},${DEFAULT_INPUT_URL}) \
           --name ${SERVICE_NAME} \
           --network mqtt-net --network-alias ${SERVICE_NAME} \
           $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) sh

stop: check-dockerhubid
	-docker rm -f ${SERVICE_NAME} 2>/dev/null || :

clean: check-dockerhubid
	-docker rm -f ${SERVICE_NAME} 2>/dev/null || :
	-docker rmi $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) 2>/dev/null || :

.PHONY: build run dev stop clean

