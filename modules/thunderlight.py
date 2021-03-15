import re
import os
import time
import string
import datetime
import random
import pprint
from modules import constant
import configparser
from rpi_ws281x import *

# ===========================================================================
# ambiance Class
# ===========================================================================

class thunderlight():

  def __init__(self):
    self.strip = Adafruit_NeoPixel(
      constant.THUNDERLIGHT_LED_COUNT, 
      constant.THUNDERLIGHT_LED_PIN, 
      constant.THUNDERLIGHT_LED_FREQ_HZ, 
      constant.THUNDERLIGHT_LED_DMA, 
      constant.THUNDERLIGHT_LED_INVERT, 
      constant.THUNDERLIGHT_LED_BRIGHTNESS, 
      constant.THUNDERLIGHT_LED_CHANNEL, 
      ws.SK6812_STRIP_RGBW
    )
    self.strip.begin()
                           
    self.currentDataPoint = 0
    self.numLed = constant.THUNDERLIGHT_LED_COUNT

    # delay factor beetween the lightnings
    self.delayFactor = 50
    # factor to calculate the number of lightnings in a sequence  
    self.strikeFactor = 9
    # factor to calculate the brightness
    self.brightFactor = 500

    # Set tooo True if you to keep the lightning focused in one LED.
    self.focused = False
                           
    self.callbacks = [
      self.simpleMovingAverage, 
      self.randomMovingAverage
    ]
    
    self.simpleMovingAveragePrevious = 0
    self.randomMovingAveragePrevious = 0

    # Simple moving average plot
    self.yValues = [
       0,
       7,
       10,
       9,
       7.1,
       7.5,
       7.4,
       12,
       15,
       10,
       0,
       3,
       3.5,
       4,
       1,
       7,
       1
    ]
    self.numYValues = len(self.yValues)

  def Exit(self):
    self.turnAllOff()

  def turnAllOff(self):
    for i in range(0, self.numLed):
      self.strip.setPixelColor(i, 0);

    self.strip.show();
    
  def turnOn(self, iPixel, iColor = 255):
    self.strip.setPixelColor(iPixel, iColor);
    self.strip.show();
  
  def getDelayFactor(self):
    return self.delayFactor

  def getStrikeFactor(self):
    return self.strikeFactor

  def getBrightFactor(self):
    return self.brightFactor
    
  def lightningStrike(self, iPixel):
    callback = self.callbacks[random.randrange(0, len(self.callbacks)-1)]
    brightness = callback()

    scaledWhite = int(abs(float(brightness) * self.brightFactor))
    print("scaledWhite: " + str(scaledWhite))
    
    self.strip.setPixelColor(iPixel, Color(scaledWhite, scaledWhite, scaledWhite))
    self.strip.show()

    time.sleep(random.randrange(5, self.delayFactor) / 100)

    self.currentDataPoint += 1
    self.currentDataPoint = self.currentDataPoint % self.numYValues

  def strike(self, delay=None, delayFactor=None, strikeFactor=None, brightFactor=None, focused=None):

    if brightFactor!=None:
      self.brightFactor = brightFactor

    if delayFactor!=None:
      self.delayFactor = delayFactor
    
    if strikeFactor!=None:
      self.strikeFactor = strikeFactor

    if focused!=None:
      self.focused = focused

    if delay!=None:
      print('strike delay ' + str(delay))
      time.sleep(delay)

    iPixel = random.randrange(0, self.numLed)
    for i in range(0, random.randrange(5, self.strikeFactor)):
      if self.focused:
        lightningStrike(iPixel)
      else:
        iPixel = random.randrange(0, self.numLed)
        self.lightningStrike(iPixel)

    self.turnAllOff()
      
  def simpleMovingAverage(self):
    startingValue = self.currentDataPoint
    endingValue = (self.currentDataPoint + 1) % self.numYValues

    simpleMovingAverageCurrent = self.simpleMovingAveragePrevious + (self.yValues[startingValue])/self.numYValues - (self.yValues[endingValue])/self.numYValues

    self.simpleMovingAveragePrevious = simpleMovingAverageCurrent

    return simpleMovingAverageCurrent
    
  def randomMovingAverage(self):
    firstValue = random.randrange(1, 10)
    secondValue = random.randrange(1, 10)

    randomMovingAverageCurrent = randomMovingAveragePrevious + firstValue/self.numYValues - secondValue/self.numYValues;

    randomMovingAveragePrevious = randomMovingAverageCurrent

    return randomMovingAverageCurrent

    return 0