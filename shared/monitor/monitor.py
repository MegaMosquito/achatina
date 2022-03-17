#
# Debug client for monitoring/debugging the achatina examples
#
# Written by Glen Darling, October 2019.
#

import json
import os
import subprocess
import threading
import time
from datetime import datetime
import base64

from io import BytesIO
from flask import Flask
from flask import send_file
from flask import render_template

# Configuration constants
MQTT_SUB_COMMAND = 'mosquitto_sub -h mqtt -p 1883 -C 1 '
MQTT_DETECT_TOPIC = '/detect'
FLASK_BIND_ADDRESS = '0.0.0.0'
FLASK_PORT = 5200
DUMMY_DETECT_IMAGE='/dummy_detect.jpg'

# Globals for the cached JSON data (last messages on these MQTT topics)
last_detect = None

webapp = Flask('monitor')
webapp.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@webapp.route("/images/detect.jpg")
def get_detect_image():
  if last_detect:
    j = json.loads(last_detect)
    i = base64.b64decode(j['detect']['image'])
    buffer = BytesIO()
    buffer.write(i)
    buffer.seek(0)
    return send_file(buffer, mimetype='image/jpg')
  else:
    return send_file(DUMMY_DETECT_IMAGE)

@webapp.route("/json")
def get_json():
  if last_detect:
    return last_detect.decode("utf-8") + '\n'
  else:
    return '{}\n'

@webapp.route("/")
def get_results():
  if None == last_detect:
    now = datetime.now().strftime("%Y/%m/%d %-I:%M%p")
    return '{"error":"' + now + ' -- No data yet."}'
  j = json.loads(last_detect)
  n = j['device-id']
  c = len(j['detect']['entities'])
  ct = j['detect']['cam-time']
  it = j['detect']['inf-time']
  s = j['source']
  u = j['source-url']
  # print(s, u)
  kafka_msg = ' Nothing is being published to Kafka!\n'
  if 'kafka-sub' in j:
    sub = j['kafka-sub']
    kafka_msg = ' This data is also being published to EventStreams (kafka). Subscribe with: <p style="font-family:monospace;">' + sub + '</p>\n'
  context = {k:v for (k,v) in locals().copy().items() if k in ('s', 'n', 'c', 'ct', 'it', 'u', 'kafka_msg')}
  return render_template("monitor.html", **context)

# Prevent caching everywhere
@webapp.after_request
def add_header(r):
  r.headers["Pragma"] = "no-cache"
  r.headers["Expires"] = "0"
  r.cache_control.max_age = 0
  r.cache_control.public = True
  return r

# Loop forever collecting object detection / classification data from MQTT
def collect_data():
  global last_detect
  # print("\nMQTT \"" + MQTT_DETECT_TOPIC + "\" topic monitor thread started!")
  detect_command = MQTT_SUB_COMMAND + '-t ' + MQTT_DETECT_TOPIC
  while True:
    last_detect = subprocess.check_output(detect_command, shell=True)
    # print("\n\nMessage received on detect topic...\n")
    # print(last_detect)

if __name__ == '__main__':
  # Main program (starts monitor thread and then web server)
  monitor_detect =  threading.Thread(target=collect_data)
  monitor_detect.start()

  webapp.run(host=FLASK_BIND_ADDRESS, port=FLASK_PORT)
