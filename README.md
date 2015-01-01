PiMony
======

Prototype Smart Remote using Python on a Pi

This is a very experimental codebase for trying out smart remote control ideas, using a Raspberry Pi
with an Adafruit PiTFT touch screen, an IR sender circuit connected to a GPIO pin and a custom keypad
matrix attached via an MCP23017 GPIO extender.

It depends upon having lirc, i2c and PiTFT support installed; and uses the Python packages smbus, RPIO
and pygame.
