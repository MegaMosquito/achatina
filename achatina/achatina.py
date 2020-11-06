#
# achatina
#
# This is the code that calls a plugin visual service's REST API, then
# pushes the results to mqtt and/or kafka, or perhaps does nothing with it.
#
# Written by Glen Darling, March 2020.
# Updated for v2, October 2020.
#

ACHATINA_URL = 'https://github.com/MegaMosquito/achatina'

import json
import os
import socket
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
ACHATINA_PLUGIN = get_from_env('ACHATINA_PLUGIN', 'cpu-only')
MQTT_BROKER_ADDRESS = get_from_env('MQTT_BROKER_ADDRESS', 'mqtt')
MQTT_BROKER_PORT = get_from_env('MQTT_BROKER_PORT', '1883')
MQTT_PUB_TOPIC = get_from_env('MQTT_PUB_TOPIC', '/detect')
KAFKA_BROKER_URLS = get_from_env('KAFKA_BROKER_URLS', '')
KAFKA_API_KEY = get_from_env('KAFKA_API_KEY', '')
KAFKA_PUB_TOPIC = get_from_env('KAFKA_PUB_TOPIC', '')
INPUT_URL = get_from_env('INPUT_URL', '')
NODE = get_from_env('NODE', '')
HOST_IP = get_from_env('HOST_IP', '')

# Exit if any required configuration is not present
if '' == INPUT_URL:
  print('******* ERROR: configuration variable "INPUT_URL" is not set! ******')
  os._exit(1)

# Log some useful information
print('achatina: ACHATINA_PLUGIN="%s"' % ACHATINA_PLUGIN)
print('achatina: MQTT_BROKER_ADDRESS="%s"' % MQTT_BROKER_ADDRESS)
print('achatina: MQTT_BROKER_PORT="%s"' % MQTT_BROKER_PORT)
print('achatina: MQTT_PUB_TOPIC="%s"' % MQTT_PUB_TOPIC)
print('achatina: KAFKA_BROKER_URLS="%s"' % KAFKA_BROKER_URLS)
if '' == KAFKA_API_KEY:
  print('achatina: KAFKA_API_KEY="%s"" (is not set)')
else:
  print('achatina: KAFKA_API_KEY="*******" (is set)')
print('achatina: KAFKA_PUB_TOPIC="%s"' % KAFKA_PUB_TOPIC)
print('achatina: INPUT_URL="%s"' % INPUT_URL)
print('achatina: NODE="%s"' % NODE)

# Configuration constants
# PLUGIN_URL is tricky because openvino unfortunately requires --net=host
if 'ACHATINA_PLUGIN' in os.environ and 'openvino' != os.environ['ACHATINA_PLUGIN']:
  PLUGIN_URL = ('http://%s:80/detect?url=%s' % (HOST_IP, urllib.parse.quote(INPUT_URL)))
else:
  PLUGIN_URL = ('http://%s:80/detect?url=%s' % (ACHATINA_PLUGIN, urllib.parse.quote(INPUT_URL)))
TEMP_FILE = '/tmp/achatina.json'
MQTT_PUB_COMMAND = ('mosquitto_pub -h %s -p %s -t %s -f ' % (MQTT_BROKER_ADDRESS, MQTT_BROKER_PORT, MQTT_PUB_TOPIC))
if '' != KAFKA_BROKER_URLS and '' != KAFKA_API_KEY and '' != KAFKA_PUB_TOPIC:
  KAFKA_PUB_COMMAND = 'kafkacat -P -b ' + KAFKA_BROKER_URLS + ' -X api.version.request=true -X security.protocol=sasl_ssl -X sasl.mechanisms=PLAIN -X sasl.username=token -X sasl.password="' + KAFKA_API_KEY + '" -t ' + KAFKA_PUB_TOPIC + ' '
else:
  KAFKA_PUB_COMMAND = ''
SLEEP_BETWEEN_CALLS = 0.1

# Log more useful information
print('achatina: TEMP_FILE="%s"' % TEMP_FILE)
print('achatina: PLUGIN_URL="%s"' % PLUGIN_URL)
print('achatina: MQTT_PUB_COMMAND="%s"' % MQTT_PUB_COMMAND)
print('achatina: KAFKA_PUB_COMMAND="%s"' % KAFKA_PUB_COMMAND)
print('achatina: SLEEP_BETWEEN_CALLS="%f"' % SLEEP_BETWEEN_CALLS)

# To log or not to log, that is the question
LOG_DETAIL = False
LOG_STATS = True
LOG_EXCEPT = True
LOG_SLEEP = False

if __name__ == '__main__':
  while True:
    #try:
      # Request one run from the plugin REST service...
      if LOG_DETAIL:
        print('\nInitiating a request...')
        print('--> URL: ' + PLUGIN_URL)
      r = requests.get(PLUGIN_URL)
      if (r.status_code > 299):
          print('ERROR: Plugin request failed: ' + str(r.status_code))
          time.sleep(10)
          continue
      if LOG_DETAIL: print('Successful response received!')
      j = r.json()
      if LOG_DETAIL or LOG_STATS:
        d = datetime.fromtimestamp(j['detect']['date']).strftime('%Y-%m-%d %H:%M:%S')
        print('Date: %s, Cam: %0.2f sec, Yolo: %0.2f msec.' % (d, j['detect']['camtime'], j['detect']['time'] * 1000.0))

      # Add info into the JSON about this example
      j['source'] = 'achatina (with plugin "' + ACHATINA_PLUGIN + '")'
      j['source-url'] = ACHATINA_URL
      if '' != NODE:
        j['deviceid'] = NODE
      else:
        j['deviceid'] = '** NO DEVICE ID ** KAFKA PUBLISHING DISABLED **'

      # Push JSON to a file (so we can publish it, since it overflows the CLI)
      with open(TEMP_FILE, 'w') as temp_file:
        json.dump(j, temp_file)

      # Publish to kafka if a device ID and appropriate creds were provided
      if '' != NODE and '' != KAFKA_PUB_COMMAND:
        if LOG_DETAIL: print('--> Kafka: ' + KAFKA_PUB_COMMAND + TEMP_FILE)
        discard = subprocess.run(KAFKA_PUB_COMMAND + TEMP_FILE, shell=True)
      else:
        if LOG_DETAIL: print('--> Kafka: *** PUBLICATION DISABLED **')

      # (Optionally) publish to the debug topic (with subscribe info if approp)
      if '' != MQTT_PUB_TOPIC:
        # Did we publish this stuff to kafka?
        if '' != KAFKA_PUB_COMMAND:
          # Provide info to the caller about how to subscribe to this kafka stream
          j['kafka-sub'] = 'kafkacat -C -b ' + KAFKA_BROKER_URLS + ' -X api.version.request=true -X security.protocol=sasl_ssl -X sasl.mechanisms=PLAIN -X sasl.username=token -X sasl.password="' + KAFKA_API_KEY + '" -t ' + KAFKA_PUB_TOPIC
          # Rewrite the file with the updated JSON
          with open(TEMP_FILE, 'w') as temp_file:
            json.dump(j, temp_file)
        if LOG_DETAIL: print('--> MQTT: ' + MQTT_PUB_COMMAND + TEMP_FILE)
        discard = subprocess.run(MQTT_PUB_COMMAND + TEMP_FILE, shell=True)

    #except:
    #  if LOG_EXCEPT: print('*** Exception in main achatina loop! ***')
    #  pass

    # Pause briefly (to not hog the CPU too much on small machines)
      if LOG_SLEEP: print('Sleeping for ' + str(SLEEP_BETWEEN_CALLS) + ' seconds...')
      time.sleep(SLEEP_BETWEEN_CALLS)
