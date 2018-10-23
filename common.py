# common functions to use

import board
import busio
import digitalio
import adafruit_max31865
import sqlite3
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import RPi.GPIO as GPIO
import time

def read_temperature(pin,wires=3):
    '''
    Inputs:
        pin - in the format board.D<pin> where <pin> is the pin you want to read the sensor on.
    
    Outputs:
        Sensor temperature in degrees C.
    '''
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    cs = digitalio.DigitalInOut(pin)
    sensor = adafruit_max31865.MAX31865(spi, cs, wires=wires)
    return sensor.temperature
    
def insert_db(db,table,value):
    '''
    Inputs:
        db - path to database
        table - table name
        value - value to be inserted
    
    Outputs:
        None
    '''
    conn = sqlite3.connect(db)
    curs = conn.cursor()
    
    curs.execute("INSERT INTO %s values(datetime('now'), (?))"%(table), (value,)) # insert the value
    conn.commit() # save the changes
    conn.close() # close the database
    
    return None
    
def initialize_display(fontSize):
    RST = None
    # 128x32 display with hardware I2C:
    disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
    
    disp.begin() # initialize display
 
    # Clear display.
    disp.clear()
    disp.display()
    
    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    #width = disp.width
    #height = disp.height
    width = 128
    height = 32
    image = Image.new('1', (width, height))
    
    draw = ImageDraw.Draw(image) # Get drawing object to draw on image.
    
    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    
    font = ImageFont.truetype(font='/home/pi/fonts/gameovercre1.ttf',size=fontSize)
    
    return disp,draw,font,width,height,image

def print_message(message,disp,draw,font,width,height,image):
    '''
    Inputs:
        message - list of lines to print.
        disp - 
        draw - 
        font - 
        width - 
        height - 
    
    Outputs:
        Prints Message to connected display
    '''
 
    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    x = 0
    top = 0
    # Write two lines of text.
    for l in message:
        draw.text((0, top),l,  font=font, fill=255)
        top += font.size

    # Display image.
    disp.image(image)
    disp.display()
    
def read_flow(seconds=30,pin=22, disp=False):
	'''
	Inputs:
		seconds - duration of time to monitor flow, defaults to 30.
		pin - GPIO pin to read (int).
		disp - display results (bool).

	Returns:
		time - the center of the interval over which the measurement was made
		rate - revolutions per second

	'''
	# initialize the 
	boardRevision = GPIO.RPI_REVISION
	GPIO.setmode(GPIO.BCM) # use real GPIO numbering
	GPIO.setup(pin,GPIO.IN, pull_up_down=GPIO.PUD_UP)

	lastPinState = False
	pinState = 0
	lastPinChange = int(time.time() * 1000) # read time and convert to integer
	pinChange = lastPinChange
	pinDelta = 0
	hertz = 0
	flow = 0
	litersPoured = 0
	deltaSeconds = 0
	revs = 0

	lastTime = time.time()
	startTime = lastTime # save start time
	if disp: print("Starting Count")
	while deltaSeconds <= seconds: # while the elapsed time less than the measurement period
		currentTime = int(time.time() * 1000) # read the time, convert to an integer
		
		# read the pin state
		if GPIO.input(pin):
			pinState = True
		else:
			pinState = False

		if(pinState != lastPinState and pinState == True): # if the pin is different than before and is high
			# get the current time
			pinChange = currentTime
			pinDelta = pinChange - lastPinChange # compute the change in time since the last revolution 
			hertz = 1000.0000 / pinDelta # cycles / second
			flow = hertz / (60 * 7.5) # L/s, compute rate
			litersPoured += flow * (pinDelta / 1000.0000) # rate * (pinDelta /1000), conver delta back to seconds

			lastPinChange = pinChange # save the last pin change time

		lastPinState = pinState # save the current pin state
		now = time.time()
		deltaSeconds = now - startTime
		
		if disp: print('%s seconds: %s liters'%(round(deltaSeconds,3),round(litersPoured,2)))


	if litersPoured == 0: # if there are no counts:
		return 0
	else: # calculate the instantaneous speed
		
		if disp: print(litersPoured)
		return litersPoured

#def send2slack():






