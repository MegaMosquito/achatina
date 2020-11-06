# A plugin using openvino (requires Movidius VPU hardware, software, and config)

# Include the make file containing all the check-* targets
include ../../checks.mk

SERVICE_NAME:="openvino"
SERVICE_VERSION:="1.1.0"

# These statements automatically configure some environment variables
ARCH:=$(shell ../../helper -a)

# Download the OpenVino Yolo-V3 ML model
openvino-yolo-v3.zip:
	wget https://ibm.box.com/shared/static/3qn6jcvgqdrq3prspfrvp0tg8or85j7v.zip -O openvino-yolo-v3.zip

# Extract the model files from the zip archive
openvino-yolo-v3.xml: openvino-yolo-v3.zip
openvino-yolo-v3.bin: openvino-yolo-v3.zip
openvino-yolo-v3.labels: openvino-yolo-v3.zip
	unzip -j openvino-yolo-v3.zip

build: check-dockerhubid openvino-yolo-v3.xml openvino-yolo-v3.bin openvino-yolo-v3.labels
	@echo "Building the OpenVino plugin for Movidius hardware"
	docker build -t $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) -f ./Dockerfile.$(ARCH) .; \

run: check-dockerhubid
	-docker network create mqtt-net 2>/dev/null || :
	-docker network create cam-net 2>/dev/null || :
	-docker rm -f $(SERVICE_NAME) 2>/dev/null || :
	docker run --rm -d \
          --privileged -v /dev:/dev \
          --name $(SERVICE_NAME) \
          -e OPENVINO_PLUGIN=MYRIAD \
          --network=host \
          $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION)

dev: check-dockerhubid
	-docker network create mqtt-net 2>/dev/null || :
	-docker network create cam-net 2>/dev/null || :
	-docker rm -f $(SERVICE_NAME) 2>/dev/null || :
	docker run -it -v `pwd`:/outside \
          --privileged -v /dev:/dev \
          --name $(SERVICE_NAME) \
          -e OPENVINO_PLUGIN=MYRIAD \
          --privileged -v /dev:/dev \
          --network=host \
          $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) /bin/bash

stop: check-dockerhubid
	-docker rm -f ${SERVICE_NAME} 2>/dev/null || :

test:
	@echo "Attempting to test inferencing on an image from the restcam service..."
	curl -sS http://127.0.0.1:80/detect?url='http%3A%2F%2Flocalhost%3A8888%2F' | jq --raw-output --join-output '.detect.image' | base64 -d > ./inferred.jpg
	-ls -l ./inferred.jpg

clean: check-dockerhubid
	-docker rm -f ${SERVICE_NAME} 2>/dev/null || :
	-docker rmi $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) 2>/dev/null || :

.PHONY: build run dev stop test clean

