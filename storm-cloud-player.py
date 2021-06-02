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
import asyncio
import concurrent.futures
import logging

from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *

from modules import ambiance
from modules import constant
from modules import screen
from modules import thunderlight
from modules import config

pool = concurrent.futures.ThreadPoolExecutor()
          
async def strike(oThunderlight, delayTime, delayFactor, strikeFactor, brightFactor):
  oThunderlight.strike(delay=delayTime, delayFactor=delayFactor, strikeFactor=strikeFactor, brightFactor=brightFactor)
 
if __name__ == "__main__":

  parser = argparse.ArgumentParser(description="Storm-cloud Ambiance service")
  parser.add_argument("-v", "--verbose", help="verbose mode", action='store_true')
  parser.add_argument("-V", "--volume", help="volume (0 > 100)", type=int)
  parser.add_argument("-l", "--log", help="Log level")
  parser.add_argument("-s", "--start", help="start mode", action='store_true')

  args = parser.parse_args()

  # ===========================================================================
  # Logging
  # ===========================================================================
  logLevel = getattr(logging, 'ERROR', None)
  if args.log:
    logLevel = getattr(logging, args.log.upper(), None)
  
  if os.path.isfile(constant.AMBIANCE_CONF):
    confFile = config.config()
    confFile.read(constant.AMBIANCE_CONF)
  
    if confFile.has_option('general', 'debug'):
      logLevel = confFile.get('general', 'debug')
      logLevel = getattr(logging, logLevel.upper(), None)
  
  logging.basicConfig(filename='/var/log/storm-cloud-player.log', level=logLevel)

  oAmbiance = ambiance.ambiance()
  oAmbiance.logger = logging

  if args.verbose:
    oAmbiance.verbose = True

  oAmbianceConf = oAmbiance.getAmbiance()

  if args.start:
    oAmbiance.start()
   
  isRunning = False

  oThunderlight = thunderlight.thunderlight()
  oThunderlight.logger = logging
  if args.verbose:
    oThunderlight.verbose = True

  oThunderlight.turnAllOff()

  while True:

    remainingSecond = oAmbiance.getRemainingSeconds()
    if remainingSecond > 0:
      
      if not oAmbiance.isRunning():
        if args.verbose: print('Is not running Start it! '  + oAmbiance.getRemainingTime())

        # init and play background if exist
        oAmbiance.playBackground()

        # init events if exist
        eventsList = oAmbiance.loadEvents()

        eventCurrent = None
        eventDelta = random.randint(oAmbiance.currentDeltaMin, oAmbiance.currentDeltaMax)
        oAmbiance.setEventDelta(eventDelta)

        if args.verbose: print('wait ' + str(eventDelta) + ' seconds for next event')

      else:

        if eventCurrent==None and eventDelta==0:

          eventIndex = random.randint(0, len(eventsList)-1)
        
          eventDuration = eventsList[eventIndex]['duration']
          oEvent = eventsList[eventIndex]['oEvent']
          sEventFile = eventsList[eventIndex]['file']

          delayTime = eventsList[eventIndex]['lightDelay'] / 1000
          lightDelay = eventsList[eventIndex]['lightDelay']
          lightStrike = eventsList[eventIndex]['lightStrike']
          lightBright = eventsList[eventIndex]['lightBright']

          iLight = oAmbiance.getLight()
          if iLight==constant.THUNDERLIGHT_ON:
            pool.submit(asyncio.run, strike(oThunderlight, delayTime=delayTime, delayFactor=lightDelay, strikeFactor=lightStrike, brightFactor=lightBright))

          thunderVolume = float(oAmbiance.getThunderVolume())
          iVolume = ((iAmbianceVolume * thunderVolume) / 100) / 100
          if (iVolume>0):
            oEvent.set_volume(iVolume)

          eventCurrent=oEvent.play()

          if args.verbose: print('play event ' + eventsList[eventIndex]['file'] + ' (' + str(eventsList[eventIndex]['duration']) + 's)')
        
        if eventCurrent!=None and eventCurrent.get_busy():
          if args.verbose: print('Wait next event (' + str(eventDelta) + ')')
          time.sleep(0.0)
        else:
          eventCurrent=None
          if eventDelta<=0:
            
            deltas = oAmbiance.getThunderDeltas()
            oAmbiance.currentDeltaMin = deltas['min']
            oAmbiance.currentDeltaMax = deltas['max']
            eventDelta = random.randint(oAmbiance.currentDeltaMin, oAmbiance.currentDeltaMax)
            oAmbiance.setEventDelta(eventDelta)
            if args.verbose: print('wait ' + str(eventDelta) + ' seconds for next event')
          else:
            oAmbiance.setEventPos(eventDelta)
            eventDelta -= 1

        iAmbianceVolume = oAmbiance.getVolume()
        if oAmbiance.currentVolume != iAmbianceVolume:
          if oAmbiance.currentBackground != None:
            iVolume = ((iAmbianceVolume * oAmbiance.currentBackgroundVolume) / 100) / 100
            if args.verbose: print('change volume to ' + str(iAmbianceVolume))
            oAmbiance.currentVolume = iAmbianceVolume
            oAmbiance.currentBackground.set_volume(iVolume)

    else:
      if args.verbose: print('remaining is over')

      if oAmbiance.isRunning():

        if args.verbose: print('Stop it!')

        oThunderlight.turnAllOff()
        oAmbiance.stop();

    time.sleep(0.5)
