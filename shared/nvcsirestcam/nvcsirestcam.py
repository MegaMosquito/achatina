#
# REST API for access to selected GPIO pins
#
# Written by Glen Darling, February 2019.
#

import fcntl
from flask import Flask
from flask import send_file
import glob
import json
import os
import queue
import select
import subprocess
import sys
import threading
import threading
import time

# REST API details
REST_API_BIND_ADDRESS = '0.0.0.0'
REST_API_PORT = 80
webapp = Flask('csicam')
webapp.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Configuration from the environment
def get_from_env(v, d):
  if v in os.environ and '' != os.environ[v]:
    return os.environ[v]
  else:
    return d
CAM_SOURCE = get_from_env('CAM_SOURCE', '1')
CAM_ORIENTATION = get_from_env('CAM_ORIENTATION', '0')
CAM_RES = get_from_env('CAM_RES', '4')

# Some possibly useful nvgstcapture arguments:
#  --camsrc        Cam source (0=v4l2, 1=csi[default], 2=videotest, 3=eglstream)
#  --mode          Capture mode value (1=still[default], 2=video)
#  --image-enc     Image encoder type (0=jpeg_SW[jpegenc] 1=jpeg_HW[nvjpegenc])
#  --file-name     Captured file name. nvcamtest is used by default
#  --orientation   Camera sensor orientation value
#                     Supported orientations
#                       (0): none
#                       (1): Rotate counter-clockwise 90 degrees
#                       (2): Rotate 180 degrees
#                       (3): Rotate clockwise 90 degrees
#  --whitebalance  Capture whitebalance value
#  --image-res     Image width & height number (2..12). e.g., --image-res=3
#                     Supported resolutions for NvArgusCamera
#                       (2) : 640x480
#                       (3) : 1280x720
#                       (4) : 1920x1080
#                       (5) : 2104x1560
#                       (6) : 2592x1944
#                       (7) : 2616x1472
#                       (8) : 3840x2160
#                       (9) : 3896x2192
#                       (10): 4208x3120
#                       (11): 5632x3168
#                       (12): 5632x4224
#  
PROCESS_START = [
    '/usr/bin/nvgstcapture-1.0',
    '--camsrc=' + CAM_SOURCE,
    '--orientation=' + CAM_ORIENTATION,
    '--image-res=' + CAM_RES
  ]
IMAGE_PREFIX = "nvcamtest"
# Global handle for the subprocess
nvgstcapture = None

# Get all image file names in the currrent directory
def find_image_files():
  image_files = glob.glob('./' + IMAGE_PREFIX + '*')
  #print(image_files)
  return image_files

# Cleanup any dangling old images
def cleanup():
  image_files = find_image_files()
  for f in image_files:
    os.remove(f)

# Read from the queue until a particular string is seen
def await_output(target):
  pointer = -1
  while pointer < (len(target) - 1):
    try:
      ch = q.get_nowait()
    except queue.Empty:
      time.sleep(0.05)
    else:
      if ch == target[pointer + 1]:
        pointer += 1
      else:
        pointer = -1
      print(ch, end='')
      sys.stdout.flush()

# REST GET: /image: capture an image
@webapp.route("/", methods=['GET'])
def csicam_get_image():
  global nvgstcapture
  if None == nvgstcapture:
    return ('{"error": nvgstcapture did not initialize!"}\n')
  else:
    cleanup()
    print("Capturing...")
    # Send "j\n" to nvgstcapture to tell it to capture one image
    nvgstcapture.stdin.write("j\n".encode('utf-8'))
    nvgstcapture.stdin.flush()
    while 0 == len(find_image_files()):
      pass
    await_output("Image Captured")
    image_files = find_image_files()
    print("\nFound " + str(len(image_files)) + "image(s).")
    return send_file(image_files[0])

# Main program (to start the nvgstcapture process and the web server thread)
def main():

  global q
  def output_handler(out, q):
    while True:
      ch = out.read(1).decode('utf-8')
      q.put(ch)

  # Start nvgstcapture. It will continue to run through the life of this process
  global nvgstcapture
  nvgstcapture = subprocess.Popen(
    PROCESS_START,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    bufsize=1)
  q = queue.Queue()
  t = threading.Thread(target=output_handler, args=(nvgstcapture.stdout, q))
  t.daemon = True
  t.start()

  # Wait until nvgstcapture has come up
  await_output("iterating capture loop")
  time.sleep(1)
  # Flush the queue (optional)
  while True:
    try:
      x = q.get_nowait()
    except queue.Empty:
      break
    else:
      pass
  print("\nCamera is ready!")
  sys.stdout.flush()

  # Start the web server
  webapp.run(host=REST_API_BIND_ADDRESS, port=REST_API_PORT)

  # NOT REACHED

if __name__ == '__main__':
  main()

