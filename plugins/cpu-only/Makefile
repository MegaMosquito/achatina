# A yolo plugin using CPU-only (should run anywhere)
  
# Include the make file containing all the check-* targets
include ../../checks.mk

SERVICE_NAME:="cpu-only"
SERVICE_VERSION:="1.1.0"

# These statements automatically configure some environment variables
ARCH:=$(shell ../../helper -a)

build: check-dockerhubid
	@echo "Building the CPU-only plugin (NOTE: should run anywhere)"
	docker build -t $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) -f ./Dockerfile.$(ARCH) .

run: check-dockerhubid
	-docker network create mqtt-net 2>/dev/null || :
	-docker network create cam-net 2>/dev/null || :
	-docker rm -f $(SERVICE_NAME) 2>/dev/null || :
	docker create --rm \
          -p 127.0.0.1:5252:80 \
          --name $(SERVICE_NAME) \
          --network mqtt-net --network-alias $(SERVICE_NAME) \
          $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION)
	docker network connect cam-net $(SERVICE_NAME) --alias $(SERVICE_NAME)
	docker start $(SERVICE_NAME)

dev: check-dockerhubid build
	-docker network create mqtt-net 2>/dev/null || :
	-docker network create cam-net 2>/dev/null || :
	-docker rm -f $(SERVICE_NAME) 2>/dev/null || :
	docker create -it -v `pwd`:/outside \
          -p 127.0.0.1:5252:80 \
          --name $(SERVICE_NAME) \
          --network mqtt-net --network-alias $(SERVICE_NAME) \
          $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) /bin/bash
	docker network connect cam-net $(SERVICE_NAME) --alias $(SERVICE_NAME)
	docker start -ia $(SERVICE_NAME)

stop: check-dockerhubid
	-docker rm -f ${SERVICE_NAME} 2>/dev/null || :

clean: check-dockerhubid
	-docker rm -f ${SERVICE_NAME} 2>/dev/null || :
	-docker rmi $(DOCKERHUB_ID)/$(SERVICE_NAME)_$(ARCH):$(SERVICE_VERSION) 2>/dev/null || :

.PHONY: build run dev stop clean

