from common import *
import board
import time

# parameters
upperPin = board.D5
lowerPin = board.D6
#lowerPin = board.D6?
db = '/home/pi/distDat.db'
upperTemp = 'upperTemp'
lowerTemp = 'lowerTemp'
fontsize=18

disp,draw,font,width,height,image = initialize_display(fontsize)

while True:
    lowerReading = read_temperature(lowerPin)
    upperReading = read_temperature(upperPin)
    
    insert_db(db, upperTemp, upperReading) # read upper temperature
    insert_db(db, lowerTemp, lowerReading) # read the lower temperature
    
    print_message(["U: %s"%(upperReading),"L: %s"%(lowerReading)],disp,draw,font,width,height,image)
    
    time.sleep(10)
    