#
# A top level Makefile for the achatina examples
#
# You must set the DOCKERHUB_ID environment variable before using this Makefile
#
# The main targets provided:
#   run             (build & test the CPU-only example -- should run anywhere)
#   run-cuda        (build & test the CUDA example -- NVIDIA setup req'd)
#   run-openvino    (build & test the OpenVino example -- Movidius setup req'd)
#   build           (build the containers needed for the CPU example)
#   build-cuda      (build the containers needed for the CUDA example)
#   build-openvino  (build the containers needed for the OpenVino example)
#   build-all       (build all of the example containers -- NVIDIA setup req'd)
#   stop            (stop and remove all example containers)
#   clean           (stop and remove all example containers, and their images)
#   deep-clean      (cleanup docker, incl. all contaiiners, images, networks)
#
# Optionally configure an INPUT_URL in your environment. You have 3 choices:
#   1. Don't set it and the "restcam" service or a static image will be used
#   2. Provide a valid HTTP image URL. E.g.:
#          https://commons.wikimedia.org/wiki/File:Example.jpg
#   3. Provide a valid RTSP stream URL. E.g.:
#           rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov
#
# If you wish to use the "restcam" (see shared/restcam) there are additional
# enviropnment variables you may wish to set to configure that servcie.
#
# Optionally, you may configure a Kafka endpoint to receive the JSON output.
# Just don't set these if you do not wish to pubish to a remote Kafka broker.
# Enviroonment variables that must be set if you wish to publish to Kafka:
#   KAFKA_BROKER_URLS, KAFKA_API_KEY, KAFKA_PUB_TOPIC
#

# These statements will automatically configure some environment variables
ARCH:=$(shell ./helper -a)
NODE:=$(shell ./helper -n)

run: run-cpu-only
build: build-cpu-only

run-shared-services: build-shared-services
	$(MAKE) -C shared/mqtt run
	$(MAKE) -C shared/restcam run
	$(MAKE) -C shared/monitor run

run-cpu-only: build-cpu-only run-shared-services
	@echo "Running the CPU-only version of the achatina application..."
	$(MAKE) -C plugins/cpu-only run
	env ACHATINA_PLUGIN=cpu-only $(MAKE) -C achatina run

run-cuda: build-cuda run-shared-services
	@echo "Running the NVIDIA-accelerated version of the achatina application..."
	$(MAKE) -C plugins/cuda run
	env ACHATINA_PLUGIN=cuda $(MAKE) -C achatina run

run-openvino: build-openvino run-shared-services
	@echo "Running the Movidius-accelerated version of the achatina application..."
	$(MAKE) -C plugins/openvino run
	env ACHATINA_PLUGIN=openvino $(MAKE) -C achatina run

build-shared-services:
	@echo "Building the shared services..."
	$(MAKE) -C shared/mqtt build
	$(MAKE) -C shared/restcam build
	$(MAKE) -C shared/monitor build

build-cpu-only: build-shared-services
	$(MAKE) -C plugins/cpu-only build
	$(MAKE) -C achatina build

build-cuda: build-shared-services
	$(MAKE) -C plugins/cuda build
	$(MAKE) -C achatina build

build-openvino: build-shared-services
	$(MAKE) -C plugins/openvino build
	$(MAKE) -C achatina build

build-all: build-shared-services
	$(MAKE) -C plugins/cpu-only build
	$(MAKE) -C plugins/cuda build
	$(MAKE) -C plugins/openvino build
	$(MAKE) -C achatina build

stop:
	@echo "Stopping all example containers."
	$(MAKE) -C shared/mqtt stop
	$(MAKE) -C shared/restcam stop
	$(MAKE) -C shared/monitor stop
	$(MAKE) -C plugins/cpu-only stop
	$(MAKE) -C plugins/cuda stop
	$(MAKE) -C plugins/openvino stop
	$(MAKE) -C achatina stop

clean:
	@echo "Stopping all example containers and removing their images."
	$(MAKE) -C shared/mqtt clean
	$(MAKE) -C shared/restcam clean
	$(MAKE) -C shared/monitor clean
	$(MAKE) -C plugins/cpu-only clean
	$(MAKE) -C plugins/cuda clean
	$(MAKE) -C plugins/openvino clean
	$(MAKE) -C achatina clean

deep-clean:
	@echo "Removing all Docker running containers, all container images, and more."
	-docker rm -f `docker ps -aq` 2>/dev/null || :
	-docker rmi -f `docker images -aq` 2>/dev/null || :
	-docker network prune || :
	-docker volume prune || :

.PHONY: run build run-shared-services run-cpu-only run-cuda run-openvino build-shared-services build-cpu-only build-cuda build-openvino build-all stop clean deep-clean
