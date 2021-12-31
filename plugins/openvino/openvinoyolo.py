#!/usr/bin/python3
#
# Written by Glen Darling, October 2020.
# (based on work by PINTO at #https://github.com/PINTO0309/OpenVINO-YoloV3)
#

import base64
from datetime import datetime
from flask import Flask, request
import os
from io import BytesIO
import json
from math import exp as exp
import numpy as np, math
import requests
import shutil
import subprocess
import sys
import threading
import time

import cv2
from openvino.inference_engine import IECore, IENetwork, IEPlugin

# Configuration constants
FLASK_BIND_ADDRESS = '0.0.0.0'
FLASK_PORT = 80
LOGO_IMAGE = '/logo.png'
LOGO_SIZE = (27,13)
INCOMING_IMAGE = '/tmp/incoming.jpg'
OUTGOING_IMAGE = '/tmp/outgoing.jpg'
COLOR_OUTLINE = (255, 255, 255)
COLOR_LABEL = (0, 0, 0)
MINIMUM_CONFIDENCE = 0.2
label_text_color = (255, 255, 255)
label_background_color = (125, 175, 75)
box_color = (255, 128, 0)
box_thickness = 1

# Configuration from the environment
def get_from_env(v, d):
  if v in os.environ and '' != os.environ[v]:
    return os.environ[v]
  else:
    return d
OPENVINO_PLUGIN = get_from_env('OPENVINO_PLUGIN', 'CPU')
print('OPENVINO_PLUGIN = %s' % (OPENVINO_PLUGIN))

# Pull in the achatina logo image (for later drawing in the bounding boxes)
# Feel free to put your own logo here! :-)
global logo
biglogo= cv2.imread(LOGO_IMAGE)
logo = cv2.resize(biglogo, LOGO_SIZE, interpolation=cv2.INTER_LANCZOS4)

# YoloV3 model constants
classes = 80
coords = 4
num = 3
yolo_shape = (416, 416)
anchors = [ 10,13,16, 30,33,23, 30,61,62, 45,59,119, 116,90,156, 198,373,326 ]

# Configure REST server args
webapp = Flask('yolo')
webapp.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Force the timezone in the container to be UTC
os.environ['TZ']='UTC'

# Outline an entity, and label it with its name and confidence
def outline (original, entity, confidence, xmin, ymin, xmax, ymax):
  # print('e=%s, conf=%f, xmin=%d, ymin=%d, xmax=%d, ymax=%d, c=%s' % (entity, confidence, xmin, ymin, xmax, ymax, str(COLOR_OUTLINE)))
  # Draw the bounding box first
  cv2.rectangle(original, (xmin, ymin), (xmax, ymax), COLOR_OUTLINE, 2)
  # Then the text box (filled)
  cv2.rectangle(original, (xmin - 1, ymin - 1), (xmax + 1, ymin - 14), COLOR_OUTLINE, -1)
  # And then the logo (directly overwrite the image bytes -- hack)
  lx = xmin + 3
  ly = ymin - 12
  original[ly : ly + logo.shape[0], lx : lx + logo.shape[1]] = logo
  # And finally the label
  label = (" %s (%0.2f%%)" % (labels[entity], 100.0 * confidence))
  cv2.putText(original, label, (xmin + logo.shape[1] + 3, ymin - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.3, COLOR_LABEL, 1, cv2.LINE_AA)

# Simple class for detected objects
class Detected():
  def __init__(self, cx, cy, h, w, entity, confidence, h_scale, w_scale):
    self.cx = cx
    self.cy = cy
    self.w = w
    self.h = h
    self.scale = (w_scale, h_scale)
    self.xmin = int((cx - w / 2) * w_scale)
    self.ymin = int((cy - h / 2) * h_scale)
    self.xmax = int(self.xmin + w * w_scale)
    self.ymax = int(self.ymin + h * h_scale)
    self.entity = entity
    self.confidence = confidence

# Taken as a "black box" from the original PINTO code
def EntryIndex(side, lcoords, lclasses, location, entry):
  n = int(location / (side * side))
  loc = location % (side * side)
  return int(n * side * side * (lcoords + lclasses + 1) + entry * side * side + loc)

# Taken as a "black box" from the original PINTO code
def IntersectionOverUnion(box_1, box_2):
  width_of_overlap_area = min(box_1.xmax, box_2.xmax) - max(box_1.xmin, box_2.xmin)
  height_of_overlap_area = min(box_1.ymax, box_2.ymax) - max(box_1.ymin, box_2.ymin)
  area_of_overlap = 0.0
  if (width_of_overlap_area < 0.0 or height_of_overlap_area < 0.0):
    area_of_overlap = 0.0
  else:
    area_of_overlap = width_of_overlap_area * height_of_overlap_area
  box_1_area = (box_1.ymax - box_1.ymin)  * (box_1.xmax - box_1.xmin)
  box_2_area = (box_2.ymax - box_2.ymin)  * (box_2.xmax - box_2.xmin)
  area_of_union = box_1_area + box_2_area - area_of_overlap
  return (area_of_overlap / area_of_union)

# Mostly taken as a "black box" from the original PINTO code
def ParseYOLOV3Output(blob, resized_im_h, resized_im_w, original_im_h, original_im_w, threshold, objects):
  out_blob_h = blob.shape[2]
  out_blob_w = blob.shape[3]
  side = out_blob_h
  side_square = side * side
  output_blob = blob.flatten()
  anchor_offset = 0
  if 13 == side:
    anchor_offset = 2 * 6
  elif 26 == side:
    anchor_offset = 2 * 3
  elif 52 == side:
    anchor_offset = 2 * 0
  for i in range(side_square):
    row = int(i / side)
    col = int(i % side)
    for n in range(num):
      obj_index = EntryIndex(side, coords, classes, n * side * side + i, coords)
      box_index = EntryIndex(side, coords, classes, n * side * side + i, 0)
      scale = output_blob[obj_index]
      if (scale < threshold):
        continue
      x = (col + output_blob[box_index + 0 * side_square]) / side * resized_im_w
      y = (row + output_blob[box_index + 1 * side_square]) / side * resized_im_h
      height = math.exp(output_blob[box_index + 3 * side_square]) * anchors[anchor_offset + 2 * n + 1]
      width = math.exp(output_blob[box_index + 2 * side_square]) * anchors[anchor_offset + 2 * n]
      for j in range(classes):
        class_index = EntryIndex(side, coords, classes, n * side_square + i, coords + 1 + j)
        prob = scale * output_blob[class_index]
        if prob < threshold:
          continue
        obj = Detected(x, y, height, width, j, prob, (original_im_h / resized_im_h), (original_im_w / resized_im_w))
        objects.append(obj)
  return objects

# Based on "main_IE_infer" in the original PINTO code
def do_detect(incoming, outgoing):

    # Read image and prepare the corresponding numpy array for openvino
    original_image = cv2.imread(incoming)
    image_width = np.size(original_image,1)
    image_height = np.size(original_image,0)
    numpy_image = cv2.resize(original_image, yolo_shape)
    numpy_image = numpy_image[np.newaxis, :, :, :]
    numpy_image = numpy_image.transpose((0, 3, 1, 2))

    # Run inferencing engine on this image (globals exec_net and input_blob)
    outputs = exec_net.infer(inputs={input_blob: numpy_image})

    # Collect the detected objects
    objects = []
    for output in outputs.values():
        objects = ParseYOLOV3Output(output, yolo_shape[0], yolo_shape[1], image_height, image_width, 0.7, objects)

    # Filter overlapping boxes (set confidence to 0 to discard -- hack!)
    objlen = len(objects)
    for i in range(objlen):
        if (objects[i].confidence == 0.0):
            continue
        for j in range(i + 1, objlen):
            if (IntersectionOverUnion(objects[i], objects[j]) >= 0.4):
                objects[j].confidence = 0

    # Return the image and the list of filtered detected objects
    return (original_image, objects)

if __name__ == '__main__':

  cv2.destroyAllWindows()

  # Consume ClI arguments
  if (4 != len(sys.argv)):
    print("Usage:  %s model.xml weights.bin classes.labels" % sys.argv[0])
    sys.exit(1)
  config_file= sys.argv[1]
  weights_file = sys.argv[2]
  labels_file = sys.argv[3]
  print("Model config file (.xml):    %s" % config_file)
  print("Model weights file (.bin):   %s" % weights_file)
  print("Class labels file (.labels): %s" % labels_file)

  # Read model's Intermediate Representation (IR, i.e., the .xml and .bin files)
  ie_core = IECore()
  net = ie_core.read_network(model=config_file, weights=weights_file)
  #ie_core.set_config(config={"VPU_FORCE_RESET": "YES"}, device_name=OPENVINO_PLUGIN)

  # Create the global input_blob (blob map)
  global input_blob
  input_blob = next(iter(net.input_info))

  # Create the global labels list
  global labels
  with open(labels_file, 'r') as f:
    labels = [x.strip() for x in f]

  # Create the global exec_net (ExecutableNetwork) on a device
  global exec_net
  exec_net = ie_core.load_network(network=net, device_name=OPENVINO_PLUGIN)

  #
  # Expose the YoloV2 "detector.infer()" function
  #
  # URL parameters (i.e., "?key=value&..."):
  #  x kind:        default (if not specified) is 'jpg'
  #  * url:         (required) url to retrieve the source image
  #    user:        if url requires HTTP basic auth, this is the user
  #    password:    if url requires HTTP basic auth, this is the password
  #  x thresh:      detection confidence threshold in percent (i.e., 0..100)
  #  x hierthresh:  hierarchical detection confidence threshold in % (0..100) 
  #  x nms:         non-max suppression intersection-over-union threshold in %
  #
  # Note:
  #  * indicates a required parameter
  #  x indicates a currently ignored parameter
  #
  # Usage example:
  #   curl http://localhost:5252/detect?kind=json&url=http%3A%2F%2Frestcam
  #
  @webapp.route("/detect", methods=['GET'])
  def get_detect():

    print("\n\nREST request received.")
    print(request.args)
    kind = request.args.get('kind', '')
    url = request.args.get('url', '')
    if '' == url:
      return('{"error": "URL not provided."}\n', 400)
    print("URL is:   %s" % url)
    user = request.args.get('user', '')
    password = request.args.get('password', '')
    thresh = request.args.get('thresh', '')
    hierthresh = request.args.get('hierthresh', '')
    nms = request.args.get('nms', '')

    # Pull image from the provided camera URL
    print("Pulling an image from the camera REST service...")
    cam_start = time.time()
    if ('' != user):
      r = requests.get(url, auth=(user, password))
    else:
      r = requests.get(url)
    print("Camera service returned.")
    if (r.status_code > 299):
      return (json.dumps({"error": "unable to get image from camera"}) + '\n', 400)
    #if (r.headers['content-type'] != 'image/jpg'):
    #  return (json.dumps({"error": "camera did not return a jpg image"}) + '\n', 400)
    cam_end = time.time()

    # We have a jpg binary. Write it into the local file system.
    with open(INCOMING_IMAGE, 'wb') as f:
      for chunk in r.iter_content(1024):
        f.write(chunk)
    print("Image is ready in file system...")

    # Run the inferencing algorithm...
    prediction_start = time.time()
    original_image, detected = do_detect(INCOMING_IMAGE, OUTGOING_IMAGE)
    prediction_end = time.time()
    print('Inferencing is finished.')

    # Prepare the outgoing JSON with image (incl. drawing bounding boxes, etc.)
    print('Preparing prediction image and formatting return data...')

    # Process the prediction result, constructing JSON and drawing outline boxes
    data = {}
    entity_raw = {}
    for obj in detected:
      if obj.confidence < MINIMUM_CONFIDENCE:
        continue
      outline(original_image, obj.entity, obj.confidence, obj.xmin, obj.ymin, obj.xmax, obj.ymax)
      if not (obj.entity in entity_raw):
        this_entity = {}
        this_entity['eclass'] = labels[obj.entity]
        this_entity['details'] = []
        entity_raw[obj.entity] = this_entity
      this_entity = entity_raw[obj.entity]
      # Prepare info for the return JSON payload
      this_instance = {}
      this_instance['confidence'] = round(float(obj.confidence), 3)
      this_instance['cx'] = int(obj.cx)
      this_instance['cy'] = int(obj.cy)
      this_instance['w'] = int(obj.w)
      this_instance['h'] = int(obj.h)
      this_entity['details'].append(this_instance)
    cv2.imwrite(OUTGOING_IMAGE, original_image)
    entity_data = []
    for cls in entity_raw:
      entity_data.append(entity_raw[cls])
    detect_data = {}
    detect_data['tool'] = 'openvino'
    detect_data['date'] = int(time.time())
    detect_data['camtime'] = round(cam_end - cam_start, 3)
    detect_data['inf-time'] = round(prediction_end - prediction_start, 3)
    detect_data['entities'] = entity_data
    image_base64 = subprocess.check_output(['/usr/bin/base64 -w 0 -i ' + OUTGOING_IMAGE], shell=True, encoding='UTF-8')
    detect_data['image'] = image_base64
    data['detect'] = detect_data
    json_data = json.dumps(data)
    return (json_data + '\n', 200)

  # Start up the REST server
  webapp.run(host=FLASK_BIND_ADDRESS, port=FLASK_PORT)

  # Prevent caching everywhere
  @webapp.after_request
  def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

