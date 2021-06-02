import re
import os
import time
import hashlib
import string
import datetime
import pygame
import pprint
import RPi.GPIO as GPIO
import glob
import configparser
import random
import logging
from inspect import getmembers
from pprint import pprint
from modules import constant
from os import listdir
from os.path import isfile, join

# ===========================================================================
# config Class
# ===========================================================================

#_UNSET = object()

class config(configparser.ConfigParser):

#  def __init__(self):
#    self.logger = None
#    self.verbose = False
#    self.ambianceConf = constant.AMBIANCE_CONF
#    self.oConfigparser = config.config()
#
#  def read(self, filenames, encoding=None):
#    self.ambianceConf = filenames
#    self.oConfigparser.read(filenames)
#
#  def write(self, fp, space_around_delimiters=True):
#    self.oConfigparser.write(fp)
#
#  def has_option(self, section, option):
#    return self.oConfigparser.has_option(section, option)
#
#  def add_section(self, section):
#    self.oConfigparser.add_section(section)
#
#  def get(self, section, option, *, raw=False, vars=None, fallback=_UNSET):
#
#    if fallback is _UNSET:
#      return self.oConfigparser.get(section, option)
#
#    return self.oConfigparser.get(section, option, fallback=fallback)

  def set(self, section, option, value=None):

    if not self.has_section(section):
      self.add_section(section)

#    if not self.oConfigparser.has_option(option):
#      self.oConfigparser.add_option(option)

    super().set(section, option, value)

#    with open(self.ambianceConf, 'w') as configfile:
#        self.oConfigparser.write(configfile)