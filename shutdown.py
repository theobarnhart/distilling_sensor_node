#! /usr/bin/python3
# This script will wait for a button to be pressed and then shutdown
# the Raspberry Pi.
# The button is to be connected on header 5 between pins 6 and 8.

# http://kampis-elektroecke.de/?page_id=3740
# http://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio
# https://pypi.python.org/pypi/RPi.GPIO

import RPi.GPIO as GPIO
import os
import sys
from common import *

pin = 23

configfile = sys.argv[1] # load the configuration file

config = configuration(configfile)

# we will use the pin numbering of the SoC, so our pin numbers in the code are 
# the same as the pin numbers on the gpio headers
GPIO.setmode(GPIO.BCM)  

# Pin 31 (Header 5) will be input and will have his pull up resistor activated
# so we only need to connect a button to ground
GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)  

# ISR: if our button is pressed, we will have a falling edge on pin 31
# this will trigger this interrupt:

def Int_shutdown(config): 
	try:
		for webhook in config.notifyWebhooks:
		 	send2slack('%s has been shutdown. Remove power in 1 minute.'%(config.node_name), webhook)
	except:
		pass
    # shutdown Raspberry Pi
	os.system("sudo shutdown -h now")

# Now we are programming pin 31 as an interrupt input
# it will react on a falling edge and call our interrupt routine "Int_shutdown"
try:
    GPIO.wait_for_edge(pin, GPIO.FALLING)
    Int_shutdown(config)
except KeyboardInterrupt:
    GPIO.cleanup()
GPI.cleanup()
