# common functions to use

import board
import busio
import digitalio
import adafruit_max31865
import sqlite3

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