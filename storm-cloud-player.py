#!/usr/bin/python

import sys
import getopt
import argparse
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from os import listdir
from os.path import isfile, join
import re
import random
import pygame
import time
import configparser
import pprint
import datetime

from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *

from modules import ambiance
from modules import constant

#
# get ambiance datas
#
def getAmbiance(name):
  global generalDeltaMin, generalDeltaMax, generalTitle

  ambianceFile = "ambiance/" + name + ".cfg"
  debug('Ambiance ' + name + ' (' + ambianceFile + ')')

  if os.path.isfile(ambianceFile):
    ambiance = configparser.ConfigParser()
    ambiance.read(ambianceFile)

    if ambiance.has_option('general', 'deltaMin'):
      generalDeltaMin = ambiance.getint('general', 'deltaMin')

    if ambiance.has_option('general', 'deltaMax'):
      generalDeltaMax = ambiance.getint('general', 'deltaMax')

    if ambiance.has_option('general', 'title'):
      generalTitle = ambiance.get('general', 'title')

    return ambiance

  print('Ambiance nor found!')
  sys.exit(2)

  return False

if __name__ == "__main__":
#  main(sys.argv[1:])

  parser = argparse.ArgumentParser(description="Alarm-clock Ambiance service")
  parser.add_argument("-v", "--verbose", help="verbose mode", action='store_true')
  parser.add_argument("-V", "--volume", help="volume (0 > 100)", type=int)

  args = parser.parse_args()

  oAmbiance = ambiance.ambiance()
  if args.verbose:
    oAmbiance.verbose = True

  oAmbiencePid = configparser.ConfigParser()
  oAmbianceConf = oAmbiance.getAmbiance()

  while True:

    remainingSecond = oAmbiance.getRemainingSeconds()
    print(remainingSecond)
    if os.path.isfile(constant.AMBIANCE_PID):

      remainingTime = oAmbiance.getRemainingTime()
      print('Start ' + remainingTime.strftime("%Y-%m-%d %H:%M:%S"))

      # init and play background if exist
#      oAmbiance.playBackground()
    
      # init events if exist
#      events = oAmbiance.loadEvents()
    
#      eventCurrent = None
#      eventDelta = random.randint(generalDeltaMin, generalDeltaMax)
#      print('wait ' + str(eventDelta) + ' seconds for next event')
    
#    if not os.path.isfile('ambience.pid'):
#      print('wait ' + str(eventDelta) + ' seconds for next event')
    
#      oAmbiencePid = configparser.ConfigParser()
    
#    oAmbiance.playBackground()
#      events = oAmbiance.loadEvents()
#      print(events)
    
#      oAmbianceConf = configparser.ConfigParser()
#      oAmbianceConf.read(constant.AMBIANCE_CONF)
#      iLight = int(oAmbianceConf.get('general', 'light', fallback=constant.THUNDERLIGHT_OFF))

#    oAmbiencePid.read(constant.AMBIANCE_PID)

#    unixTimeLimit = oAmbiencePid.getfloat('general', 'limit')
#    unixTimeNow = time.mktime(datetime.datetime.now().timetuple())

#    if unixTimeNow>unixTimeLimit:
#      print('limit:' + str(unixTimeLimit))
#      print('unixTimeNow:' + str(unixTimeNow))
#      pygame.mixer.music.fadeout(4000)
#      pygame.mixer.music.stop()
#      time.sleep(4.25)
#      sys.exit(0)

#    if eventCurrent==None and eventDelta==0:
#      eventIndex = random.randint(0, len(eventsDict)-1)

#      eventDuration = eventsDict[eventIndex]['duration']
#      oEvent = eventsDict[eventIndex]['oEvent']
#      eventCurrent=oEvent.play()
#      print('play event ' + eventsDict[eventIndex]['file'] + ' (' + str(eventsDict[eventIndex]['duration']) + 's)')

#    if eventCurrent!=None and eventCurrent.get_busy():
#      time.sleep(0.0)
#    else:
#      sys.stdout.write("%i \r" % (eventDelta))

#      eventCurrent=None
#      if eventDelta<=0:
#        eventDelta = random.randint(generalDeltaMin, generalDeltaMax)
#        print('wait ' + str(eventDelta) + ' seconds for next event')
#      else:
#        eventDelta -= 1

#    sys.stdout.flush()

    time.sleep(1.0)