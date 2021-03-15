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
import threading

from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *

from modules import ambiance
from modules import constant
from modules import thunderlight

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

async def strike(oThunderlight, delayTime):
  print('stike')
  oThunderlight.strike(delay=delayTime)
  time.sleep(5.0)
  print('stike end')

if __name__ == "__main__":
#  main(sys.argv[1:])

  parser = argparse.ArgumentParser(description="Alarm-clock Ambiance service")
  parser.add_argument("-v", "--verbose", help="verbose mode", action='store_true')
  parser.add_argument("-V", "--volume", help="volume (0 > 100)", type=int)
  parser.add_argument("-s", "--start", help="start mode", action='store_true')

  args = parser.parse_args()

  oAmbiance = ambiance.ambiance()
  if args.verbose:
    oAmbiance.verbose = True

  oAmbianceConf = oAmbiance.getAmbiance()

  if args.start:
    oAmbiance.start()
   
  isRunning = False

  oThunderlight = thunderlight.thunderlight()
 
  while True:

    remainingSecond = oAmbiance.getRemainingSeconds()
    if remainingSecond > 0:
      
      if not oAmbiance.isRunning():
        if args.verbose: print('Is not running Start it! '  + oAmbiance.getRemainingTime())

        iLight = oAmbiance.getLight()

        # init and play background if exist
        oAmbiance.playBackground()

        # init events if exist
        eventsList = oAmbiance.loadEvents()

        eventCurrent = None
        eventDelta = random.randint(constant.AMBIANCE_DELTAMIN, constant.AMBIANCE_DELTAMAX)

        if args.verbose: print('wait ' + str(eventDelta) + ' seconds for next event')

      else:

        if eventCurrent==None and eventDelta==0:

          eventIndex = random.randint(0, len(eventsList)-1)
        
          eventDuration = eventsList[eventIndex]['duration']
          oEvent = eventsList[eventIndex]['oEvent']

          print(eventsList)

#          threadStrike = threading.Thread(target=oThunderlight.strike(), args=('delay=' + eventsList[eventIndex]['lightDelay']))
#          threadStrike.start()
          strike(oThunderlight, delay=eventsList[eventIndex]['lightDelay'])
          
#          eventCurrent=oEvent.play()
                    
          #eventsList[eventIndex]['lightForce']

          if args.verbose: print('play event ' + eventsList[eventIndex]['file'] + ' (' + str(eventsList[eventIndex]['duration']) + 's)')
        
        if eventCurrent!=None and eventCurrent.get_busy():
          time.sleep(0.0)
        else:
          if args.verbose: print("%i \r" % (eventDelta))
        
          eventCurrent=None
          if eventDelta<=0:
            eventDelta = random.randint(generalDeltaMin, generalDeltaMax)
            if args.verbose: print('wait ' + str(eventDelta) + ' seconds for next event')
          else:
            eventDelta -= 1

    else:
      if args.verbose: print('remaining is over')

      if oAmbiance.isRunning():

        if args.verbose: print('Stop it!')

        oThunderlight.turnAllOff()
        oAmbiance.stop();

      #os.remove("demofile.txt") 
    
      #print(remainingSecond)
      #if os.path.isfile(oAmbiance.getFilePid()):

      #  remainingTime = oAmbiance.getRemainingTime()

#    if not os.path.isfile('ambience.pid'):
#      print('wait ' + str(eventDelta) + ' seconds for next event')
#      oAmbiencePid = configparser.ConfigParser()
#    oAmbiance.playBackground()
#      events = oAmbiance.loadEvents()
#      print(events)
#      oAmbianceConf = configparser.ConfigParser()
#      oAmbianceConf.read(constant.AMBIANCE_CONF)
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