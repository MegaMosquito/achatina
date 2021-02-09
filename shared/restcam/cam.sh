#!/bin/bash

# Defaults
if [ -z "${CAM_DEVICE:-}" ]; then CAM_DEVICE="V4L2:/dev/video0"; fi
if [ -z "${CAM_DELAY_SEC:-}" ]; then CAM_DELAY_SEC=0; fi
if [ -z "${CAM_OUT_WIDTH:-}" ]; then CAM_OUT_WIDTH=640; fi
if [ -z "${CAM_OUT_HEIGHT:-}" ]; then CAM_OUT_HEIGHT=480; fi

# Files (@@@ these should all be just in RAM)
JPG="/tmp/cam.jpg"
RTN_JSON="/tmp/rtn.json"
SCALE="${CAM_OUT_WIDTH}x${CAM_OUT_HEIGHT}"

# Use this static image if anything goes wrong
MOCK="/mock.jpg"

# Remove any existing image
rm -f "${JPG}"

# Capture an image from CAM_DEVICE
fswebcam --device "${CAM_DEVICE}" --delay "${CAM_DELAY_SEC}" --scale "${SCALE}" --no-banner "${JPG}" 2>/dev/null

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

