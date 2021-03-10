import RPi.GPIO as GPIO
import time
from threading import Timer
from modules import constant
from os import getenv
from pprint import pprint

class rotary():
  
  def __init__(self, CLK=None, DT=None, SW=None, polling_interval=1, device=None):
    self.pinCLK = CLK
    self.pinDT = DT
    self.pinSW = SW

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self.pinCLK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(self.pinDT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(self.pinSW, GPIO.IN, pull_up_down=GPIO.PUD_UP)