import re
import os
import time
import hashlib
import string
import datetime
import pygame
import pprint
import RPi.GPIO as GPIO
import glob
import configparser
import random
from modules import constant
from os import listdir
from os.path import isfile, join

# ===========================================================================
# ambiance Class
# ===========================================================================

class ambiance():

  def __init__(self):
    self.ambianceConf = constant.AMBIANCE_CONF
    self.verbose = False
    
    # init sound mixer
    pygame.mixer.init();

  def debug(self, message):
    if self.verbose:
      print(message)

  def getAmbiance(self):
    if os.path.isfile(self.ambianceConf):
      oAmbiance = configparser.ConfigParser()
      oAmbiance.read(self.ambianceConf)
  
      if oAmbiance.has_option('general', 'title'):
        generalTitle = oAmbiance.get('general', 'title')
  
      return oAmbiance
  
    return False

  def isRunning(self):
    return True

  def getRemainingSeconds(self):
    oAmbiance = self.getAmbiance()

    nowTime = datetime.datetime.now().replace(microsecond=0)
    startTime = nowTime

    if os.path.isfile(constant.AMBIANCE_PID):
      f = open(constant.AMBIANCE_PID, "r")
      startTime = f.read()

    timeDelta = nowTime - startTime

    return timeDelta.total_seconds()

  def getRemainingTime(self, bIncludeSeconds = False):
    seconds = self.getRemainingSeconds()

    hours = seconds // (60*60)
    seconds %= (60*60)
    minutes = seconds // 60
    seconds %= 60

    if bIncludeSeconds:
      return "%02i:%02i:%02i" % (hours, minutes, seconds)
      
    return "%02i:%02i" % (hours, minutes)


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
    
    # pidFile = constant.AMBIANCE_PID
    # pid = configparser.ConfigParser()
    # pid.add_section('general')
    # pid['general']['start'] = str(unixTime)
    # with open(ambiancePid, 'w') as configfile:
    #   pid.write(configfile)

    #f = open("demofile2.txt", "a")
    #f.write("Now the file has more content!")
    #f.close()

    # now = datetime.datetime.now()
    # unixTime = time.mktime(now.timetuple())
    # if args.verbose:
    #   print('Start ' + now.strftime("%Y-%m-%d %H:%M:%S") + ' (unixtime:' + str(unixTime) + ')')

    return True
    
  def stop(self):
    return True
    
  def loadEvents(self):
    oAmbianceConf = configparser.ConfigParser()
    oAmbianceConf.read(self.ambianceConf)

    iEvent = int(oAmbianceConf.get('general', 'thunder', fallback=constant.THUNDERSTORM_LEVEL_NONE))
    iLightDelay = int(oAmbianceConf.get('light', 'delay', fallback=0))
    iLightForce = int(oAmbianceConf.get('light', 'force', fallback=1))
    iAmbianceVolume = int(oAmbianceConf.get('general', 'volume', fallback=50))

    regexp = r".*/(thunder-" + str(iEvent) + "-.*)\.(.*)"
    eventsDict = {}
    eventIndex = 0
    for file in glob.glob('sounds/thunder/*.wav'):
      result = re.match(regexp, str(file))
      if result is not None:

        self.debug('find event ' + file)

        fileRoot = result.groups()[0]
        fileExt = result.groups()[1]

        oEventConf = configparser.ConfigParser()

        eventFileConf = 'sounds/thunder/' + fileRoot + '.conf'
        if os.path.isfile(eventFileConf):
          oEventConf.read(eventFileConf)
        
        fVolume = 100.0
        if oEventConf.has_option('general', 'volume'):
          fVolume = oEventConf.getfloat('general', 'volume', fallback=100)
        
        iVolume = ((iAmbianceVolume * fVolume) / 100) / 100
        
        eventFile = '%s/../sounds/thunder/%s.%s' % (os.path.dirname(__file__), fileRoot, fileExt)
        self.debug('load event ' + eventFile)
        
        oEvent = pygame.mixer.Sound(eventFile)
        oEvent.set_volume(iVolume)
    
        self.debug('..loaded ' + str(eventIndex) + '(duration:' + str(oEvent.get_length()) + ', volume:' + str(iVolume) + ')')
        eventsDict[eventIndex] = {'file' : eventFile, 'oEvent' : oEvent, 'duration' : oEvent.get_length(), 'volume' : iVolume, 'lightDelay': iLightDelay, 'lightForce': iLightForce}
        
        eventIndex += 1
      else:
        self.debug('..not found')

    self.debug('has ' + str(len(eventsDict)) + ' event(s) loaded')
    
    return eventsDict
    
  def playBackground(self):
    oAmbianceConf = configparser.ConfigParser()
    oAmbianceConf.read(self.ambianceConf)

    iRain = int(oAmbianceConf.get('general', 'rain', fallback=constant.RAIN_LEVEL_NONE))
    iAmbianceVolume = int(oAmbianceConf.get('general', 'volume', fallback=50))

    regexp = r".*/(rain-" + str(iRain) + "-.*)\.(.*)"
    rainFiles = []
    for file in glob.glob('sounds/rain/*.wav'):
      result = re.match(regexp, str(file))
      if result is not None:
        rainFiles.append({'file': file, 'root': result.groups()[0], 'ext': result.groups()[1]})

    if len(rainFiles) <= 0:
      return False

    iIdx = 0
    if len(rainFiles) > 1:
      iIdx = random.randrange(0, len(rainFiles)-1)

    rainFile = rainFiles[iIdx]

    oBackgroundConf = configparser.ConfigParser()

    backgroundFileConf = 'sounds/rain/' + rainFile['root'] + '.conf'
    if os.path.isfile(backgroundFileConf):
      oBackgroundConf.read(backgroundFileConf)

    fVolume = 100.0
    if oBackgroundConf.has_option('general', 'volume'):
      fVolume = oBackgroundConf.getfloat('general', 'volume', fallback=100)

    iVolume = ((iAmbianceVolume * fVolume) / 100) / 100

    backgroundFile = '%s/../sounds/rain/%s.%s' % (os.path.dirname(__file__), rainFile['root'], rainFile['ext'])
    self.debug('load background ' + backgroundFile)

    if os.path.isfile(backgroundFile):
      oBackground = pygame.mixer.Sound(backgroundFile)

      self.debug('play background ' + backgroundFile + ' (volume:' + str(iVolume) + ')')

      oBackground.set_volume(iVolume)
      oBackground.play(-1)
