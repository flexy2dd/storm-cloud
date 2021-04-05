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
from aiohttp import web
from modules import constant
from modules import ambiance

parser = argparse.ArgumentParser(description="Storm-cloud server service")
parser.add_argument("-v", "--verbose", help="verbose mode", action='store_true')
args = parser.parse_args()

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
  remainingSeconds = oAmbiance.getRemainingSeconds()
  await sio.emit('update_remaining', {'remainingSeconds': str(remainingSeconds)})

## SNOOZE
@sio.event
async def launch_snooze(sid, data):
  oAmbiance = ambiance.ambiance()
  snooze = oAmbiance.setSnooze(data)
  oAmbiance.start();
  await sio.emit('update_snooze', {'snooze': str(data)})

@sio.event
async def stop_snooze(sid, data):
  oAmbiance = ambiance.ambiance()
  oAmbiance.stop();
  remainingSeconds = oAmbiance.getRemainingSeconds()
  await sio.emit('update_remaining', {'remainingSeconds': str(remainingSeconds)})

@sio.event
async def get_snooze(sid, data):
  oAmbiance = ambiance.ambiance()
  snooze = oAmbiance.getSnooze()
  await sio.emit('update_snooze', {'snooze': str(snooze)})
  
@sio.event
async def set_snooze(sid, data):
  oAmbiance = ambiance.ambiance()
  snooze = oAmbiance.setSnooze(data)
  await sio.emit('update_snooze', {'snooze': str(data)})

## RAIN
@sio.event
async def get_rain(sid):
  oAmbiance = ambiance.ambiance()
  rain = oAmbiance.getRain()
  await sio.emit('update_rain', {'rain': str(rain)})

@sio.event
async def set_rain(sid, data):
  oAmbiance = ambiance.ambiance()
  oAmbiance.setRain(data)
  await sio.emit('update_rain', {'rain': str(data)})

## THUNDER
@sio.event
async def get_thunder(sid):
  oAmbiance = ambiance.ambiance()
  thunder = oAmbiance.getThunder()
  await sio.emit('update_thunder', {'thunder': str(thunder)})

@sio.event
async def set_thunder(sid, data):
  oAmbiance = ambiance.ambiance()
  oAmbiance.setThunder(data)
  await sio.emit('update_thunder', {'thunder': str(data)})

## LIGHT
@sio.event
async def get_light(sid):
  oAmbiance = ambiance.ambiance()
  light = oAmbiance.getLight()
  await sio.emit('update_light', {'light': str(light)})

@sio.event
async def set_light(sid, data):
  oAmbiance = ambiance.ambiance()
  oAmbiance.setLight(data)
  await sio.emit('update_light', {'light': str(data)})

## VOLUME
@sio.event
async def get_volume(sid):
  oAmbiance = ambiance.ambiance()
  volume = oAmbiance.getVolume()
  if args.verbose: print('get volume ' + str(volume))
  await sio.emit('update_volume', {'volume': str(volume)})

@sio.event
async def set_volume(sid, data):
  if args.verbose: print('set volume ' + str(data))
  oAmbiance = ambiance.ambiance()
  oAmbiance.setVolume(data)
  await sio.emit('update_volume', {'volume': str(data)})

app.router.add_static('/static', 'server/static')
app.router.add_get('/', index)

if __name__ == '__main__':
    web.run_app(app, port=80)
    
