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

  ambianceConf = 'ambiance.cfg'

  def __init__(self):
    self.ambianceFile = self.ambianceConf
    
  def check(self, oScreen):
    alarmKey = self.isRun()
    oScreen.alarmState = 0
    
    if alarmKey != False: 
      alarm = configparser.ConfigParser()
      alarm.read(self.ambianceFile)
    
      soundFile = '%s/../sounds/alarm/%s' % (os.path.dirname(__file__), alarm.get(alarmKey, 'sound'))
      print('play ',soundFile)
      if os.path.isfile(soundFile):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(soundFile)
        pygame.mixer.music.play(-1)

      while(True):
        if not (GPIO.input(constant.GPIO_KEY_SNOOZE)):
          pygame.mixer.music.stop()
          break

        oScreen.alarmPlay()
        time.sleep(0.05)
        
  def getKey(self, item):
    return item['time']
    
  def getNext(self):
    aList = []
    
    nowTime = datetime.datetime.now().replace(microsecond=0) 
    iDayNow = int(datetime.datetime.now().strftime('%w'))
    
    aDaysStr = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']
    
    if iDayNow==6:
      aDays = [6, 0]
    else:
      aDays = [iDayNow, iDayNow+1]
    
    iIdx = 0
    for iDay in aDays:
      iIdx += 1
      for alarmKey in self.alarmsList:
        alarm = self.alarmsList[alarmKey]
        
        aAlarmTime = string.split(alarm['time'], ':')
        tAlarmTime = datetime.datetime.now().replace(hour = int(aAlarmTime[0]), minute = int(aAlarmTime[1]), second=0, microsecond=0) 
        
        if iIdx>1:
          tAlarmTime += datetime.timedelta(days=iIdx-1)  
        
        if ((nowTime < tAlarmTime) and (aDaysStr[iDay] in alarm['days'])):
          aList.append(tAlarmTime)

    aList.sort()
    if (len(aList)>0):
      diffTime = aList[0] - nowTime
     
      d = diffTime.days  # days
      h = divmod(diffTime.seconds, 3600)  # hours
      m = divmod(h[1], 60)  # minutes
      s = m[1] # seconds

      text = ''
      hours = h[0] 
      if d>0:
        hours += d*24
      
      if hours>0:
        text += '%dh ' % (h[0])
        
      if m[0]>1:
        text += '%d mins' % (m[0])
      elif m[0]>=0:
        text += '%d min' % (m[0])
        
      if int(m[0])==0 and int(hours)==0 and int(s)>0:
        text = '%d sec' % (s)
          
      return text
      
    return ''
      
  def status(self, oScreen):
    isEnable = False
    sNext = ''
    
    for alarmKey in self.alarmsList:
      isEnable = True 
      sNext = self.getNext()
      break      
     
    oScreen.alarmInfos(isEnable, sNext)

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