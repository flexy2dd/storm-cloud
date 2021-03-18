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
import asyncio
import concurrent.futures

from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *

from modules import ambiance
from modules import constant
from modules import thunderlight

pool = concurrent.futures.ThreadPoolExecutor()
          
async def strike(oThunderlight, delayTime, delayFactor, strikeFactor, brightFactor):
  oThunderlight.strike(delay=delayTime, delayFactor=delayFactor, strikeFactor=strikeFactor, brightFactor=brightFactor)
 
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
        eventDelta = random.randint(oAmbiance.iDeltaMin, oAmbiance.iDeltaMax)

        if args.verbose: print('wait ' + str(eventDelta) + ' seconds for next event')

      else:

        if eventCurrent==None and eventDelta==0:

          eventIndex = random.randint(0, len(eventsList)-1)
        
          eventDuration = eventsList[eventIndex]['duration']
          oEvent = eventsList[eventIndex]['oEvent']

          delayTime = eventsList[eventIndex]['lightDelay'] / 1000
          lightDelay = eventsList[eventIndex]['lightDelay']
          lightStrike = eventsList[eventIndex]['lightStrike']
          lightBright = eventsList[eventIndex]['lightBright']
    
          pool.submit(asyncio.run, strike(oThunderlight, delayTime=delayTime, delayFactor=lightDelay, strikeFactor=lightStrike, brightFactor=lightBright))

          eventCurrent=oEvent.play()

          if args.verbose: print('play event ' + eventsList[eventIndex]['file'] + ' (' + str(eventsList[eventIndex]['duration']) + 's)')
        
        if eventCurrent!=None and eventCurrent.get_busy():
          if args.verbose: print('Wait next event')
          time.sleep(0.0)
        else:
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

    time.sleep(1.0)