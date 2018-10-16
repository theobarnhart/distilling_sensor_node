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
    
def initialize_display():
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
    width = 64
    height = 16
    image = Image.new('1', (width, height))
    
    draw = ImageDraw.Draw(image) # Get drawing object to draw on image.
    
    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    
    font = ImageFont.load_default()
    
    return disp,draw,font,width,height

def print_message(message,disp,draw,font,width,height):
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

    # Write two lines of text.
    for l in message:
        draw.text((0, top),l,  font=font, fill=255)
        top += 8

    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(.1)
    