FROM nvcr.io/nvidia/deepstream:5.0-dp-20.04-triton

# Install dependencies
RUN apt-get update --fix-missing && apt-get install -y \
   ca-certificates \
   build-essential \
   autoconf libtool \
   python3 \
   python3-dev \
   python3-pip \
   python3-setuptools \
   python-gi-dev \
   libgstreamer1.0-dev \
   python3-opencv \
   libgstrtspserver-1.0-0 \
   gstreamer1.0-rtsp \
   libgirepository1.0-dev \
   gobject-introspection \
   gir1.2-gst-rtsp-server-1.0 \
   && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the Python deepstrem bindings. These were downloaded from here:
#   https://developer.nvidia.com/deepstream_python_v0.5
COPY deepstream_python_v0.9.tbz2 /
WORKDIR /
RUN tar -xvf /deepstream_python_v0.9.tbz2
RUN tar -xvf /deepstream_python_v0.9/ds_pybind_v0.9.tbz2 -C /opt/nvidia/deepstream/deepstream-5.0/sources

# Copy the python source and config file
COPY rtsp2way.py rtsp2way.cfg / 

# Users need to put their RTSP input URI into RTSPINPUT at build time. E.g.:
#   docker build --build-arg RTSPINPUT=... imagename .
ARG RTSPINPUT
RUN echo "Using RTSP input URI:" $RTSPINPUT
RUN echo "Output stream URI is: rtsp://localhost:8554/ds-test"

# Uncomment these for development, and comment the other ENTRYPOINT
# RUN echo "python3 rtsp2way.py -i \"$RTSPINPUT\""
# ENTRYPOINT /bin/bash
ENTRYPOINT python3 rtsp2way.py -i "$RTSPINPUT"

