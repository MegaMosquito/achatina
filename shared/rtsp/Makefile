# REWRITE ALL OF THIS
# rtsp
#
# This container provides a basic REST camera service. It leverages
# ffmpeg (https://www.ffmpeg.org/) to access an rtsp link, and provide 
# images over HTTP. If anything
# goes wrong with the rtsp link, a static image of a few people is
# provided instead.
#
# The "rtsp" container provides service on port 80. I also expose this
# service on the host loopback interface (127.0.0.1) at port 8888. Locally
# running host processes can access the service using the loopback. I also
# bind to an interface on the Docker bridge network named "cam-net". You
# can therefore also use this camera service from other running containers
# by attaching them to the "cam-net" bridge network. Once you do that you
# will be able to use the network name "rtsp" to access the camera
# service on port 80 there.
#
# Written by Clement Ng, Sep 2021.
#

# Include the make file containing all the check-* targets
include ../../checks.mk

SERVICE_NAME:="rtsp"
SERVICE_VERSION:="1.0.0"

# These statements automatically configure some environment variables
ARCH:=$(shell ../../helper -a)

# You may also optionally define these variables in your shell environment:
#     CAM_OUT_WIDTH, CAM_OUT_HEIGHT
# See the "cam.sh" file to see how these are passed to ffmpeg, and see the
# ffmpeg documentation to see how they are used.

build: check-dockerhubid
	docker build -t $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) -f ./Dockerfile.$(ARCH) .

run: check-dockerhubid
	-docker network create cam-net 2>/dev/null || :
	-docker rm -f $(SERVICE_NAME) 2>/dev/null || :
	docker run -d \
           -p 127.0.0.1:8888:80 \
           --privileged \
           -e RTSP_LINK="${RTSP_LINK}" \
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
           -e RTSP_LINK="${RTSP_LINK}" \
           -e CAM_OUT_WIDTH="${CAM_OUT_WIDTH}" \
           -e CAM_OUT_HEIGHT="${CAM_OUT_HEIGHT}" \
           --name ${SERVICE_NAME} \
           --network cam-net --network-alias $(SERVICE_NAME) \
           --mount type=tmpfs,destination=/app \
           $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) /bin/bash

# =============================================================================
# To perform a quick self-test of the "rtsp" service:
#    1. start a "rtsp" service instance: `make run`
#    2. in a terminal on the host, HTTP GET a test image: `make test`
#    3. you should see the file "test.jpg" appear in this directory
#    4. optionally inspect the "test.jpg" file in a browser or image viewer
#    5. optionally, in a terminal, time getting 10 images: `make timetest`
#    6. terminate the "rtsp" service: `make stop`
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

.PHONY: build run dev test timetest stop clean

