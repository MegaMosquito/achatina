IMAGENAME:=ibmosquito/deepstream-python-amd64:1.0.0
RTSPINPUT:="rtsp://192.168.1.52:8554/Streaming/Channels/401"

run: stop
	@echo "\n\n"
	@echo "***   Using RTSP input URI: $(RTSPINPUT)"
	@echo "***   Output stream URI is: rtsp://localhost:8554/ds-test"
	@echo "\n\n"
	#docker run -d --shm-size=1g --ulimit memlock=-1 --ulimit stack=67108864 -p 8554:8554 $(IMAGENAME)
	docker run -it --name ds5python -p 8554:8554 $(IMAGENAME)

build:
	docker build --build-arg RTSPINPUT=$(RTSPINPUT) -t $(IMAGENAME) .

stop:
	@docker rm -f ds5python >/dev/null 2>&1 || :

.PHONY: build run stop
