#
# restcam
#
# This container provides a basic REST camera service. It leverages the
# "fswebcam" (http://manpages.ubuntu.com/manpages/bionic/man1/fswebcam.1.html)
# utility to access a local camera, and provide images over HTTP. If anything
# goes wrong with the camera access, a static image of a few people is
# provided instead.
#
# The "restcam" contaiiner provides service on port 80. I also expose this
# service on the host loopback interface (127.0.0.1) at port 8888. Locally
# running host processes can access the service using the loopback. I also
# bind to an interface on the Docker bridge network named "cam-net". You
# can therefore also use this camera service from other running containers
# by attaching them to the "cam-net" bridge network. Once you do that you
# will be able to use the network name "restcam" to access the camera
# service on port 80 there.
#
# Note that fswebcam is painfully slow (often taking several seconds to
# return a single image).
#
# Written by Glen Darling, Oct 2020.
#

# Include the make file containing all the check-* targets
include ../../checks.mk

SERVICE_NAME:="restcam"
SERVICE_VERSION:="1.1.0"

# These statements automatically configure some environment variables
ARCH:=$(shell ../../helper -a)

# Optionally configure a camera device address in CAM_DEVICE in your shell
# environment. The line below just configues a default camera device address to
# be the standard default Video-4-Linux-v2 (V4L2) camera device address. This
# default will only be used if CAM_DEVICE is not set in your environment.
DEFAULT_CAM_DEVICE:="V4L2:/dev/video0"
# Similarly, this device bind is added to `docker run` with `--device`:
DEFAULT_DEVICE_BIND:="/dev/video0"

# You may also optionally define these variables in your shell environment:
#     CAM_DELAY_SEC, CAM_OUT_WIDTH, CAM_OUT_HEIGHT
# See the "cam.sh" file to see how these are passed to "fswebcam", and see the
# fswebcam documentation to see how they are used.

build: check-dockerhubid
	docker build -t $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) -f ./Dockerfile.$(ARCH) .

run: check-dockerhubid
	-docker network create cam-net 2>/dev/null || :
	-docker rm -f $(SERVICE_NAME) 2>/dev/null || :
	docker run -d \
           -p 127.0.0.1:8888:80 \
           --privileged \
           --device $(DEFAULT_DEVICE_BIND) \
           -e CAM_DEVICE=$(if $(CAM_DEVICE),$(CAM_DEVICE),$(DEFAULT_CAM_DEVICE)) \
           -e CAM_DELAY_SEC="${CAM_DELAY_SEC}" \
           -e CAM_OUT_WIDTH="${CAM_OUT_WIDTH}" \
           -e CAM_OUT_HEIGHT="${CAM_OUT_HEIGHT}" \
           --name ${SERVICE_NAME} \
           --network cam-net --network-alias $(SERVICE_NAME) \
           --mount type=tmpfs,destination=/app \
           $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION)

# This target mounts this code dir in the container, useful for development.
dev: check-dockerhubid build
	-docker network create cam-net 2>/dev/null || :
	-docker rm -f $(SERVICE_NAME) 2>/dev/null || :
	docker run -it -v `pwd`:/outside \
           -p 127.0.0.1:8888:80 \
           --privileged \
           --device $(DEFAULT_DEVICE_BIND) \
           -e CAM_DEVICE=$(if $(CAM_DEVICE),$(CAM_DEVICE),$(DEFAULT_CAM_DEVICE)) \
           -e CAM_DELAY_SEC="${CAM_DELAY_SEC}" \
           -e CAM_OUT_WIDTH="${CAM_OUT_WIDTH}" \
           -e CAM_OUT_HEIGHT="${CAM_OUT_HEIGHT}" \
           --name ${SERVICE_NAME} \
           --network cam-net --network-alias $(SERVICE_NAME) \
           --mount type=tmpfs,destination=/app \
           $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) /bin/bash

# =============================================================================
# To perform a quick self-test of the "restcam" service:
#    1. start a "restcam" service instance: `make run`
#    2. in a terminal on the host, HTTP GET a test image: `make test`
#    3. you should see the file "test.jpg" appear in this directory
#    4. optionally inspect the "test.jpg" file in a browser or iimage viewer
#    5. optionally, in a terminal, time getting 10 images: `make timetest`
#    6. terminate the "restcam" service: `make stop`
# =============================================================================
test:
	@echo "Attempting to retrieve an image from the REST service..."
	curl -sS http://localhost:8888/ > ./test.jpg
	-ls -l ./test.jpg

timetest:
	@echo "Attempting to retrieve 10 images from the REST service..."
	bash -c "time sh -c '\
	curl -sS http://localhost:8888/ > ./test.jpg; rm ./test.jpg;\
	curl -sS http://localhost:8888/ > ./test.jpg; rm ./test.jpg;\
	curl -sS http://localhost:8888/ > ./test.jpg; rm ./test.jpg;\
	curl -sS http://localhost:8888/ > ./test.jpg; rm ./test.jpg;\
	curl -sS http://localhost:8888/ > ./test.jpg; rm ./test.jpg;\
	curl -sS http://localhost:8888/ > ./test.jpg; rm ./test.jpg;\
	curl -sS http://localhost:8888/ > ./test.jpg; rm ./test.jpg;\
	curl -sS http://localhost:8888/ > ./test.jpg; rm ./test.jpg;\
	curl -sS http://localhost:8888/ > ./test.jpg; rm ./test.jpg;\
	curl -sS http://localhost:8888/ > ./test.jpg; rm ./test.jpg;\
	curl -sS http://localhost:8888/ > ./test.jpg; rm ./test.jpg;\
	'"


stop: check-dockerhubid
	@docker rm -f ${SERVICE_NAME} 2>/dev/null || :

clean: check-dockerhubid
	-docker rm -f ${SERVICE_NAME} 2>/dev/null || :
	-docker rmi $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) 2>/dev/null || :
	-docker network rm cam-net 2>/dev/null || :

.PHONY: build run dev test stop clean

