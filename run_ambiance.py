#!/usr/bin/python

import sys
import getopt
import argparse
import os
import re
import random
import pygame
import time
import ConfigParser
import pprint
import datetime

from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *

isVerbose = True
ambiancePid = 'ambiance.pid'
ambianceName = 'default'
ambianceDuration = 5
ambianceVolume = 50
eventsDict = {}
generalDeltaMin = 10
generalDeltaMax = 20
generalTitle = ''

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
def main(argv):
  global ambianceName, ambianceDuration, ambianceVolume

  parser = argparse.ArgumentParser(description="Alarm-clock Ambiance service")
  parser.add_argument("-v", "--verbose", help="verbose mode", action='store_true')
  parser.add_argument("-n", "--ambiance", help="ambiance name (default '" + ambianceName + "')")
  parser.add_argument("-d", "--duration", help="duration (in minutes)", type=int)
  parser.add_argument("-V", "--volume", help="volume (0 > 100)", type=int)

  args = parser.parse_args()

  if args.duration:
    ambianceDuration = args.duration

  if args.ambiance:
    ambianceName = args.ambiance

  if args.volume:
    ambianceVolume = args.volume

  now = datetime.datetime.now()
  limit = now + datetime.timedelta(0, 0, 0, 0, int(ambianceDuration))
  unixTime = time.mktime(limit.timetuple())
  debug('Limit ' + limit.strftime("%Y-%m-%d %H:%M:%S") + ' (unixtime:' + str(unixTime) + ')')
  debug('Volume:' + str(ambianceVolume))

  pidFile = ambiancePid
  pid = ConfigParser.ConfigParser()
  pid.add_section('general')
  pid.set('general', 'duration', str(ambianceDuration))
  pid.set('general', 'limit', unixTime)
  pid.set('general', 'volume', ambianceVolume)

  with open(pidFile, 'wb') as configfile:
    pid.write(configfile)

#
# get ambiance datas
#
def getAmbiance(name):
  global generalDeltaMin, generalDeltaMax, generalTitle

  ambianceFile = "ambiance/" + name + ".cfg"
  debug('Ambiance ' + name + ' (' + ambianceFile + ')')

  if os.path.isfile(ambianceFile):
    ambiance = ConfigParser.ConfigParser()
    ambiance.read(ambianceFile)

    if ambiance.has_option('general', 'deltaMin'):
      generalDeltaMin = ambiance.getint('general', 'deltaMin')

    if ambiance.has_option('general', 'deltaMax'):
      generalDeltaMax = ambiance.getint('general', 'deltaMax')

    if ambiance.has_option('general', 'title'):
      generalTitle = ambiance.get('general', 'title')

    return ambiance

  print('Ambiance nor found!')
  sys.exit(2)

  return False

#
# playing background wav
#
def playBackground(oAmbiance):
  if oAmbiance.has_section('background'):
    backgroundFile = 'sounds/' + oAmbiance.get('background', 'sound')
    if os.path.isfile(backgroundFile):
      background = pygame.mixer.Sound(backgroundFile)

      loops = -1
      if oAmbiance.has_option('background', 'loop'):
        loops = oAmbiance.getint('background', 'loop')

      volume = 100.0
      if oAmbiance.has_option('background', 'volume'):
        volume = oAmbiance.getfloat('background', 'volume')

      volume = ((ambianceVolume * volume) / 100) / 100

      debug('play background ' + backgroundFile + ' (loops:' + str(loops) + ', volume:' + str(volume) + ')')
      background.set_volume(volume)
      background.play(loops)

#
# load events wav
#
def loadEvents(oAmbiance):
  global eventsDict
  eventIndex = 0
  for section in oAmbiance.sections():
    events = re.match(r'^event([0-9].*)$', section)
    if events:
      eventFile = 'sounds/' + oAmbiance.get(section, 'sound')
      debug('find event ' + eventFile + ' (' + section + ')')

      if os.path.isfile(eventFile):
        oEvent = pygame.mixer.Sound(eventFile)

        volume = 100.0
        if oAmbiance.has_option(section, 'volume'):
          volume = oAmbiance.getfloat(section, 'volume')

        volume = ((ambianceVolume * volume) / 100) / 100
        
        oEvent.set_volume(volume)

        eventsDict[eventIndex] = {'file' : eventFile, 'oEvent' : oEvent, 'duration' : oEvent.get_length(), 'volume' : volume}
        debug('..loaded (duration:' + str(oEvent.get_length()) + ', volume:' + str(volume) + ')')
        eventIndex += 1
      else:
        debug('..not found')

  #debug('play background ' + backgroundFile + ' (' + str(loops) + ')')

  debug('has ' + str(len(eventsDict)) + ' event(s) loaded')

if __name__ == "__main__":
  main(sys.argv[1:])

  # load ambiance file
  oAmbiance = getAmbiance(ambianceName)

  # init sound mixer
  pygame.mixer.init();
  #freq, size, chan = pygame.mixer.get_init()
  #pygame.mixer.init(freq, size, chan, 3072)

  # init and play background if exist
  playBackground(oAmbiance)

  # init events if exist
  loadEvents(oAmbiance)

  eventCurrent = None
  eventDelta = random.randint(generalDeltaMin, generalDeltaMax)
  debug('wait ' + str(eventDelta) + ' seconds for next event')

  if not os.path.isfile('ambience.pid'):
    debug('wait ' + str(eventDelta) + ' seconds for next event')

  oAmbiencePid = ConfigParser.ConfigParser()

  while True:

    oAmbiencePid.read(ambiancePid)
    unixTimeLimit = oAmbiencePid.getfloat('general', 'limit')
    unixTimeNow = time.mktime(datetime.datetime.now().timetuple())

    if unixTimeNow>unixTimeLimit:
      debug('limit:' + str(unixTimeLimit))
      debug('unixTimeNow:' + str(unixTimeNow))
      pygame.mixer.music.fadeout(4000)
      pygame.mixer.music.stop()
      time.sleep(4.25)
      sys.exit(0)

    if eventCurrent==None and eventDelta==0:
      eventIndex = random.randint(0, len(eventsDict)-1)

      eventDuration = eventsDict[eventIndex]['duration']
      oEvent = eventsDict[eventIndex]['oEvent']
      eventCurrent=oEvent.play()
      debug('play event ' + eventsDict[eventIndex]['file'] + ' (' + str(eventsDict[eventIndex]['duration']) + 's)')

    if eventCurrent!=None and eventCurrent.get_busy():
      time.sleep(0.0)
    else:
      sys.stdout.write("%i \r" % (eventDelta))

      eventCurrent=None
      if eventDelta<=0:
        eventDelta = random.randint(generalDeltaMin, generalDeltaMax)
        debug('wait ' + str(eventDelta) + ' seconds for next event')
      else:
        eventDelta -= 1

    sys.stdout.flush()

    time.sleep(1.0)