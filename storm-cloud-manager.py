import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import re
import signal
import argparse
import time
import configparser
import pprint
import datetime
import logging
import logging.handlers
import RPi.GPIO as GPIO

from PIL import ImageFont, ImageDraw, Image
from luma.core.render import canvas

from modules import network
from modules import menu
from modules import screen
from modules import rotary
from modules import constant
#from modules import alarm
from modules import ambiance

# ===========================================================================
# Logging
# ===========================================================================
LOG_FILENAME = "/tmp/storm-cloud.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"

parser = argparse.ArgumentParser(description="Alarm-clock service")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")
parser.add_argument("-v", "--verbose", help="verbose mode", action='store_false')

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
    { 'title': "Snooze", 'type': constant.MENU_MENU,
      'options': [
        { 'title': "Lancer", 'type': constant.MENU_COMMAND, 'command': 'setSnooze' },
        { 'title': "Arreter", 'type': constant.MENU_COMMAND, 'command': 'setStop' },
      ]
    },
    { 'title': "Ambiance", 'type': constant.MENU_MENU,
      'options': [
        { 'title': "Pluie", 'type': constant.MENU_COMMAND, 'command': 'setRain' },
        { 'title': "Orage", 'type': constant.MENU_COMMAND, 'command': 'setThunder' },
        { 'title': "Eclairs", 'type': constant.MENU_COMMAND, 'command': 'setLight' },
        { 'title': "Volume", 'type': constant.MENU_COMMAND, 'command': 'setVolume' },
      ]
    },
    { 'title': "Parametres", 'type': constant.MENU_MENU,
      'options': [
        { 'title': "Volume", 'type': constant.MENU_COMMAND, 'command': 'setVolume' },
        { 'title': "Informations", 'type': 'viewInfos'}
#        { 'title': "Heure", 'type': constant.MENU_COMMAND, 'command': 'setTime' },
#        { 'title': "Date", 'type': constant.MENU_COMMAND, 'command': 'setDate' },
      ]
    },
  ]
}

# ===========================================================================
# Screen
# ===========================================================================
oScreen = screen.screen()
oScreen.cls()
oScreen.debug('init clock')
oScreen.debug("ip: %s" % network.get_lan_ip())
oScreen.sleep(0.5)

# ===========================================================================
# Rotary encoder
# ===========================================================================

swithRelease = 0

def rotaryRotateCall(direction):
  print('Rotate to ' + direction)

def rotarySwitchCall(switchStatus):
  global swithRelease
  if switchStatus=='release':
    swithRelease = 1

oRotary = rotary.rotary(
  switch_callback=rotarySwitchCall,
  rotate_callback=rotaryRotateCall
)

# Continually update 
while(True):
  try:

    if swithRelease==1:
      oRotary.triggerDisable()
      oScreen.cls()
      oMenu = menu.menu()
      oMenu.processmenu(oScreen, oRotary, menu_data)
      oRotary.setSwitchCallback(rotarySwitchCall)
      oRotary.setRotateCallback(rotaryRotateCall)
      oRotary.triggerEnable()
      swithRelease = 0
      oScreen.cls()

    # add wifi level signal on screen
    oScreen.pulse()

#    # refresh screen
#    oScreen.display()
    
    time.sleep(0.50)
  except:
#    print("Unexpected error:", sys.exc_info()[0])
    raise
    