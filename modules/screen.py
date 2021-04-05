import datetime
import os
import codecs
import time
import math
import pprint

from luma.core.interface.serial import i2c, spi, pcf8574
from luma.core.interface.parallel import bitbang_6800
from luma.core.render import canvas
from luma.oled.device import ssd1306

from PIL import ImageFont, ImageDraw, Image

from modules import constant
from modules import ambiance

# ===========================================================================
# screen Class
# ===========================================================================

class screen():
  
  def __init__(self):
    i2cbus = i2c()
    self.device = ssd1306(i2cbus)
    self.device.show()
    
    self.image = Image.new(self.device.mode, self.device.size)
    self.draw = ImageDraw.Draw(self.image)

    self.remainingPos = self.device.width
    self.pulseStatus = 1
    self.pulsePos = 1
    self.fontSize = 10
    self.maxScreenLines = 6
    self.width = self.device.width
    self.height = self.device.height

    self.font = ImageFont.truetype('%s/../fonts/FreeSans.ttf' % os.path.dirname(__file__), self.fontSize)

    self.draw.text((0, 0), text="Init screen", font=self.font, fill='white')
    self.display()
      
    self.debugLines = []
    
    self.logoWifi100 = Image.open('%s/../icons/wifi-100.png' % os.path.dirname(__file__))
    self.logoWifi75  = Image.open('%s/../icons/wifi-75.png' % os.path.dirname(__file__))
    self.logoWifi50  = Image.open('%s/../icons/wifi-50.png' % os.path.dirname(__file__))
    self.logoWifi25  = Image.open('%s/../icons/wifi-25.png' % os.path.dirname(__file__))
    self.logoWifi0   = Image.open('%s/../icons/wifi-0.png' % os.path.dirname(__file__))
    
  def display(self):
    self.device.display(self.image)
    
  def cls(self, fill = 0):
    self.draw.rectangle(self.device.bounding_box, outline="black", fill="black")
    self.display()
    time.sleep(0.2)
    
  def setText(self, left, top, text, fill):
    self.draw.text((left, top), text, font=self.font, fill=fill)
  
  def setRect(self, left, top, width, height, outline, fill):
    self.draw.rectangle((left, top, width, height), outline, fill)
    
  def debug(self, text):
    self.debugLines.append(text)
    linesCount = len(self.debugLines) # how many lines
    
    if (linesCount > self.maxScreenLines):
      self.debugLines.pop(0)
      linesCount = len(self.debugLines)

    for index in range(linesCount):
      iTop = (index * self.fontSize)
      self.draw.text((0, iTop),  self.debugLines[index], fill="white")

    self.display()
    
  def remainingTime(self):

    oAmbiance = ambiance.ambiance()
    remainingtime = oAmbiance.getRemainingSeconds()
   
    if remainingtime>0:
      h = divmod(remainingtime, 3600)  # hours
      m = divmod(h[1], 60)  # minutes

      print(str(remainingtime) + ' - ' + str(h) + ':' + str(m))

      hours = math.trunc(h[0])
      minutes = math.trunc(m[0])
     
    else:
      hours = 0
      minutes = 0

    font = ImageFont.truetype('%s/../fonts/digital-7mono.ttf' % os.path.dirname(__file__), 55)

    print(str(hours) + ':' + str(minutes))

    self.draw.text((0, 5), '{:0>2}'.format(hours) , font=font, fill=1)
    self.draw.text((65, 5), '{:0>2}'.format(minutes) , font=font, fill=1)
    self.draw.text((46, 5), ':' , font=font, fill=1)

  def pulse(self):

    # pulse indicator
    step = 4

#    if self.pulseStatus == 1:
#      self.pulsePos = self.pulsePos + step
#    else:
#      self.pulsePos = self.pulsePos - step
#
#    if self.pulsePos < 0:
#      self.pulsePos = self.pulsePos + (step * 2)
#      self.pulseStatus = 1

#    if self.pulsePos > self.device.width:
#      self.pulsePos = self.pulsePos - (step * 2)
#      self.pulseStatus = 0

    self.pulsePos = self.pulsePos + 1

    self.draw.rectangle((0, self.device.height-1, self.device.width, self.device.height-1), outline="black", fill="black")
    if self.pulsePos > 2:
      self.pulsePos = 0
      self.draw.rectangle((1, self.device.height-1, 1, self.device.height-1), outline="white", fill="white")
    
    oAmbiance = ambiance.ambiance()

    # remaining indicator
    remainingtimeSeconds = oAmbiance.getRemainingSeconds()
    if remainingtimeSeconds>0:
      self.remainingPos = (self.device.width / (oAmbiance.getSnooze() * 60)) * remainingtimeSeconds
      self.draw.rectangle((0, self.device.height-2, self.device.width, self.device.height-2), outline="black", fill="black")
      self.draw.rectangle((self.remainingPos, self.device.height-2, self.remainingPos, self.device.height-2), outline="white", fill="white")
    else:
      self.draw.rectangle((0, self.device.height-2, self.device.width, self.device.height-2), outline="black", fill="black")

    # storm indicator
    stormDelta = oAmbiance.getEventDelta()
    stormPos = oAmbiance.getEventPos()

    if stormPos>0 and stormDelta>0 and remainingtimeSeconds>0:
      stormPos = (self.device.width / stormDelta) * stormPos
      self.draw.rectangle((0, self.device.height-3, self.device.width, self.device.height-3), outline="black", fill="black")
      self.draw.rectangle((stormPos, self.device.height-3, stormPos, self.device.height-3), outline="white", fill="white")
    else:
      self.draw.rectangle((0, self.device.height-3, self.device.width, self.device.height-3), outline="black", fill="black")

    self.display()
    
  def sleep(self, secondsWait = 5.0):
    affStart = time.time()
    milliseconds = float(secondsWait)*1000
    step = self.device.width / milliseconds

    self.draw.rectangle((0, self.device.height-1, self.device.width, self.device.height-1), outline="black", fill="black")
    self.display()

    while True:
      affCurrent=time.time()-affStart
      width = math.floor((affCurrent*step)*1000)

      self.draw.rectangle((0, self.device.height-2, width, self.device.height-2), fill="white")
      self.display()

      if affCurrent>secondsWait:
        self.cls()
        break