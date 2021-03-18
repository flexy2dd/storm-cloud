#!/usr/bin/python

import sys
import getopt
import argparse
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import re
import random
import time
import configparser
import pprint
import datetime
from rpi_ws281x import *
from modules import thunderlight
from modules import constant

from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *

#
# debug message
#
def debug(message):
  global isVerbose
  if isVerbose:
    print(message)

#
# main
#
if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Alarm-clock Ambiance service")
  parser.add_argument("-v", "--verbose", help="verbose mode", action='store_true')
  parser.add_argument("-f", "--delayFactor", help="delay factor volume (0 > 100)", type=int)
  parser.add_argument("-s", "--strikeFactor", help="strike factor", type=int)
  parser.add_argument("-b", "--brightFactor", help="bright factor", type=int)
  parser.add_argument("-d", "--delay", help="delay", type=int)

  args = parser.parse_args()

  oThunderlight = thunderlight.thunderlight()

  if args.verbose:
    oThunderlight.verbose = True

  delayFactor = None
  strikeFactor = None
  brightFactor = None
  delay = None

  if args.delayFactor:
    delayFactor = args.delayFactor

  if args.strikeFactor:
    strikeFactor = args.strikeFactor

  if args.brightFactor:
    brightFactor = args.brightFactor
    
  if args.delay:
    delay = args.delay
 
  oThunderlight.strike(delay=delay, delayFactor=delayFactor, strikeFactor=strikeFactor, brightFactor=brightFactor, focused=None)
 
  oThunderlight.turnAllOff()

