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
    self.logoWifi25  = Image.open('%s/../icons/wifi-50.png' % os.path.dirname(__file__))
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
    
  def viewInfos(self):
    self.cls()
    self.display()
    
  def clock(self):
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute
    second = now.second             
    
    font = ImageFont.truetype('%s/../fonts/digital-7mono.ttf' % os.path.dirname(__file__), 55)
    
    self.draw.text((0, 0), now.strftime('%H') , font=font, fill=1)
    self.draw.text((65, 0), now.strftime('%M') , font=font, fill=1)
    
    if ((now.second % 2) == 0): # Toggle colon at 1Hz
      self.draw.text((46, 0), now.strftime(':') , font=font, fill=1)
    
  def alarmInfos(self, bEnable, sNext = ''): 
    font = ImageFont.truetype('%s/../fonts/fontawesome-webfont.ttf' % os.path.dirname(__file__), 12)
    if bEnable:
      text = codecs.unicode_escape_decode(constant.FONT_AWESOME_ICONS["fa-bell-o"])[0]
    else:
      text = codecs.unicode_escape_decode(constant.FONT_AWESOME_ICONS["fa-bell-slash-o"])[0]

    self.draw.text((0, 52), text, font=font, fill=1)
    
    font = ImageFont.truetype('%s/../fonts/FreeSans.ttf' % os.path.dirname(__file__), 12)
    self.draw.text((14, 52), sNext, font=font, fill=1)

  def signalLevel(self, level = 0):          
    
    left = 114
    top = 52
    
    self.draw.rectangle((left, top, left+12, top+14), outline="white", fill="white")

    level = int(level)
    if level>0 and level<=25:
      self.draw.bitmap((left, top), self.logoWifi25, fill="black")
    elif level>25 and level<=50:
      self.draw.bitmap((left, top), self.logoWifi50, fill="black")
    elif level>50 and level<=75:
      self.draw.bitmap((left, top), self.logoWifi75, fill="black")
    elif level>75:
      self.draw.bitmap((left, top), self.logoWifi100, fill="black")
    else:
      self.draw.bitmap((left, top), self.logoWifi0, fill="black")
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