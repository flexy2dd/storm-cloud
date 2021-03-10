#!/usr/bin/python
# -*- coding: utf-8 -*-

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
import ConfigParser

# ===========================================================================
# alarm Class
# ===========================================================================

class alarm():

  alarmsConf = 'alarms.cfg'

  def __init__(self):
    self.alarmsFile = self.alarmsConf
    self.alarmsList = self.getList(True)
    
  def getList(self, bOnlyEnable = False):
    
    data = {}
    
    if os.path.isfile(self.alarmsFile):
      alarms = ConfigParser.ConfigParser()
      alarms.read(self.alarmsFile)
      
      for section in alarms.sections():        
        if alarms.has_option(section, 'time'):
          
          bEnable = alarms.getboolean(section, 'enable')
          
          if (bOnlyEnable and not bEnable):
            continue

          sDays = alarms.get(section, 'days')
          sTime = alarms.get(section, 'time')
          
          data[section] = {} 
          data[section]['key']    = section
          data[section]['enable'] = bEnable
          data[section]['name']   = alarms.get(section, 'name')
          data[section]['time']   = sTime
          data[section]['days']   = string.split(sDays, ',')

    return data

  def disable(self, alarmKey):
    alarm = ConfigParser.ConfigParser()
    alarms.read(self.alarmsFile)
    
    if alarm.has_section(alarmKey):
      
      alarm.remove_section(alarmKey)
      alarm.setboolean(alarmKey, 'enable', 'false')
    
      with open(self.alarmsFile, 'wb') as configfile:
        alarm.write(configfile)

      return True
    
    return False
    
  def enable(self, alarmKey):    
    alarm = ConfigParser.ConfigParser()
    alarms.read(self.alarmsFile)
    
    if alarm.has_section(alarmKey):
      
      alarm.remove_section(alarmKey)
      alarm.setboolean(alarmKey, 'enable', 'true')
    
      with open(self.alarmsFile, 'wb') as configfile:
        alarm.write(configfile)

      return True

    return False
    
  def delete(self, alarmKey):    
    alarm = ConfigParser.ConfigParser()
    alarms.read(self.alarmsFile)
    
    if alarm.has_section(alarmKey):
      
      alarm.remove_section(alarmKey)
      
      with open(self.alarmsFile, 'wb') as configfile:
        alarm.write(configfile)
        
      return True
    
    return False

  def update(self, sTime, aDays = ['mon','tue','wed','thu','fri'], sName = 'default', bEnable = True):
    self.add(sTime, aDays, sName, bEnable)
      
  def add(self, sTime, aDays = ['mon','tue','wed','thu','fri'], sName = 'default', bEnable = True):
    
    m = hashlib.sha1()
    m.update(sTime)
    m.update(','.join(aDays))
    m.update(sName)
    alarmKey = m.hexdigest()
 
    alarm = ConfigParser.ConfigParser()
    alarm.add_section(alarmKey)
    alarm.set(alarmKey, 'time', str(sTime))
    alarm.set(alarmKey, 'days', ','.join(aDays))
    alarm.set(alarmKey, 'name', sName)
    alarm.set(alarmKey, 'enable', bEnable)
    
    with open(self.alarmsFile, 'wb') as configfile:
      alarm.write(configfile)
      
    return alarmKey
    
  def isRun(self):
    for alarmKey in self.alarmsList:
      alarm = self.alarmsList[alarmKey]
      
      aAlarmTime = string.split(alarm['time'], ':')
      tAlarmTime = datetime.time(hour = int(aAlarmTime[0]), minute = int(aAlarmTime[1]), second=0)
            
      nowTime = datetime.datetime.now().replace(microsecond=0) 
      #pprint.pprint(nowTime)
      if ((nowTime.time() == tAlarmTime) and (datetime.datetime.now().strftime('%a').lower() in alarm['days'])):
        return alarmKey
        
      
    return False
    
  def check(self, oScreen):
    alarmKey = self.isRun()
    oScreen.alarmState = 0
    
    if alarmKey != False: 
      alarm = ConfigParser.ConfigParser()
      alarm.read(self.alarmsFile)
    
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
        time.sleep(0.25)
        
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
