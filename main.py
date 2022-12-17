import os
import logging
import time
import yaml
import json
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import ssl
from datetime import datetime
from bme280.bme280 import bme280


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

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# END SETUP - BEGIN FUNCTIONS
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# END FUNCTIONS - BEGIN PROGRAM
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
logger.critical("**************************************************")
logger.critical("*")
logger.critical("* Starting Program")
logger.critical("*")
logger.critical("**************************************************")
logger.critical(os.uname())
logger.critical(GPIO.RPI_INFO)
logger.critical("Log Level = " + str(logLevel))

logger.critical("Reading config file")
with open("settings.yaml", 'r') as stream:
  appSettings=yaml.safe_load(stream)
  logger.info(appSettings)

logLevelNew = appSettings['LOGLEVEL']
logger.critical("Changing log level from " + str(logLevel) + " to " + str(logLevelNew))
logging.getLogger().setLevel(logLevelNew)

try:
  while True:
    logger.info("================================ Top of Loop ================================")
    loopTime = datetime.now()

    # Read the environmental sensor and store in a dictionaries for later use
    sensor = bme280()
    sensorData = dict()
    sensorData = sensor.readBME280Data()
    logger.debug(sensorData)

    mqttMessageJson = {
      'temperature': round(sensorData['TempF']),
      'humidity': round(sensorData['Humidity'], 0),
      'pressure': round(sensorData['Pressure'], 0)
    }
    logger.debug(mqttMessageJson)

    mqttClient = mqtt.Client(appSettings['MQTT']['CLIENTID'])
    mqttClient.username_pw_set(appSettings['MQTT']['USER'], appSettings['MQTT']['PASS'])
    mqttClient.connect(appSettings['MQTT']['BROKER'], appSettings['MQTT']['PORT'])
    mqttRetrun = mqttClient.publish(appSettings['MQTT']['TOPIC'], json.dumps(mqttMessageJson))
    logger.debug(mqttRetrun)


    logger.info("Pausing for a few seconds")
    time.sleep(60)

except KeyboardInterrupt:
  logger.critical("Keyboard Interrupt:  Program Exiting")
  print(datetime.now().strftime("Program Shutdown -- %Y/%m/%d -- %H:%M  -- Goodbye! \n"))
finally:
  logger.critical("!!!!!!!!!!!!!!!!!!!!!!!!! Exiting Program !!!!!!!!!!!!!!!!!!!!!!!!!")
  GPIO.cleanup()
  logger.critical("Program Ending = " + os.uname().nodename + ":" + __file__)
  #sendSMS("Program Ended = " + os.uname().nodename + ":" + __file__)
  logger.critical("!!!!!!!!!!!!!!!!!!!!!!!!! End Program !!!!!!!!!!!!!!!!!!!!!!!!!")
