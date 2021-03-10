#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import signal
import argparse
import time
#import ConfigParser
import pprint
import datetime
import logging
import logging.handlers
import threading

from luma.core.render import canvas
from threading import Timer

from modules import network
from modules import menu
from modules import screen
from modules import rotary
from modules import constant
#from modules import alarm
#from modules import ambiance

import RPi.GPIO as GPIO

from PIL import ImageFont, ImageDraw, Image

#from thirdparties.adafruit.Adafruit_7Segment import SevenSegment
#from thirdparties.lib_oled96.lib_oled96 import ssd1306
#from smbus import SMBus

# ===========================================================================
# Logging
# ===========================================================================
LOG_FILENAME = "/tmp/storm-cloud.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"

parser = argparse.ArgumentParser(description="Alarm-clock service")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")
parser.add_argument("-v", "--verbose", help="verbose mode", action='store_false')
parser.add_argument("-s", "--segments", help="view 7 segments clock", action='store_true')

args = parser.parse_args()
if args.log:
  LOG_FILENAME = args.log

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Make a class we can use to capture stdout and sterr in the log
class oLogger(object):
  def __init__(self, logger, level):
    """Needs a logger and a logger level."""
    self.logger = logger
    self.level = level

  def write(self, message):
    if message.rstrip() != "":
      self.logger.log(self.level, message.rstrip())

if not args.verbose:
  sys.stdout = oLogger(logger, logging.INFO)
  sys.stderr = oLogger(logger, logging.ERROR)

def signal_handler(signal, frame):
  print('You pressed Ctrl+C!')
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

signalLevel = 0

# ===========================================================================
# Menu definition
# ===========================================================================
menu_data = {
  'title': "General", 'type': constant.MENU_MENU,
  'options':[
#    { 'title': "Reveil", 'type': constant.MENU_COMMAND, 'command': 'setAlarm' },
#    { 'title': "Ambiance", 'type': constant.MENU_COMMAND, 'command': 'setAmbiance' },
    { 'title': "Ambiance", 'type': constant.MENU_MENU,
      'options': [
        { 'title': "Select", 'type': constant.MENU_COMMAND, 'command': 'setAmbiance' },
        { 'title': "Volume", 'type': constant.MENU_COMMAND, 'command': 'setAmbianceVol' }
#        { 'title': "Date", 'type': constant.MENU_COMMAND, 'command': 'setDate' },
      ]
    },
    { 'title': "Parametres", 'type': constant.MENU_MENU,
      'options': [
        { 'title': "Informations", 'type': 'viewInfos'},
#        { 'title': "Heure", 'type': constant.MENU_COMMAND, 'command': 'setTime' },
#        { 'title': "Date", 'type': constant.MENU_COMMAND, 'command': 'setDate' },
      ]
    },
  ]
}

# ===========================================================================
# Alarm
# ===========================================================================
#oAlarm = alarm.alarm()

# ===========================================================================
# Screen
# ===========================================================================
oScreen = screen.screen()

# ===========================================================================
# Button
# ===========================================================================
#GPIO.setmode(GPIO.BCM)
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(constant.GPIO_KEY_MENU, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(constant.GPIO_KEY_UP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(constant.GPIO_KEY_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(constant.GPIO_KEY_SNOOZE, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def clock():
    tClock = Timer(1.0, clock)
    tClock.start()
    
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute
    second = now.second

    #if args.segments:
    #  # Set hours
    #  clockSegment.writeDigit(0, int(hour / 10))     # Tens
    #  clockSegment.writeDigit(1, hour % 10)          # Ones
    #  # Set minutes
    #  clockSegment.writeDigit(3, int(minute / 10))   # Tens
    #  clockSegment.writeDigit(4, minute % 10)        # Ones
    #  # Toggle colon
    #  clockSegment.setColon(second % 2)              # Toggle colon at 1Hz

    # Wait a quarter second (less than 1 second to prevent colon blinking getting in phase with odd/even seconds).
    time.sleep(0.10)

oScreen.cls()
oScreen.debug('init clock')

oScreen.sleep(2.0)

# ===========================================================================
# Rotary encoder
# ===========================================================================
def rotaryEvent(position):
  print('Hello world! The position is {}' . format(position))

oRotary = rotary.rotary(
  CLK=21,
  DT=20,
  SW=16
)

oRotary.setup(scale_min=0, scale_max=100, step=1, chg_callback=rotaryEvent)
menuThread = threading.Thread(target=oRotary.watch)
menuThread.start()

# Continually update the time
while(True):
  try:

#    if not (GPIO.input(constant.GPIO_KEY_MENU)):
#      oScreen.cls()
#      menu.processmenu(oScreen, menu_data)
#      oScreen.cls()

#    # check alarms
#    oAlarm.check(oScreen) 
    
    # clear screen
    #oScreen.cls()
    
#    # add alarm status on screen
#    oAlarm.status(oScreen) 
    
#    # add clock on screen
#    oScreen.clock()
    
    # add wifi level signal on screen
    newSignalLevel = network.get_wifi_signal()
    if signalLevel != newSignalLevel:
      signalLevel = newSignalLevel
      oScreen.signalLevel(signalLevel)

#    # refresh screen
#    oScreen.display()
    
    time.sleep(0.10)
  except:
#    print("Unexpected error:", sys.exc_info()[0])
    raise
    
