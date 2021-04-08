import sys
import os
import re
import getopt
import signal
import argparse
import time
import configparser
import pprint
import datetime
import logging
import logging.handlers
import RPi.GPIO as GPIO
import socketio
import json
from aiohttp import web
from modules import constant
from modules import ambiance

parser = argparse.ArgumentParser(description="Storm-cloud server service")
parser.add_argument("-v", "--verbose", help="verbose mode", action='store_true')
parser.add_argument("-l", "--log", help="Log level")
args = parser.parse_args()

verbose = False
if args.verbose: 
  verbose = True

# ===========================================================================
# Logging
# ===========================================================================
logLevel = getattr(logging, 'ERROR', None)
if args.log:
  logLevel = getattr(logging, args.log.upper(), None)

if os.path.isfile(constant.AMBIANCE_CONF):
  confFile = configparser.ConfigParser()
  confFile.read(constant.AMBIANCE_CONF)

  if confFile.has_option('general', 'debug'):
    logLevel = confFile.get('general', 'debug')
    logLevel = getattr(logging, logLevel.upper(), None)

logging.basicConfig(filename='/var/log/storm-cloud-server.log', level=logLevel)

#sio = socketio.AsyncServer(logger=True, engineio_logger=True)
sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

async def index(request):
  """Serve the client-side application."""
  with open('server/index.html') as f:
    return web.Response(text=f.read(), content_type='text/html')

#@sio.event
#def connect(sid, environ):
#  print("connect ", sid)

#@sio.event
#def disconnect(sid):
#  print('disconnect ', sid)

@sio.event
async def check_remaining(sid, data):
  oAmbiance = ambiance.ambiance()
  if args.verbose: oAmbiance.verbose = True
  oAmbiance.logger = logging
  remainingSeconds = oAmbiance.getRemainingSeconds()
  await sio.emit('update_remaining', {'remainingSeconds': str(remainingSeconds)})

@sio.event
async def check_playing(sid):
  oAmbiance = ambiance.ambiance()
  if args.verbose: oAmbiance.verbose = True
  oAmbiance.logger = logging
  playing = oAmbiance.getPlaying()
  await sio.emit('update_playing', {'playing': playing})

## SNOOZE
@sio.event
async def launch_snooze(sid, data):
  if args.verbose: print('launch snooze ' + str(data))
  oAmbiance = ambiance.ambiance()
  if args.verbose: oAmbiance.verbose = True
  oAmbiance.logger = logging
  snooze = oAmbiance.setSnooze(data)
  oAmbiance.start();
  await sio.emit('update_snooze', {'snooze': str(data)})

@sio.event
async def stop_snooze(sid, data):
  if args.verbose: print('stop snooze ' + str(data))
  oAmbiance = ambiance.ambiance()
  if args.verbose: oAmbiance.verbose = True
  oAmbiance.logger = logging
  oAmbiance.stop();
  remainingSeconds = oAmbiance.getRemainingSeconds()
  await sio.emit('update_remaining', {'remainingSeconds': str(remainingSeconds)})

@sio.event
async def get_snooze(sid, data):
  oAmbiance = ambiance.ambiance()
  oAmbiance.logger = logging
  snooze = oAmbiance.getSnooze()
  await sio.emit('update_snooze', {'snooze': str(snooze)})
  
@sio.event
async def set_snooze(sid, data):
  if args.verbose: print('set snooze ' + str(data))
  oAmbiance = ambiance.ambiance()
  if args.verbose: oAmbiance.verbose = True
  oAmbiance.logger = logging
  snooze = oAmbiance.setSnooze(data)
  await sio.emit('update_snooze', {'snooze': str(data)})

## RAIN
@sio.event
async def get_rain(sid):
  oAmbiance = ambiance.ambiance()
  if args.verbose: oAmbiance.verbose = True
  oAmbiance.logger = logging
  rain = oAmbiance.getRain()
  await sio.emit('update_rain', {'rain': str(rain)})

@sio.event
async def set_rain(sid, data):
  if args.verbose: print('set rain ' + str(data))
  oAmbiance = ambiance.ambiance()
  if args.verbose: oAmbiance.verbose = True
  oAmbiance.logger = logging
  oAmbiance.setRain(data)
  await sio.emit('update_rain', {'rain': str(data)})

## THUNDER
@sio.event
async def get_thunder(sid):
  oAmbiance = ambiance.ambiance()
  if args.verbose: oAmbiance.verbose = True
  oAmbiance.logger = logging
  thunder = oAmbiance.getThunder()
  await sio.emit('update_thunder', {'thunder': str(thunder)})

@sio.event
async def set_thunder(sid, data):
  if args.verbose: print('set thunder ' + str(data))
  oAmbiance = ambiance.ambiance()
  if args.verbose: oAmbiance.verbose = True
  oAmbiance.logger = logging
  oAmbiance.setThunder(data)
  await sio.emit('update_thunder', {'thunder': str(data)})

## LIGHT
@sio.event
async def get_light(sid):
  oAmbiance = ambiance.ambiance()
  if args.verbose: oAmbiance.verbose = True
  oAmbiance.logger = logging
  light = oAmbiance.getLight()
  await sio.emit('update_light', {'light': str(light)})

@sio.event
async def set_light(sid, data):
  if args.verbose: print('set light ' + str(data))
  oAmbiance = ambiance.ambiance()
  if args.verbose: oAmbiance.verbose = True
  oAmbiance.logger = logging
  oAmbiance.setLight(data)
  await sio.emit('update_light', {'light': str(data)})

## THUNDER DELTA
@sio.event
async def get_thunder_deltas(sid):
  oAmbiance = ambiance.ambiance()
  if args.verbose: oAmbiance.verbose = True
  oAmbiance.logger = logging
  deltas = oAmbiance.getThunderDeltas()

  if args.verbose: 
    print('get thunder deltas')

  await sio.emit('update_thunder_deltas', {'deltas': { 'max': deltas['max'], 'min': deltas['min']} })

@sio.event
async def set_thunder_deltas(sid, data):
  if args.verbose: print('set thunder deltas')
  oAmbiance = ambiance.ambiance()
  if args.verbose: oAmbiance.verbose = True
  oAmbiance.logger = logging
  oAmbiance.setThunderDeltas(data)
  await sio.emit('update_thunder_deltas', {'deltas': { 'max': deltas['max'], 'min': deltas['min']} })

## THUNDER VOLUME
@sio.event
async def get_thunder_volume(sid):
  oAmbiance = ambiance.ambiance()
  if args.verbose: oAmbiance.verbose = True
  oAmbiance.logger = logging
  volume = oAmbiance.getThunderVolume()
  if args.verbose: print('get thunder volume ' + str(volume))
  await sio.emit('update_thunder_volume', {'volume': str(volume)})

@sio.event
async def set_thunder_volume(sid, data):
  if args.verbose: print('set thunder volume ' + str(data))
  oAmbiance = ambiance.ambiance()
  if args.verbose: oAmbiance.verbose = True
  oAmbiance.logger = logging
  oAmbiance.setThunderVolume(data)
  await sio.emit('update_thunder_volume', {'volume': str(data)})

## VOLUME
@sio.event
async def get_volume(sid):
  oAmbiance = ambiance.ambiance()
  if args.verbose: oAmbiance.verbose = True
  oAmbiance.logger = logging
  volume = oAmbiance.getVolume()
  if args.verbose: print('get volume ' + str(volume))
  await sio.emit('update_volume', {'volume': str(volume)})

@sio.event
async def set_volume(sid, data):
  if args.verbose: print('set volume ' + str(data))
  oAmbiance = ambiance.ambiance()
  if args.verbose: oAmbiance.verbose = True
  oAmbiance.logger = logging
  oAmbiance.setVolume(data)
  await sio.emit('update_volume', {'volume': str(data)})

@sio.event
async def set_rain_select(sid, rain, rainSelect):
  if args.verbose: print('set rain select ' + str(rain) + ' ' + str(rainSelect))
  oAmbiance = ambiance.ambiance()
  if args.verbose: oAmbiance.verbose = True
  oAmbiance.logger = logging
  oAmbiance.setRainSelect(rain, rainSelect)
  await sio.emit('update_rain_select', {'rain': str(rain), 'rainSelect': str(rainSelect)})

async def get_rain_list(request):
  rainLevel = int(request.query['rain'])
  if args.verbose: print('get rain select ' + str(rainLevel))
  oAmbiance = ambiance.ambiance()
  if args.verbose: oAmbiance.verbose = True
  oAmbiance.logger = logging
  rainSelect = oAmbiance.getRainList(rainLevel)
  return web.Response(text=json.dumps(rainSelect), status=200)

app.router.add_static('/static', 'server/static')
app.router.add_get("/rest/rain/list", get_rain_list)
app.router.add_get('/', index)

if __name__ == '__main__':
    web.run_app(app, port=80)
    
