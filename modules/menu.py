import RPi.GPIO as GPIO
import time
import math
from pprint import pprint
from modules import constant
from modules import network
from modules import ambiance

# This function displays the appropriate menu and returns the option selected
def runmenu(screen, menu, parent):

  # work out what text to display as the last menu option
  if parent is None:
    lastoption = "Sortie"
  else:
    lastoption = "Retour %s" % parent['title']

  optioncount = len(menu['options']) # how many options in this menu

  pos=0 #pos is the zero-based index of the hightlighted menu option. Every time runmenu is called, position returns to 0, when runmenu ends the position is returned and tells the program what opt$
  oldpos=None # used to prevent the screen being redrawn every time
  affStart=time.time()
  secondsWait=10

  milliseconds=float(secondsWait)*1000
  totalWidth=screen.screen.width
  waitStep=totalWidth/milliseconds
  screen.draw.rectangle((0, screen.screen.height-1, totalWidth, screen.screen.height-1), 0, 1)

  # Loop until return key is pressed
  while True:
    #affCurrent=int(math.floor(time.time()-affStart))
    affCurrent=time.time()-affStart
    waitWidth=(affCurrent*waitStep)*1000
    screen.draw.rectangle((0, screen.screen.height-1, waitWidth, screen.screen.height-1), 0, 0)
    screen.display()

    if pos != oldpos:
      affStart=time.time()
      screen.draw.rectangle((0, screen.screen.height-1, totalWidth, screen.screen.height-1), 0, 1)
      oldpos = pos
      screen.setText(0, 0, menu['title'], 1)

      # Display all the menu items, showing the 'pos' item highlighted
      for index in range(optioncount):
        iTop = 10 + (index * screen.fontSize)

        if pos==index:
          screen.setRect(0, iTop, screen.width-1, iTop + screen.fontSize, 1, 1)
          screen.setText(0, iTop, "%d - %s" % (index+1, menu['options'][index]['title']), 0)
        else:
          screen.setRect(0, iTop, screen.width-1, iTop + screen.fontSize, 0, 0)
          screen.setText(0, iTop, "%d - %s" % (index+1, menu['options'][index]['title']), 1)

      # Now display Exit/Return at bottom of menu
      iTop = 10 + (optioncount * screen.fontSize)
      if pos==optioncount:
        screen.setRect(0, iTop, screen.width-1, iTop + screen.fontSize, 1, 1)
        screen.setText(0, iTop, "%d - %s" % (optioncount+1, lastoption), 0)
      else:
        screen.setRect(0, iTop, screen.width-1, iTop + screen.fontSize, 0, 0)
        screen.setText(0, iTop, "%d - %s" % (optioncount+1, lastoption), 1)

      screen.display()
      # finished updating screen

    if affCurrent>secondsWait:
      return -1

    if not (GPIO.input(constant.GPIO_KEY_UP)): # down arrow
      if pos < optioncount:
        pos += 1
      else:
        pos = optioncount
    elif not (GPIO.input(constant.GPIO_KEY_DOWN)): # up arrow
      if pos > 0:
        pos += -1
      else:
        pos = 0
    elif not (GPIO.input(constant.GPIO_KEY_MENU)): # set
      break

  # return index of the selected item
  return pos

# This function calls showmenu and then acts on the selected item
def processmenu(screen, menu, parent=None):
  optioncount = len(menu['options'])
  exitmenu = False
  while not exitmenu: #Loop until the user exits the menu
    getin = runmenu(screen, menu, parent)
    if getin == optioncount:
        exitmenu = True
    elif getin == -1:
      exitmenu = True
    elif menu['options'][getin]['type'] == 'viewInfos':
      viewInfos(screen)
    elif menu['options'][getin]['type'] == constant.MENU_COMMAND:

      if menu['options'][getin]['command'] == 'setAmbiance':
        setAmbiance(screen)

      if menu['options'][getin]['command'] == 'setAmbianceVol':
        setAmbianceVol(screen)

      screen.cls()
    elif menu['options'][getin]['type'] == constant.MENU_MENU:
          screen.cls() #clears previous screen on key press and updates display based on pos
          processmenu(screen, menu['options'][getin], menu) # display the submenu
          screen.cls() #clears previous screen on key press and updates display based on pos
    elif menu['options'][getin]['type'] == constant.MENU_EXIT:
          exitmenu = True

def viewInfos(screen):
  screen.cls()
  screen.setText(0, 10, "ip: %s" % network.get_lan_ip(), 1)
  screen.display()
  while(True):
    if not (GPIO.input(constant.GPIO_KEY_MENU)):
      break

    time.sleep(0.10)

def setAmbiance(screen):
	oAmbiance = ambiance.ambiance()
	oAmbiance.setSelectScreen(screen)

def setAmbianceVol(screen):
  oAmbiance = ambiance.ambiance()
  oAmbiance.setVolumeScreen(screen)
