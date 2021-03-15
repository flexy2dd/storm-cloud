import re
import os
import time
import hashlib
import string
import datetime
import pygame
import pprint
import RPi.GPIO as GPIO
from modules import constant
import configparser

# ===========================================================================
# ambiance Class
# ===========================================================================

class ambiance():

  ambianceConf = 'config.conf'

  def __init__(self):
    self.ambianceFile = self.ambianceConf
    
   
  def getRemainingTime(self):
    ambiance=self.getAmbiance()
    nowTime = datetime.datetime.now().replace(microsecond=0) 
    return ambiance.get('general', 'runningtime', fallback=str(nowTime))

  def getAmbiance(self):
    if os.path.isfile(self.ambianceConf):
      ambiance = configparser.ConfigParser()
      ambiance.read(self.ambianceConf)
  
      if ambiance.has_option('general', 'title'):
        generalTitle = ambiance.get('general', 'title')
  
      return ambiance
  
    return False

  def setRain(self, rain):
    if os.path.isfile(self.ambianceConf):
      ambiance = configparser.ConfigParser()
      ambiance.read(self.ambianceConf)

      if int(rain) in [constant.RAIN_LEVEL_NONE, constant.RAIN_LEVEL_LIGHT, constant.RAIN_LEVEL_MODERATE, constant.RAIN_LEVEL_HEAVY]:
        ambiance.set('general', 'rain', str(rain))

        with open(self.ambianceConf, 'w') as configfile:
          ambiance.write(configfile)

        return True

    return False;

  def getRain(self):
    ambiance = self.getAmbiance()
    return int(ambiance.get('general', 'rain', fallback=constant.RAIN_LEVEL_NONE))

  def setThunder(self, thunderstorm):
    if os.path.isfile(self.ambianceConf):
      ambiance = configparser.ConfigParser()
      ambiance.read(self.ambianceConf)

      if int(thunderstorm) in [constant.THUNDERSTORM_LEVEL_NONE, constant.THUNDERSTORM_LEVEL_LIGHT, constant.THUNDERSTORM_LEVEL_MODERATE, constant.THUNDERSTORM_LEVEL_HEAVY]:
        ambiance.set('general', 'thunder', str(thunderstorm))

        with open(self.ambianceConf, 'w') as configfile:
          ambiance.write(configfile)

        return True

    return False;

  def getThunder(self):
    ambiance = self.getAmbiance()
    return int(ambiance.get('general', 'thunder', fallback=constant.THUNDERSTORM_LEVEL_NONE))

  def setLight(self, thunderlight):
    if os.path.isfile(self.ambianceConf):
      ambiance = configparser.ConfigParser()
      ambiance.read(self.ambianceConf)

      if int(thunderlight) in [constant.THUNDERLIGHT_ON, constant.THUNDERLIGHT_OFF]:
        ambiance.set('general', 'light', str(thunderlight))

        with open(self.ambianceConf, 'w') as configfile:
          ambiance.write(configfile)

        return True

    return False;

  def getLight(self):
    ambiance = self.getAmbiance()
    return int(ambiance.get('general', 'light', fallback=constant.THUNDERLIGHT_ON))

  def setVolume(self, volume):
    if os.path.isfile(self.ambianceConf):
      ambiance = configparser.ConfigParser()
      ambiance.read(self.ambianceConf)

      ambiance.set('general', 'volume', str(volume))
    
      with open(self.ambianceConf, 'w') as configfile:
        ambiance.write(configfile)

      return True

    return False;

  def getVolume(self):
    ambiance=self.getAmbiance()
    return int(ambiance.get('general', 'volume', fallback='30'))

  def setSnooze(self, snooze):
    if os.path.isfile(self.ambianceConf):
      ambiance = configparser.ConfigParser()
      ambiance.read(self.ambianceConf)

      ambiance.set('general', 'snooze', str(snooze))
    
      with open(self.ambianceConf, 'w') as configfile:
        ambiance.write(configfile)

      return True

    return False;

  def getSnooze(self):
    ambiance=self.getAmbiance()
    return int(ambiance.get('general', 'snooze', fallback='30'))

  def play(self):
    return True
    
  def stop(self):
    return True