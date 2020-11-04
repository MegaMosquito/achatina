# A simple Makefile for the achatina shared services

run: build
	@echo "Starting all of the shared services..."
	make -C mqtt run
	make -C restcam run
	make -C monitor run

build:
	@echo "Building all of the shared services..."
	make -C mqtt build
	make -C restcam build
	make -C monitor build

stop:
	@echo "Stopping all of the shared services..."
	make -C mqtt stop
	make -C restcam stop
	make -C monitor stop

clean:
	@echo "Cleaning all of the shared services..."
	make -C mqtt clean
	make -C restcam clean
	make -C monitor clean

.PHONY: build run stop clean

