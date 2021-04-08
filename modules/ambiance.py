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
import logging
from inspect import getmembers
from pprint import pprint
from modules import constant
from modules import screen
from modules import thunderlight
from os import listdir
from os.path import isfile, join

# ===========================================================================
# ambiance Class
# ===========================================================================

class ambiance():

  def __init__(self):
    self.logger = None
    self.ambianceConf = constant.AMBIANCE_CONF
    self.verbose = False
    self.currentDeltaMin = constant.AMBIANCE_DELTAMIN
    self.currentDeltaMax = constant.AMBIANCE_DELTAMAX
    self.currentRainLevel = 0
    self.currentThunderLevel = 0
    self.currentBackground = None
    self.currentBackgroundVolume = 0
    self.currentBackgroundName = ''
    self.currentVolume = 0
    
    # init sound mixer
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init();

  def log(self, level, message):
    if self.logger != None:
      if level.upper()=='DEBUG':
        self.logger.debug(message)
      elif level.upper()=='INFO':
        self.logger.info(message)
      elif level.upper()=='WARNING':
        self.logger.warning(message)
      elif level.upper()=='ERROR':
        self.logger.error(message)

  def debug(self, message):
    if self.verbose:
      self.log('DEBUG', message)
      print(message)

  def getFilePid(self):
    return '%s/../%s' % (os.path.dirname(__file__), constant.AMBIANCE_PID)

  def getFileConf(self):
    return '%s/../%s' % (os.path.dirname(__file__), constant.AMBIANCE_CONF)

  def getAmbiance(self):
    if os.path.isfile(self.ambianceConf):
      oAmbiance = configparser.ConfigParser()
      oAmbiance.read(self.ambianceConf)
  
      if oAmbiance.has_option('general', 'title'):
        generalTitle = oAmbiance.get('general', 'title')
  
      return oAmbiance
  
    return False

  def isRunning(self):
    return pygame.mixer.get_busy()

  def getRemainingSeconds(self):
    nowTime = time.mktime(datetime.datetime.now().replace(microsecond=0).timetuple())
    targetTime = nowTime

    if os.path.isfile(self.getFilePid()):
      f = open(self.getFilePid(), "r")
      targetTime = f.read()

    try:
      fTargetTime = float(targetTime)
    except:
      self.debug('targetTime is not correct erase it')
      if os.path.exists(self.getFilePid()):
        os.remove(self.getFilePid())
      return 0

    targetTime = datetime.datetime.fromtimestamp(float(targetTime)) 
    nowTime = datetime.datetime.fromtimestamp(float(nowTime))

    if targetTime < nowTime:
      self.debug('targetTime is over')
      return 0

    timeDelta = targetTime - nowTime
    
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
        ambiance.set('rain', 'rain', str(rain))

        with open(self.ambianceConf, 'w') as configfile:
          ambiance.write(configfile)

        return True

    return False;

  def getRain(self):
    ambiance = self.getAmbiance()
    return int(ambiance.get('rain', 'rain', fallback=constant.RAIN_LEVEL_NONE))

  def setThunder(self, thunderstorm):
    if os.path.isfile(self.ambianceConf):
      ambiance = configparser.ConfigParser()
      ambiance.read(self.ambianceConf)

      if int(thunderstorm) in [constant.THUNDERSTORM_LEVEL_NONE, constant.THUNDERSTORM_LEVEL_LIGHT, constant.THUNDERSTORM_LEVEL_MODERATE, constant.THUNDERSTORM_LEVEL_HEAVY]:
        ambiance.set('thunder', 'thunder', str(thunderstorm))

        with open(self.ambianceConf, 'w') as configfile:
          ambiance.write(configfile)

        return True

    return False;

  def getThunder(self):
    ambiance = self.getAmbiance()
    return int(ambiance.get('thunder', 'thunder', fallback=constant.THUNDERSTORM_LEVEL_NONE))

  def setThunderVolume(self, volume):
    if os.path.isfile(self.ambianceConf):
      ambiance = configparser.ConfigParser()
      ambiance.read(self.ambianceConf)

      ambiance.set('thunder', 'volume', str(volume))
      self.debug('set volume ' + str(volume))
    
      with open(self.ambianceConf, 'w') as configfile:
        ambiance.write(configfile)

      return True

    return False;

  def getThunderVolume(self):
    ambiance=self.getAmbiance()
    return int(ambiance.get('thunder', 'volume', fallback='80'))

  def setThunderDeltas(self, thunderDeltas):
    if os.path.isfile(self.ambianceConf):
      ambiance = configparser.ConfigParser()
      ambiance.read(self.ambianceConf)

      ambiance.set('thunder', 'deltaMax', str(thunderDeltas['max']))
      ambiance.set('thunder', 'deltaMin', str(thunderDeltas['min']))
      with open(self.ambianceConf, 'w') as configfile:
        ambiance.write(configfile)

      return True

    return False;

  def getThunderDeltas(self):
    ambiance=self.getAmbiance()
    deltaMax = int(ambiance.get('thunder', 'deltaMax', fallback=str(constant.AMBIANCE_DELTAMAX)))
    deltaMin = int(ambiance.get('thunder', 'deltaMin', fallback=str(constant.AMBIANCE_DELTAMIN)))
    return {'max': deltaMax, 'min': deltaMin}

  def setLight(self, thunderlight):
    if os.path.isfile(self.ambianceConf):
      ambiance = configparser.ConfigParser()
      ambiance.read(self.ambianceConf)

      if int(thunderlight) in [constant.THUNDERLIGHT_ON, constant.THUNDERLIGHT_OFF]:
        ambiance.set('thunder', 'light', str(thunderlight))

        with open(self.ambianceConf, 'w') as configfile:
          ambiance.write(configfile)

        return True

    return False;

  def getLight(self):
    ambiance = self.getAmbiance()
    return int(ambiance.get('thunder', 'light', fallback=constant.THUNDERLIGHT_ON))

  def setVolume(self, volume):
    if os.path.isfile(self.ambianceConf):
      ambiance = configparser.ConfigParser()
      ambiance.read(self.ambianceConf)

      ambiance.set('general', 'volume', str(volume))
      self.debug('set volume ' + str(volume))
    
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
      self.debug('set snooze ' + str(snooze))

      with open(self.ambianceConf, 'w') as configfile:
        ambiance.write(configfile)

      return True

    return False;

  def getSnooze(self):
    ambiance=self.getAmbiance()
    self.debug('get snooze')
    return int(ambiance.get('general', 'snooze', fallback='30'))

  def setEventDelta(self, delta):
    if os.path.isfile(self.ambianceConf):
      ambiance = configparser.ConfigParser()
      ambiance.read(self.ambianceConf)

      ambiance.set('event', 'delta', str(delta))

      with open(self.ambianceConf, 'w') as configfile:
        ambiance.write(configfile)

      return True

    return False;

  def getEventDelta(self):
    ambiance=self.getAmbiance()
    return int(ambiance.get('event', 'delta', fallback='1'))

  def setEventPos(self, delta):
    if os.path.isfile(self.ambianceConf):
      ambiance = configparser.ConfigParser()
      ambiance.read(self.ambianceConf)

      ambiance.set('event', 'pos', str(delta))

      with open(self.ambianceConf, 'w') as configfile:
        ambiance.write(configfile)

      return True

    return False;

  def getEventPos(self):
    ambiance=self.getAmbiance()
    return int(ambiance.get('event', 'pos', fallback='0'))

  def start(self):
    self.debug('start')
    if os.path.exists(self.getFilePid()):
      os.remove(self.getFilePid())
      self.debug('start remove pid ' + self.getFilePid())

    iSnooze = self.getSnooze()
    unixTime = time.mktime(datetime.datetime.now().replace(microsecond=0).timetuple())
    sSnooze = str(unixTime + (iSnooze * 60))
    f = open(self.getFilePid(), "w")
    f.write(sSnooze)
    self.debug('start write pid ' + self.getFilePid() + ' : ' + sSnooze)
    f.close()

    return True

  def stop(self):
    self.debug('stop')

    if os.path.exists(self.getFilePid()):
      os.remove(self.getFilePid())
      self.debug('stop remove pid ' + self.getFilePid())

    self.setPlaying('')
    pygame.mixer.fadeout(4000)
    pygame.mixer.stop()

    return True

  def thunderToStr(self, iThunder):
    switcher = {
        1: "light",
        2: "moderate",
        3: "heavy",
    }
    return switcher.get(iThunder, "none")

  def loadEvents(self):
    oAmbianceConf = configparser.ConfigParser()
    oAmbianceConf.read(self.ambianceConf)

    eventsDict = {}

    self.currentThunderLevel = self.getThunder()
    #int(oAmbianceConf.get('general', 'thunder', fallback=constant.THUNDERSTORM_LEVEL_NONE))

    if self.currentThunderLevel>0:
      iAmbianceVolume = int(oAmbianceConf.get('general', 'volume', fallback=50))
      oThunderlight = thunderlight.thunderlight()

      # default values
      fDefaultVolume = 100.00
      iDefaultLightOffset = 0
      iDefaultLightDelay = int(oThunderlight.getDelayFactor())
      iDefaultLightStrike = int(oThunderlight.getStrikeFactor())
      iDefaultLightBright = int(oThunderlight.getBrightFactor())

      oEventDefaultConf = configparser.ConfigParser()
      eventFileDefaultConf = 'sounds/thunder/thunder.conf'
      if os.path.isfile(eventFileDefaultConf):
        oEventDefaultConf.read(eventFileDefaultConf)
        fDefaultVolume = oEventDefaultConf.getfloat('general-' + str(self.currentThunderLevel), 'volume', fallback=fDefaultVolume)
        iDefaultLightOffset = oEventDefaultConf.getint('light-' + str(self.currentThunderLevel), 'offset', fallback=iDefaultLightOffset)
        iDefaultLightDelay = oEventDefaultConf.getint('light-' + str(self.currentThunderLevel), 'delay', fallback=iDefaultLightDelay)
        iDefaultLightStrike = oEventDefaultConf.getint('light-' + str(self.currentThunderLevel), 'force', fallback=iDefaultLightStrike)
        iDefaultLightBright = oEventDefaultConf.getint('light-' + str(self.currentThunderLevel), 'bright', fallback=iDefaultLightBright)

      regexp = r".*/(thunder-" + self.thunderToStr(self.currentThunderLevel) + "-.*)\.(wav|mp3)"
      eventIndex = 0
      for file in glob.glob('sounds/thunder/*'):
        result = re.match(regexp, str(file))
        if result is not None:

          self.debug('find event ' + file)

          fileRoot = result.groups()[0]
          fileExt = result.groups()[1]
      
          oEventConf = configparser.ConfigParser()
      
          eventFileConf = 'sounds/thunder/' + fileRoot + '.conf'
          if os.path.isfile(eventFileConf):
            oEventConf.read(eventFileConf)
      
          fVolume = fDefaultVolume
          if oEventConf.has_option('general', 'volume'):
            fVolume = oEventConf.getfloat('general', 'volume', fallback=fDefaultVolume)
          
          iVolume = ((iAmbianceVolume * fVolume) / 100) / 100
      
          iLightOffset = int(oEventConf.get('light', 'offset', fallback=iDefaultLightOffset))
          iLightDelay = int(oEventConf.get('light', 'delay', fallback=iDefaultLightDelay))
          iLightStrike = int(oEventConf.get('light', 'force', fallback=iDefaultLightStrike))
          iLightBright = int(oEventConf.get('light', 'bright', fallback=iDefaultLightBright))
          
          eventFile = '%s/../sounds/thunder/%s.%s' % (os.path.dirname(__file__), fileRoot, fileExt)
          self.debug('load event ' + eventFile)
          
          oEvent = pygame.mixer.Sound(eventFile)
          oEvent.set_volume(iVolume)
      
          self.debug('..loaded ' + str(eventIndex) + '(duration:' + str(oEvent.get_length()) + ', volume:' + str(iVolume) + ')')
          eventsDict[eventIndex] = {'file' : eventFile, 'oEvent' : oEvent, 'duration' : oEvent.get_length(), 'volume' : iVolume, 'lightOffset': iLightOffset, 'lightDelay': iLightDelay, 'lightStrike': iLightStrike, 'lightBright': iLightBright}
          
          eventIndex += 1
        else:
          self.debug('..not found')

    self.debug('has ' + str(len(eventsDict)) + ' event(s) loaded')
    
    return eventsDict
  
  def rainToStr(self, iRain):
    switcher = {
        1: "light",
        2: "moderate",
        3: "heavy",
    }
    return switcher.get(iRain, "none")

  def setPlaying(self, background):
    if os.path.isfile(self.ambianceConf):
      ambiance = configparser.ConfigParser()
      ambiance.read(self.ambianceConf)

      ambiance.set('play', 'background', str(background))

      with open(self.ambianceConf, 'w') as configfile:
        ambiance.write(configfile)

      return True

    return False;

  def getPlaying(self):
    ambiance = self.getAmbiance()
    return ambiance.get('play', 'background', fallback='')

  def playBackground(self):
    oAmbianceConf = configparser.ConfigParser()
    oAmbianceConf.read(self.ambianceConf)

    self.currentRainLevel = self.getRain()
    #int(oAmbianceConf.get('rain', 'rain', fallback=constant.RAIN_LEVEL_NONE))
    
    if self.currentRainLevel>0:

      iAmbianceVolume = int(oAmbianceConf.get('general', 'volume', fallback=50))
      
      fDefaultVolume = 100.00
      iDefaultDeltaMin = constant.AMBIANCE_DELTAMIN
      iDefaultDeltaMax = constant.AMBIANCE_DELTAMAX
      oDefaultConf = configparser.ConfigParser()
      fileDefaultConf = 'sounds/rain/rain.conf'
      if os.path.isfile(fileDefaultConf):
        oDefaultConf.read(fileDefaultConf)
        fDefaultVolume = oDefaultConf.getfloat('general-' + str(self.currentRainLevel), 'volume', fallback=fDefaultVolume)
        iDefaultDeltaMin = oDefaultConf.getint('general-' + str(self.currentRainLevel), 'deltaMin', fallback=iDefaultDeltaMin)
        iDefaultDeltaMax = oDefaultConf.getint('general-' + str(self.currentRainLevel), 'deltaMax', fallback=iDefaultDeltaMax)

      regexp = r".*/(rain-" + self.rainToStr(self.currentRainLevel) + "-.*)\.(wav|mp3)"
      rainFiles = []
      for file in glob.glob('sounds/rain/*'):
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
      
      fVolume = fDefaultVolume
      if oBackgroundConf.has_option('general', 'volume'):
        fVolume = oBackgroundConf.getfloat('general', 'volume', fallback=fDefaultVolume)
      
      self.currentBackgroundVolume = fVolume
      iVolume = ((iAmbianceVolume * fVolume) / 100) / 100
      self.currentVolume = iVolume
      
      deltas = self.getThunderDeltas()
      self.currentDeltaMin = deltas['min']
      self.currentDeltaMax = deltas['max']
             
#      self.currentDeltaMin = oBackgroundConf.getint('general', 'deltaMin', fallback=iDefaultDeltaMin)
#      self.currentDeltaMax = oBackgroundConf.getint('general', 'deltaMax', fallback=iDefaultDeltaMax)
      
      backgroundFile = '%s/../sounds/rain/%s.%s' % (os.path.dirname(__file__), rainFile['root'], rainFile['ext'])
      self.debug('load background ' + backgroundFile)
      
      if os.path.isfile(backgroundFile):
        oBackground = pygame.mixer.Sound(backgroundFile)
      
        self.debug('play background ' + backgroundFile + ' (volume:' + str(iVolume) + ')')

        self.setPlaying(rainFile['root'])
        self.currentBackgroundName = backgroundFile
        self.currentBackground = oBackground
        oBackground.set_volume(iVolume)
        oBackground.play(-1)
