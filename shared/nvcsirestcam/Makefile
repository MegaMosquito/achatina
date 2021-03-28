#
# restcam for NVIDIA Jetson MIPI CSI cameras
#
# This container provides a basic HTTP image service for a MIPI CSI camera
# attached to an NVIDIA Jetson. It leverages the `nvgstcapture-1.0` binary
# from the host (mounts it and the CSI camera's argus daemon socket path
# into the container), uses it to capture still images from the CSI camera
# then enables then to be retrieved using an HTTP GET like any web image.
#
# The "restcam" container provides service on port 80. I also expose this
# service on the host loopback interface (127.0.0.1) at port 8888. Locally
# running host processes can access the service using the loopback. I also
# bind to an interface on the Docker bridge network named "cam-net". You
# can therefore also use this camera service from other running containers
# by attaching them to the "cam-net" bridge network. Once you do that you
# will be able to use the network name "restcam" to access the camera
# service on port 80 at that address.
#
# Written by Glen Darling, Mar 2021.
#

# Include the make file containing all the check-* targets
include ../../checks.mk

# Using the same name for this service as the `fswebcam`-based version so it
# can be used as a direct drop-in replacement for that servcie on Jetsons.
SERVICE_NAME:="restcam"
SERVICE_VERSION:="1.0.0"

# These statements automatically configure some environment variables
ARCH:=$(shell ../../helper -a)

# You may optionally define these variables in your shell environment:
#    CAM_SOURCE (0-3), CAM_ORIENTATION (0-3), CAM_RES (2-12)
# See the "nvcsirestcam.py" source file to see how these are passed to
# "nvgstcapture-1.0", and see the nvgstcapture-1.0 documentation to
# see how they are used.

build: check-dockerhubid
	docker build -t $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) -f ./Dockerfile.$(ARCH) .

run: check-dockerhubid
	-docker network create cam-net 2>/dev/null || :
	-docker rm -f $(SERVICE_NAME) 2>/dev/null || :
	docker run -d \
           -p 127.0.0.1:8888:80 \
           --volume /usr/bin/nvgstcapture-1.0:/usr/bin/nvgstcapture-1.0 \
           --volume /tmp/argus_socket:/tmp/argus_socket \
           --volume /usr/lib/aarch64-linux-gnu:/usr/lib/aarch64-linux-gnu \
           -e CAM_SOURCE="$(CAM_SOURCE)" \
           -e CAM_ORIENTATION="$(CAM_ORIENTATION)" \
           -e CAM_RES="$(CAM_RES)" \
           --name ${SERVICE_NAME} \
           --network cam-net --network-alias $(SERVICE_NAME) \
           $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION)

# This target mounts this code dir in the container, useful for development.
dev: check-dockerhubid build
	@echo "Restarting the NVIDIA argus camera daemon..."
	sudo systemctl restart nvargus-daemon
	sleep 1
	-docker network create cam-net 2>/dev/null || :
	-docker rm -f $(SERVICE_NAME) 2>/dev/null || :
	docker run -it -v `pwd`:/outside \
           -p 127.0.0.1:8888:80 \
           --privileged \
           --volume /usr/bin/nvgstcapture-1.0:/usr/bin/nvgstcapture-1.0 \
           --volume /tmp/argus_socket:/tmp/argus_socket \
           --volume /usr/lib/aarch64-linux-gnu:/usr/lib/aarch64-linux-gnu \
           -e CAM_SOURCE="$(CAM_SOURCE)" \
           -e CAM_ORIENTATION="$(CAM_ORIENTATION)" \
           -e CAM_RES="$(CAM_RES)" \
           --name ${SERVICE_NAME} \
           --network cam-net --network-alias $(SERVICE_NAME) \
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

