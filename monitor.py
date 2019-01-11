"""
Script to run the monitoring script and insert the data into the gsheet.

Things that occur:
- update temperature display every 30 seconds w/ instantaneous values
- every 15 minutes update temperature, flow, voc to gsheet
"""

from common import *
import board
import time
import numpy as np

# read the yaml file....

emails = None
googleAPI_key = None

limits = [upperLim,lowerLim,flowLim]

# parameters
upperPin = board.D5
lowerPin = board.D6

upperTemp = 'upperTemp'
lowerTemp = 'lowerTemp'
fontsize=18

disp,draw,font,width,height,image = initialize_display(fontsize)

# create a new spreadsheet based on the date...
gc = initializeGspread(googleAPI_key)
key,url = makeSheet(gc,time.localtime(),emails)

send2slack('A Distillation has begun. Data can be found at: %s'%(url), "Factory")

while True: # run the monitoring function

    localtime = time.localtime()
    seconds = time.strftime('%S', localtime)
    minutes = time.strftime('%M', localtime)

    if seconds == 30 | seconds == 0: # run the loop on 30 second intervals
        
        # read the upper and lower temperatures and display
        upperT = read_temperature(upperPin)
        lowerT = read_temperature(lowerPin)

        print_message(["U: %s"%(round(upperT,1)),"L: %s"%(round(lowerT,1))],disp,draw,font,width,height,image)
        
        if minutes == 0 | minutes == 15 | minutes == 30 | minutes == 45: # print values to the spreadsheet 

            datetime = time.strftime('%y-%m-%d %H:%M:%S')
            temp,voc,eco2 = read_atm() 
            flow = read_flow()

            data = [datetime, upperT, lowerT, flow, voc]

            sheet = initializeGsheet(gc,key)

            sheet.append_rows(data, value_input_option="USER_ENTERED")

            del sheet

            # run the warning system here!
            warning_system(data, limits)
    
    time.sleep(1) # pause for 1 second
    