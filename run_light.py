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

#  strip = Adafruit_NeoPixel(
#      constant.THUNDERLIGHT_LED_COUNT, 
#      constant.THUNDERLIGHT_LED_PIN, 
#      constant.THUNDERLIGHT_LED_FREQ_HZ, 
#      constant.THUNDERLIGHT_LED_DMA, 
#      constant.THUNDERLIGHT_LED_INVERT, 
#      constant.THUNDERLIGHT_LED_BRIGHTNESS, 
#      constant.THUNDERLIGHT_LED_CHANNEL, 
#      ws.SK6812_STRIP_RGBW
#  )
#  strip.begin()
#  strip.setPixelColor(0, Color(139, 156, 200,100));
#  strip.show();
#  time.sleep(1.0)
#  strip.setPixelColor(0, Color(0, 0, 255,100));
#  strip.show();

  oThunderlight = thunderlight.thunderlight()
 
  oThunderlight.strike()
 
  time.sleep(4.0)
  oThunderlight.turnAllOff()

