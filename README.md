![achatina](https://raw.githubusercontent.com/MegaMosquito/achatina/master/achatina.png)

Achatina is a set of examples that do visual inferencing using Docker containers on small computers, usually relatively slowly.

## Object Detection and Classification

The examples in this repository do visual inferencing. That is, these examples examine visual images and try to infer something interesting from the images. For example, they may try to detect whether there are any people or elephants in the image. In general, when they detect something, they try to classify it, and they annotate the incoming image to highlight what was detected. They also construct a standard JSON description of everything detected, and with the resulting base64-encoded image embedded as well. Here's an example output image:

![example-image](https://raw.githubusercontent.com/MegaMosquito/achatina/master/example.png)

Many of these examples are based on the [YOLO/DarkNet](https://pjreddie.com/darknet/yolo/) models trained from the [COCO](http://cocodataset.org/#home) data set. The COCO data set contains examples of 80 classes of visual objects from people to elephants. The YOLO/DarkNet software and models come in a variety of levels, but in general the examples here use the latest "tiny" versions.

The YOLO/DarkNet stuff is very easy to work with, and runs on very small computers, so it is a great fit for achatina.

### Docker is Required

All of the examples here *require a recent version of Docker* to be installed (I think version 18.06 or newer will work, maybe older ones too).

Using docker makes these examples extremely portable, requiring little or no setup on any host to use these examples. Usually all prerequistes are embedded within the resulting Docker containers. I try to do almost all of my coding within Docker containers these days, and acahtina is no exception.

## Usage

To quickly try this on your Linux machine:

- attach a camera (usually on `/dev/video0`, and compatible with `fswebcam`)
- make sure docker, git and make are installed
- clone this git repo, then cd into the top directory
- run `make test-yolocpu` (or some other target)
- when everything is up, point your browser to port `5200` on this machine

For more info, read the `README.md` files (here at the top, and in each of the example directories). Also read the Makefiles in each of these directories to see how the Docker containers are started, and the environment variables you can use to configure them differently (e.g., for a local camera on a different path than `/dev/video0`, or for your own webcam service).

## More Details

Many of the examples use the following 3 shared service containers:

### Shared Service -- restcam

All of these examples are also designed to make use of a camera, or a webcam. By default they try to use the local [restcam](https://github.com/MegaMosquito/achatina/tree/master/shared/restcam) shared service and it, in turn, uses the popular [fswebcam](https://github.com/fsphil/fswebcam) software to view the world through your camera. If image retrieval fails (e.g., if you don't have a camera attached) the raw original of the image above (before inferencing, and without any bounding boxes, laebls, etc.) will be provided by the `restcam` service. The `restcam` service provides images in the form of an image file, suitable for embedding in an HTML document. So you can easilt replace the `restcam` service with another image source anywhere on your LAN or even out on the Internet.

### Shared Service -- mqtt

Although it is not strictly necessary for the inferencing, all of the examples publish their inferencing results to the `/detect` topic on the local shared [mqtt](https://github.com/MegaMosquito/achatina/tree/master/shared/mqtt) broker. This MQTT broker is primarily an aid for debugging and for developer convenience. You can subscribe to this topic locally and see the JSON metadata that is generated each time inferencing is performed.

### Shared Service -- monitor

The shared [monitor](https://github.com/MegaMosquito/achatina/tree/master/shared/monitor) service is also not required, but it enables a quick local check of these examples. When you are running these examples you can navigate to the host's port `5200` using your browser to see live output. There you should see output similar to this:

![example-page](https://raw.githubusercontent.com/MegaMosquito/achatina/master/page.png)

## The Examples

This repository contains the following examples:

### CPU-Only Example

The [yolocpu](https://github.com/MegaMosquito/achatina/tree/master/yolocpu) example works on arm32, arm64, and amd64 hardware using only the CPU(s) of the machine. CPUs are not very fast for visual inferencing, but if that's all you've got you can still do cool stuff with them. And hey, if it takes 60 seconds to detect something in an image, maybe that is more than fine for your particular application. If so, you can save some of your cash, because the accelerated examples usually have significant additional costs. Achatina may be slow, but she's happy with just a CPU to work with. She doesn't need any fancy inferencing accelerators to get the job done.

### Accelerated Examples

Of course, using a GPU (or specialized visual inferencing hardware) to accelerate inferencing can usually significantly improve achatina's speed. Accelerated examples available currently include:

1. NVIDIA CUDA Example

Currently the CUDA example is the only GPU-accelerated example provided. The [yolocuda](https://github.com/MegaMosquito/achatina/tree/master/yolocuda) example relies on the NVIDIA CUDA software which requires an NVIDIA GPU. Currently the CUDA example only works with these NVIDIA Jetson boards: TX1, TX2, and Nano.

2. Intel Movidius Example

(coming soon)

## How Does It Work?

Each of these examples consists of multiple Docker containers providing services to each other privately and exposing some services on the host. Each of them also is designed to push its results to a remote [Apache Kafka](https://kafka.apache.org/) end point (broker). If you provide Kafka credentials, for a broker you have configured, then you can subscribe to that Kafka broker from other machines and monitor the output remotely.

### Service Architecture

The examples here are structured with 5 services:

1. `restcam` -- a webcam service (can use any other web cam service and not include this `restcam` service at all of you wish)
2. `mqtt` -- a locally accessible MQTT broker (intended for develpment and debugging, can be removed for production)
3. `monitor` -- a tiny web server, implemented with Python Flask for monitoring the example's output (intended for develpment and debugging, can be removed for production)
4. a *detector* service -- an object detection and classification REST service (different for each example, using CPU, or CUDA, or other tools as appropriate for the specific example), and
5. an application -- a top level container that invokes the above detector service, passing it the URL of the web cam to use (the `restcam` service by default), and receiving back the inferencing results. It then publishes the results to the local `mqtt` broker for debugging (and for the local `monitor` to notice and present on a web page). This MQTT publishing is optional. It also publishes the same data to a remote Kafka broker if the appropriate credentials are configured.

The diagram below shows the common architecture used for these examples:

![architecture-diagram](https://raw.githubusercontent.com/MegaMosquito/achatina/master/arch.png)

Arrows in the diagram represent the flow of data. Squares represent software components. Start at the `app`, invoke a REST GET on the `detector` service, passing the image source URL. The `detector` then invokes a REST GET on that image source URL (either the default `restcam` service or some other source), runs its inferencing magic upon it, then it responds to the REST GET from the `app` with the results, encoded in JSON (the image, and metadata about what was detected). Normally the `app` then publishes to `mqtt` (optional) and the remote Kafka broker (if credentials were provided). The `monitor` is watching `mqtt` and provides a local web server on port `5200` where you can see the results.

## JSON

The detector is expected to deliver a JSON payload back to the app. That JSON is then very slightly enhanced by the app to provide some information primarily for the monitor. The resulting JSON that is published to MQTT and kafka has this form:

```
{
  "source": "YOLO Tiny (COCO) -- for NVIDIA CUDA",
  "source-url": "https://github.com/MegaMosquito/achatina/yolocuda",
  "kafka-sub": " ... <only on MQTT, a complete kafkacat subscribe command> ... ",
  "detect": {
    "tool": "yolo-tiny-cuda",
    "deviceid": "nano-02",
    "image": " ... <large base64-encoded image is here> ...",
    "time": 0.132,
    "date": 1584407149,
    "camtime": 1.682,
    "entities": [
      {
        "eclass": "person",
        "details": [
          { "confidence": 0.996, "cx": 277, "cy": 296, "w": 139, "h": 394 },
          { "confidence": 0.952, "cx": 120, "cy": 270, "w": 191, "h": 403 },
          { "confidence": 0.853, "cx": 405, "cy": 276, "w": 166, "h": 394 },
          { "confidence": 0.667, "cx": 550, "cy": 283, "w": 160, "h": 366 }
        ]
      },
      {
        "eclass": "elephant",
        "details": [
          ...
        ]
      }
    ]
  }
}
```

Fields like `source`, `source-url`, and `tool` provide information about this particular detector. The device sending the data is identified with `device-id`.

Date shows the UTC date and time that the image was acquired. The `camtime` field states the time in seconds required to acquire the image from the webcam. The `time` field states the time in seconds that the inferencing step took.

There may be zero or more entities of zero or more classes detected (YOLO/COCO only knows 80 classes). The `entities` are grouped into classes. The details array for each detected class contains entries showing the detection confidence (between 0.0 and 1.0) plus the center location (cx, cy) and bounding box size (w x h) for each entity.

If kafka credentials were provided, then the `kafkacat` command to subscribe is provided when publishing to MQTT. This is redundant in the kafka data so it is omitted when sending the JSON to kafka.

## For more info

Each of the examples has its own README.md with additional details.

## Author

Written by Glen Darling, March 2020.
Inspired by earlier work from my former teammate, [David Martin](https://github.com/dcmartin).

