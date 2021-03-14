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

  oThunderlight = thunderlight.thunderlight()
 
  oThunderlight.strike()
 
  time.sleep(2.0)
  oThunderlight.turnAllOff()

