#!/usr/bin/python
import sys
import os

from os.path import exists

GPIO_ROOT = "/sys/class/gpio"
BACKLIGHT_PATH = GPIO_ROOT + "/gpio252"

class Backlight(object):

    def __init__(self):
        # Check if GPIO252 has already been set up
        if not exists(BACKLIGHT_PATH):
            with open(GPIO_ROOT + "/export", "w") as bfile:
                bfile.write("252")

        # Set the direction
        with open(BACKLIGHT_PATH + "/direction", "w") as bfile:
            bfile.write("out")

    def set(self, light):
        '''Turns the PiTFT backlight on or off.

        Usage:
         Backlight(True) - turns light on
         Backlight(False) - turns light off
        '''
        with open(BACKLIGHT_PATH + "/value", "w") as bfile:
            bfile.write("%d" % int(bool(light)))

