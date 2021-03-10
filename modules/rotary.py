import RPi.GPIO as GPIO
import time
from threading import Timer
from modules import constant
from os import getenv
from pprint import pprint

class rotary():
  
  def __init__(self, CLK=None, DT=None, SW=None, polling=1, device=None):
    self.pinCLK = CLK
    self.pinDT = DT
    self.pinSW = SW

    pprint(self.pinCLK)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self.pinCLK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(self.pinDT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(self.pinSW, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    self.lastState = GPIO.input(self.pinCLK)
    self.polling = polling
                  
  def warnFloatDepreciation(self, i):
    if isinstance(i, float):
      warnings.warn('Float numbers as `scale_min`, `scale_max`, `sw_debounce_time` or `step` will be deprecated in the next major release. Use integers instead.', DeprecationWarning)

  def setup(self, **params):
    if 'loop' in params and params['loop'] is True:
      self.counter_loop = True
    else:
      self.counter_loop = False

    if 'scale_min' in params:
      assert isinstance(params['scale_min'], int) or isinstance(params['scale_min'], float)
      self.min_counter = params['scale_min']
      self.counter = self.min_counter
      self.warnFloatDepreciation(params['scale_min'])

    if 'scale_max' in params:
      assert isinstance(params['scale_max'], int) or isinstance(params['scale_max'], float)
      self.max_counter = params['scale_max']
      self.warnFloatDepreciation(params['scale_max'])

    if 'step' in params:
      assert isinstance(params['step'], int) or isinstance(params['step'], float)
      self.step = params['step']
      self.warnFloatDepreciation(params['step'])

    if 'chg_callback' in params:
      assert callable(params['chg_callback'])
      self.chg_callback = params['chg_callback']

  def _switch_press(self):
    now = time() * 1000
    if not self.sw_triggered:
      if self.latest_switch_press is not None:
        if now - self.latest_switch_press > self.sw_debounce_time:
          self.sw_callback()
      else:
        self.sw_callback()
    self.sw_triggered = True
    self.latest_switch_press = now

  def _switch_release(self):
    self.sw_triggered = False

  def _clockwise_tick(self):
    if self.counter + self.step <= self.max_counter:
      self.counter += self.step
    elif self.counter + self.step > self.max_counter:
      self.counter = self.min_counter if self.counter_loop is True else self.max_counter

    if self.inc_callback is not None:
      self.inc_callback(self.counter)
    if self.chg_callback is not None:
      self.chg_callback(self.counter)

  def _counterclockwise_tick(self):
    if self.counter - self.step >= self.min_counter:
      self.counter -= self.step
    elif self.counter - self.step < self.min_counter:
      self.counter = self.max_counter if self.counter_loop is True else self.min_counter

    if self.inc_callback is not None:
      self.dec_callback(self.counter)
    if self.chg_callback is not None:
      self.chg_callback(self.counter)

  def watch(self):
    while True:
      try:
        if self.sw_callback:
          if GPIO.input(self.sw) == GPIO.LOW:
            self._switch_press()
          else:
            self._switch_release()

        clkState = GPIO.input(self.pinCLK)
        dtState = GPIO.input(self.pinDT)

        if clkState != self.clk_last_state:
          if dtState != clkState:
            self._clockwise_tick()
          else:
            self._counterclockwise_tick()

        self.clk_last_state = clkState
        sleep(self.polling_interval / 1000)

      except BaseException as e:
        GPIO.cleanup()
        break
    return