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
ct2 = 0
upper = []
lower = []

upper2 = []
lower2 = []
while True:
    upperT = read_temperature(upperPin)
    lowerT = read_temperature(lowerPin)
    
    upper.append(upperT)
    lower.append(lowerT)
    
    upper2.append(upperT)
    lower2.append(lowerT)
    
    if ct == 899:
        upperReading = np.mean(upper)
        lowerReading = np.mean(lower)
        
        insert_db(db, upperTemp, upperReading) # read upper temperature
        insert_db(db, lowerTemp, lowerReading) # read the lower temperature
        
        # reset the counter
        upper = []
        lower = []
        ct = 0
    
    elif ct2 == 9:
        upperReading = np.mean(upper2)
        lowerReading = np.mean(lower2)
        print_message(["U: %s"%(round(upperReading,1)),"L: %s"%(round(lowerReading,1))],disp,draw,font,width,height,image)
        
        ct2 = 0
        upper2 = []
        lower2 = []
        
    else:
        
        ct += 1
    
    time.sleep(1)
    