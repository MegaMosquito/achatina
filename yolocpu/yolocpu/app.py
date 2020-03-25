#
# The pump that calls the CPU yolo REST API, then pushes the results to kafka.
# It can also (optionally) push the data to the local MQTT for debug purposes.
#
# Written by Glen Darling, March 2020.
#

EXAMPLE_TITLE = 'YOLO (COCO) -- for CPU'
EXAMPLE_URL = 'https://github.com/MegaMosquito/achatina/yolocpu'

import json
import os
import subprocess
import threading
import time
from datetime import datetime
import base64
import requests
import urllib.parse

# Configuration from the environment
def get_from_env(v, d):
  if v in os.environ and '' != os.environ[v]:
    return os.environ[v]
  else:
    return d
EVENTSTREAMS_BROKER_URLS = get_from_env('EVENTSTREAMS_BROKER_URLS', '')
EVENTSTREAMS_API_KEY = get_from_env('EVENTSTREAMS_API_KEY', '')
EVENTSTREAMS_PUB_TOPIC = get_from_env('EVENTSTREAMS_PUB_TOPIC', '')
CAM_URL = get_from_env('CAM_URL', '')
MQTT_PUB_TOPIC = get_from_env('MQTT_PUB_TOPIC', '/detect')
DEFAULT_HZN_DEVICE_ID = '** NO DEVICE ID ** PUBLISHING TO KAFKA IS DISABLED **'
HZN_DEVICE_ID = get_from_env('HZN_DEVICE_ID', DEFAULT_HZN_DEVICE_ID)


# Try to compute some kind of value for the CAM URL if one was not provided
if '' == CAM_URL:
  host_ip = get_from_env('HOST_IP', '')
  if '' != host_ip:
    # Use the IP Address provided by the Makefile for dev purposes
    CAM_URL = 'http://' + host_ip + ":8888/"
  else:
    # If run by the Open-Horizon Agent, we should have this list of host IPs
    hzn_host_ips = get_from_env('HZN_HOST_IPS', '')
    if '' != hzn_host_ips:
      # HACK! Blindly try the first IP address found (really hacky!)
      CAM_URL = 'http://' + hzn_host_ips[0] + ":8888/"
    else:
      # If all else fails, just give them Albert
      CAM_URL = 'https://upload.wikimedia.org/wikipedia/commons/6/6f/Einstein-formal_portrait-35.jpg'
#print('CAM_URL = "' + CAM_URL + '"')

# Additional configuration constants
TEMP_FILE = '/tmp/yolo.json'
YOLO_URL = 'http://restyolocpu:80/detect?kind=jpg&url=' + urllib.parse.quote(CAM_URL)
MQTT_PUB_COMMAND = 'mosquitto_pub -h mqtt -p 1883'
DEBUG_PUB_COMMAND = MQTT_PUB_COMMAND + ' -t ' + MQTT_PUB_TOPIC + ' -f '
if '' != EVENTSTREAMS_BROKER_URLS and '' != EVENTSTREAMS_API_KEY and '' != EVENTSTREAMS_PUB_TOPIC:
  KAFKA_PUB_COMMAND = 'kafkacat -P -b ' + EVENTSTREAMS_BROKER_URLS + ' -X api.version.request=true -X security.protocol=sasl_ssl -X sasl.mechanisms=PLAIN -X sasl.username=token -X sasl.password="' + EVENTSTREAMS_API_KEY + '" -t ' + EVENTSTREAMS_PUB_TOPIC + ' '
else:
  KAFKA_PUB_COMMAND = ''
SLEEP_BETWEEN_CALLS = 0.1

# To log or not to log, that is the question
LOG_STATS = False
LOG_ALL = False

if __name__ == '__main__':
  while True:
    try:
      # Request one run from the yolo REST service...
      if LOG_ALL:
        print('\nInitiating a request...')
        print('--> URL: ' + YOLO_URL)
      r = requests.get(YOLO_URL)
      if (r.status_code > 299):
          print('ERROR: Yolo request failed: ' + str(r.status_code))
          time.sleep(10)
          continue
      if LOG_ALL: print('Successful response received!')
      j = r.json()
      if LOG_ALL or LOG_STATS:
        d = datetime.fromtimestamp(j['detect']['date']).strftime('%Y-%m-%d %H:%M:%S')
        print('Date: %s, Cam: %0.2f sec, Yolo: %0.2f msec.' % (d, j['detect']['camtime'], j['detect']['time'] * 1000.0))

      # Add info into the JSON about this example
      j['source'] = EXAMPLE_TITLE
      j['source-url'] = EXAMPLE_URL
      j['deviceid'] = HZN_DEVICE_ID

      # Push JSON to a file (so we can publish it, since it overflows the CLI)
      with open(TEMP_FILE, 'w') as temp_file:
        json.dump(j, temp_file)

      # Publish to kafka if a device ID and appropriate creds were provided
      if HZN_DEVICE_ID != DEFAULT_HZN_DEVICE_ID and '' != KAFKA_PUB_COMMAND:
        if LOG_ALL: print('--> Kafka: ' + KAFKA_PUB_COMMAND + TEMP_FILE)
        discard = subprocess.run(KAFKA_PUB_COMMAND + TEMP_FILE, shell=True)
      else:
        if LOG_ALL: print('--> Kafka: *** PUBLICATION DISABLED **')

      # (Optionally) publish to the debug topic (with subscribe info if approp)
      if '' != MQTT_PUB_TOPIC:
        # Did we publish this stuff to kafka?
        if '' != KAFKA_PUB_COMMAND:
          # Provide info to the caller about how to subscribe to this kafka stream
          j['kafka-sub'] = 'kafkacat -C -b ' + EVENTSTREAMS_BROKER_URLS + ' -X api.version.request=true -X security.protocol=sasl_ssl -X sasl.mechanisms=PLAIN -X sasl.username=token -X sasl.password="' + EVENTSTREAMS_API_KEY + '" -t ' + EVENTSTREAMS_PUB_TOPIC
          # Rewrite the file with the updated JSON
          with open(TEMP_FILE, 'w') as temp_file:
            json.dump(j, temp_file)
        if LOG_ALL: print('--> MQTT: ' + DEBUG_PUB_COMMAND + TEMP_FILE)
        discard = subprocess.run(DEBUG_PUB_COMMAND + TEMP_FILE, shell=True)

    except:
      if LOG_ALL: print('*** Exception in main loop! ***')
      pass

    # Pause briefly (to not hog the CPU too much)
    if LOG_ALL: print('Sleeping for ' + str(SLEEP_BETWEEN_CALLS) + ' seconds...')
    time.sleep(SLEEP_BETWEEN_CALLS)
