#!/bin/bash

# Defaults
if [ -z "${RTSP_LINK:-}" ]; then RTSP_LINK="http://158.58.130.148/mjpg/video.mjpg"; fi
if [ -z "${CAM_OUT_WIDTH:-}" ]; then CAM_OUT_WIDTH=640; fi
if [ -z "${CAM_OUT_HEIGHT:-}" ]; then CAM_OUT_HEIGHT=480; fi

# Files
JPG="/app/cam.jpg"
SCALE="${CAM_OUT_WIDTH}x${CAM_OUT_HEIGHT}"

# Use this static image if anything goes wrong
MOCK="/mock.jpg"

# Remove any existing image
rm -f "${JPG}"

# Capture an image from RTSP_LINK
ffmpeg -y -i "${RTSP_LINK}" -vframes 1 -s ${SCALE} "${JPG}" 2>/dev/null

# Did we get an image
if [ ! -s "${JPG}" ]; then
  # No. Use the static image instead
  cp "${MOCK}" "${JPG}"
fi

# Send the HTTP metadata
SIZE=`stat -c '%s' "${JPG}"`
echo -ne "HTTP/1.1 200 OK\nContent-type: image/jpg\nContent-length: $SIZE\n\n"

# Send the file itself
cat "${JPG}"

