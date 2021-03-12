import RPi.GPIO as GPIO
import time
import math
from pprint import pprint
from modules import constant
from modules import network
from modules import ambiance

class menu():

  def __init__(self):
    self.swithRelease = 0
  
  # This function displays the appropriate menu and returns the option selected
  def runmenu(self, screen, rotary, menu, parent):
  
    # work out what text to display as the last menu option
    if parent is None:
      lastoption = "Sortie"
    else:
      lastoption = "Retour %s" % parent['title']
  
    self.optioncount = len(menu['options']) # how many options in this menu
  
    self.pos = 0 #pos is the zero-based index of the hightlighted menu option. Every time runmenu is called, position returns to 0, when runmenu ends the position is returned and tells the program what opt$
    oldpos = None # used to prevent the screen being redrawn every time
    affStart = time.time()
    secondsWait = 60
  
    milliseconds = float(secondsWait) * 1000
    totalWidth = screen.width
    waitStep = totalWidth / milliseconds
    screen.draw.rectangle((0, screen.height-1, totalWidth, screen.height-1), 0, 1)
  
    # Loop until return key is pressed
    while True:
      affCurrent = time.time() - affStart
      waitWidth = (affCurrent * waitStep) * 1000
      screen.draw.rectangle((0, screen.height-1, waitWidth, screen.height-1), 0, 0)
      screen.display()
  
      if self.pos != oldpos:
        affStart = time.time()
        screen.draw.rectangle((0, screen.height-1, totalWidth, screen.height-1), 0, 1)
        oldpos = self.pos
        screen.setText(0, 0, menu['title'], fill="white")
  
        # Display all the menu items, showing the 'pos' item highlighted
        for index in range(self.optioncount):
          iTop = 10 + (index * screen.fontSize)
  
          if self.pos == index:
            screen.setRect(0, iTop, screen.width-1, iTop + screen.fontSize, 1, 1)
            screen.setText(0, iTop, "%d - %s" % (index+1, menu['options'][index]['title']), 0)
          else:
            screen.setRect(0, iTop, screen.width-1, iTop + screen.fontSize, 0, 0)
            screen.setText(0, iTop, "%d - %s" % (index+1, menu['options'][index]['title']), 1)
  
        # Now display Exit/Return at bottom of menu
        iTop = 10 + (self.optioncount * screen.fontSize)
        if self.pos == self.optioncount:
          screen.setRect(0, iTop, screen.width-1, iTop + screen.fontSize, 1, 1)
          screen.setText(0, iTop, "%d - %s" % (self.optioncount+1, lastoption), 0)
        else:
          screen.setRect(0, iTop, screen.width-1, iTop + screen.fontSize, 0, 0)
          screen.setText(0, iTop, "%d - %s" % (self.optioncount+1, lastoption), 1)
  
        screen.display()
        # finished updating screen
  
      if affCurrent>secondsWait:
        return -1

      if self.swithRelease==1:
        self.swithRelease = 0
        break
  
    # return index of the selected item
    return self.pos
  
  def rotaryRotateCall(self, direction):
    if direction=='left':
      if self.pos < self.optioncount:
        self.pos += 1
      else:
        self.pos = self.optioncount
    elif direction=='right':
      if self.pos > 0:
        self.pos += -1
      else:
        self.pos = 0
  
  def rotarySwitchCall(self, switchStatus):
    if switchStatus=='release':
      self.swithRelease = 1
  
  # This function calls showmenu and then acts on the selected item
  def processmenu(self, screen, rotary, menu, parent=None):
    self.optioncount = len(menu['options'])
    self.exitmenu = False
    
    rotary.setSwitchCallback(self.rotarySwitchCall)
    rotary.setRotateCallback(self.rotaryRotateCall)
    rotary.triggerEnable()
    
    while not self.exitmenu: #Loop until the user exits the menu
      getin = self.runmenu(screen, rotary, menu, parent)
      if getin == self.optioncount:
         self.exitmenu = True
      elif getin == -1:
        self.exitmenu = True
      elif menu['options'][getin]['type'] == 'viewInfos':
        self.viewInfos(screen)
      elif menu['options'][getin]['type'] == constant.MENU_COMMAND:
  
        if menu['options'][getin]['command'] == 'setAmbiance':
          self.setAmbiance(screen)
  
        if menu['options'][getin]['command'] == 'setVolume':
          self.setVolume(screen)
  
        screen.cls()
      elif menu['options'][getin]['type'] == constant.MENU_MENU:
            screen.cls() #clears previous screen on key press and updates display based on pos
            self.processmenu(screen, rotary, menu['options'][getin], menu) # display the submenu
            screen.cls() #clears previous screen on key press and updates display based on pos
      elif menu['options'][getin]['type'] == constant.MENU_EXIT:
            self.exitmenu = True

    rotary.triggerDisable()
  
  def viewInfos(self, screen):
    screen.cls()
    screen.setText(0, 10, "ip: %s" % network.get_lan_ip(), 1)


    left = 10
    top = 15
    
    screen.draw.rectangle((left, top, left+30, top+30), outline="white", fill="white")

    level = int(network.get_wifi_signal())
    level = 0
    if level>0 and level<=25:
      screen.draw.bitmap((left, top), screen.logoWifi25, fill="black")
    elif level>25 and level<=50:
      screen.draw.bitmap((left, top), screen.logoWifi50, fill="black")
    elif level>50 and level<=75:
      screen.draw.bitmap((left, top), screen.logoWifi75, fill="black")
    elif level>75:
      screen.draw.bitmap((left, top), screen.logoWifi100, fill="black")
    else:
      screen.draw.bitmap((left, top), screen.logoWifi0, fill="black")

    screen.display()

    while(True):
      if self.swithRelease==1:
        self.swithRelease = 0
        break

      time.sleep(0.10)
  
  def setSnooze(self, screen):

    if self.swithRelease==1:
      self.swithRelease = 0
#      break

      time.sleep(0.10)

  def setRain(self, screen):

    oAmbiance = ambiance.ambiance()
    oAmbiance.getRain()

    if self.swithRelease==1:
      self.swithRelease = 0
#      break

    time.sleep(0.10)

  def setStorm(self, screen):

    if self.swithRelease==1:
      self.swithRelease = 0
#      break

    time.sleep(0.10)

  def setVolume(self, screen):
    oAmbiance = ambiance.ambiance()
    oAmbiance.setVolumeScreen(screen)
