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
import RPi.GPIO as GPIO
import logging

from PIL import ImageFont, ImageDraw, Image
from luma.core.render import canvas

from modules import network
from modules import menu
from modules import screen
from modules import rotary
from modules import constant
from modules import ambiance

# ===========================================================================
# Menu definition
# ===========================================================================
menu_data = {
  'title': "General", 'type': constant.MENU_MENU,
  'options':[
    { 'title': "Snooze", 'type': constant.MENU_MENU,
      'options': [
        { 'title': "Lancer", 'type': constant.MENU_COMMAND, 'command': 'setSnooze', 'enable': True },
        { 'title': "Arreter", 'type': constant.MENU_COMMAND, 'command': 'setStop', 'enable': True },
      ]
    },
    { 'title': "Ambiance", 'type': constant.MENU_MENU,
      'options': [
        { 'title': "Pluie", 'type': constant.MENU_COMMAND, 'command': 'setRain', 'enable': True },
        { 'title': "Orage", 'type': constant.MENU_COMMAND, 'command': 'setThunder', 'enable': True },
        { 'title': "Eclairs", 'type': constant.MENU_COMMAND, 'command': 'setLight', 'enable': True },
        { 'title': "Volume", 'type': constant.MENU_COMMAND, 'command': 'setVolume', 'enable': True },
      ]
    },
    { 'title': "Parametres", 'type': constant.MENU_MENU,
      'options': [
        { 'title': "Volume", 'type': constant.MENU_COMMAND, 'command': 'setVolume', 'enable': True },
        { 'title': "Informations", 'type': 'viewInfos', 'enable': True}
#        { 'title': "Heure", 'type': constant.MENU_COMMAND, 'command': 'setTime', 'enable': True },
#        { 'title': "Date", 'type': constant.MENU_COMMAND, 'command': 'setDate', 'enable': True },
      ]
    },
  ]
}

parser = argparse.ArgumentParser(description="Storm-cloud Ambiance service")
parser.add_argument("-v", "--verbose", help="verbose mode", action='store_true')
parser.add_argument("-l", "--log", help="Log level")
args = parser.parse_args()

# ===========================================================================
# Logging
# ===========================================================================
logLevel = getattr(logging, 'ERROR', None)
if args.log:
  logLevel = getattr(logging, args.log.upper(), None)

if os.path.isfile(constant.AMBIANCE_CONF):
  confFile = configparser.ConfigParser()
  confFile.read(constant.AMBIANCE_CONF)

  if confFile.has_option('general', 'debug'):
    logLevel = confFile.get('general', 'debug')
    logLevel = getattr(logging, logLevel.upper(), None)

logging.basicConfig(filename='/var/log/storm-cloud-manager.log', level=logLevel)

# ===========================================================================
# Screen
# ===========================================================================
oScreen = screen.screen()
oScreen.cls()
oScreen.logger = logging
oScreen.debug('init clock')
oScreen.debug("ip: %s" % network.get_lan_ip())
oScreen.sleep(0.5)

swithRelease = 0

# ===========================================================================
# Rotary encoder
# ===========================================================================

swithRelease = 0
swithRotate = 0

def rotaryRotateCall(direction):
  global swithRotate
  swithRotate = 1
  print('Rotate to ' + direction)

def rotarySwitchCall(switchStatus):
  global swithRelease
  if switchStatus=='release':
    swithRelease = 1

oRotary = rotary.rotary(
  switch_callback=rotarySwitchCall,
  rotate_callback=rotaryRotateCall
)
oRotary.logger = logging

screenStatus = 0

# Continually update 
while(True):
  try:

    if screenStatus==0:
      if swithRelease==1 or swithRotate == 1:
        screenStatus = 1
        swithRelease = 0
        swithRotate = 0
        oScreen.cls()
        oScreen.remainingTime()
        affStart = time.time()
        secondsWait = constant.MENU_WAIT_SECONDS
        waitStep = oScreen.width / (float(secondsWait) * 1000)
        oScreen.draw.rectangle((0, oScreen.height-1, oScreen.width, oScreen.height-1), 0, 1)
      else:
        oScreen.pulse()

    elif screenStatus==1:

      # Loop until return key is pressed
      while True:
        affCurrent = time.time() - affStart
        oScreen.draw.rectangle((0, oScreen.height-1, (affCurrent * waitStep) * 1000, oScreen.height-1), 0, 0)
      
        if swithRelease==1:
          oRotary.triggerDisable()
          oScreen.cls()
          oMenu = menu.menu()
          oMenu.logger = logging
          oMenu.processmenu(oScreen, oRotary, menu_data)
          oRotary.setSwitchCallback(rotarySwitchCall)
          oRotary.setRotateCallback(rotaryRotateCall)
          oRotary.triggerEnable()
          swithRelease = 0
          screenStatus = 0
          oScreen.cls()
          break
      
        oScreen.display()
      
        if affCurrent>secondsWait:
          screenStatus = 0
          oScreen.cls()
          break

    time.sleep(0.25)
  except:
#    print("Unexpected error:", sys.exc_info()[0])
    raise
    
