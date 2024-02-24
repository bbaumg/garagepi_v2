import os
import logging
import time
import yaml
import json
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import ssl
import traceback
import sys
import signal
import http.client
import urllib
from datetime import datetime
from bme280 import bme280

class garagepi:

  def __init__(self):
    self.logger = self._init_logger()
    self.logger.critical("**************************************************")
    self.logger.critical("*")
    self.logger.critical("* Starting Program")
    self.logger.critical("*")
    self.logger.critical("**************************************************")
    self.logger.critical(os.uname())
    self.logger.critical(GPIO.RPI_INFO)
    self.logger.critical("Log Level = " + str(self.logger.getEffectiveLevel()))

    self.appSettings = self.loadSettings()
    
    signal.signal(signal.SIGTERM, self._handle_sigterm)
  
  def _init_logger(self):
    # Setup logging
    logLevel = logging.CRITICAL
    #logLevel = logging.ERROR
    #logLevel = logging.WARNING
    #logLevel = logging.INFO
    #logLevel = logging.DEBUG
    logFormat = '%(asctime)s - %(module)s %(funcName)s - %(levelname)s - %(message)s'
    logDateFormat = '%Y-%m-%d %H:%M:%S'
    logFilename = 'garagepi.log'
    #logHandlers = [logging.FileHandler(logFilename)]
    logHandlers = [logging.FileHandler(logFilename), logging.StreamHandler()]
    logging.basicConfig(level = logLevel, format = logFormat, datefmt = logDateFormat, handlers = logHandlers)
    logger = logging.getLogger(__name__)
    return logger
  
  def _handle_sigterm(self, sig, frame):
    self.logger.critical("SIGTERM recieved:  Program Exiting")
    self.stop()
  
  def loadSettings(self):
    self.logger.critical("Reading config file")
    with open("settings.yaml", 'r') as stream:
      appSettings=yaml.safe_load(stream)
    return appSettings
  
  def start(self):
    logging.getLogger().setLevel(self.appSettings['LOGLEVEL'])
    self.logger.critical("Changed log level to " + str(self.logger.getEffectiveLevel()))
    
    #  Could not put with the setting section due to loging level being set too high to output.
    #  But don't want it on all loads, because it contains passwords/keys
    self.logger.debug("Settings Loaded:  " + str(self.appSettings))

    try:
      while True:
        self.logger.info("================================ Top of Loop ================================")

        # Read the environmental sensor and store in a dictionaries for later use
        sensor = bme280.bme280()
        sensorData = dict()
        sensorData = sensor.readBME280Data()
        self.logger.debug("Sensor Data:  " + str(sensorData))
        
        # Build a JSON message for the sensor data
        mqttMessageJson = {
          'temperature': round(sensorData['TempF']),
          'humidity': round(sensorData['Humidity'], 0),
          'pressure': round(sensorData['Pressure'], 0)
        }
        self.logger.debug("Create MQTT message to send :  " + str(mqttMessageJson))

        # Setup MQTT Connection
        mqttClient = mqtt.Client(self.appSettings['MQTT']['CLIENTID'])
        mqttClient.username_pw_set(self.appSettings['MQTT']['USER'], self.appSettings['MQTT']['PASS'])

        # Attempt to connect
        try:
          mqttClient.connect(self.appSettings['MQTT']['BROKER'], self.appSettings['MQTT']['PORT'])
        except Exception as error:
          self.logger.error("ERROR!!!  Unable to connect to MQTT Server!")
          self.logger.error("**Error Msg:  " + str(error))
        else:
          mqttRetrun = mqttClient.publish(self.appSettings['MQTT']['TOPIC'], json.dumps(mqttMessageJson))
          self.logger.debug("MQTT Response:  " + str(mqttRetrun))
        
        # Pause the loop
        self.logger.info("Pausing for " + str(self.appSettings['FREQUENCY']) + " seconds")
        time.sleep(self.appSettings['FREQUENCY'])

    except KeyboardInterrupt:
      self.logger.critical("Keyboard Interrupt:  Program Exiting")
      self.stop()
  
  def stop(self):
    self.logger.critical("!!!!!!!!!!!!!!!!!!!!!!!!! Exiting Program !!!!!!!!!!!!!!!!!!!!!!!!!")
    self.alert(message="garagepi on " + str(os.uname()[1]) + " has exited", priority="-1")
    GPIO.cleanup()
    self.logger.critical("Program Ending = " + os.uname().nodename + ":" + __file__)
    self.logger.critical("!!!!!!!!!!!!!!!!!!!!!!!!! End Program !!!!!!!!!!!!!!!!!!!!!!!!!")
    sys.exit(0)
  
  def alert(self, message, priority="0",sound="none"):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
      urllib.parse.urlencode({
        "token": self.appSettings['PUSHOVER']['API_TOKEN'],
        "user": self.appSettings['PUSHOVER']['USER_KEY'],
        "title": "GaragePi Notification",
        "sound": sound,
        "priority": priority,
        "message": message,
      }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

if __name__ == '__main__':
  service = garagepi()
  service.start()

  # TO DO LIST:
