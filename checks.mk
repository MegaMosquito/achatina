# Makefile targets to validate that required environment variables are set
# This file is included in other Makefiles in this project.

check-dockerhubid:
	@if [ -z "${DOCKERHUB_ID}" ]; \
          then { echo "***** ERROR: \"DOCKERHUB_ID\" is not set!"; exit 1; }; \
          else echo "  NOTE: Using DockerHubID: \"${DOCKERHUB_ID}\""; \
        fi
	@sleep 1

check-input-url:
	@if [ -z "${INPUT_URL}" ]; \
          then echo "  Warning: \"INPUT_URL\" is not set! Using default!"; \
        fi
	@sleep 1

check-kafka-creds:
	@if [ -z "${EVENTSTREAMS_BROKER_URLS}" ] || \
          [ -z "${EVENTSTREAMS_API_KEY}" ] || \
          [ -z "${EVENTSTREAMS_PUB_TOPIC}" ]; \
          then echo "  Warning: No EventStreams credentials found! Kafka publication is disabled."; \
          else echo "  NOTE: Publishing to topic: ${EVENTSTREAMS_PUB_TOPIC}"; \
        fi

.PHONY: check-dockerhubid check-input-url check-kafka-creds

