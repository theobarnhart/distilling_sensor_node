from common import *
import board
import time
import numpy as np

# parameters
upperPin = board.D5
lowerPin = board.D6
#lowerPin = board.D6?
db = '/home/pi/distDat.db'
upperTemp = 'upperTemp'
lowerTemp = 'lowerTemp'
fontsize=18

disp,draw,font,width,height,image = initialize_display(fontsize)
ct = 0
upper = []
lower = []
while True:
    upper.append(read_temperature(upperPin))
    lower.append(read_temperature(lowerPin))
    
    if ct == 29:
        upperReading = np.mean(upper)
        lowerReading = np.mean(lower)
        
        insert_db(db, upperTemp, upperReading) # read upper temperature
        insert_db(db, lowerTemp, lowerReading) # read the lower temperature
    
        print_message(["U: %s"%(round(upperReading,1)),"L: %s"%(round(lowerReading,1))],disp,draw,font,width,height,image)
        
        # reset the counter
        upper = []
        lower = []
        ct = 0
    
    else:
        ct += 1
    
    time.sleep(1)
    