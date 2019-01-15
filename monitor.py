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
import sys
import datetime

configFile = sys.argv[1]

# load the configuration file:
config = configuration(configFile)

# Wiring parameters, do not change without rewiring!
upperPin = board.D5
lowerPin = board.D6

disp,draw,font,width,height,image = initialize_display(config.fontsize)

# create a new spreadsheet based on the date...
gc = initializeGspread(config.googleAPI_key)
key,url = makeSheet(gc,time.localtime(),config)

for webhook in config.notifyWebhooks:
    send2slack('A Distillation has begun. Data can be found at: %s'%(url), webhook)

lastAlert = datetime.datetime.fromtimestamp(time.mktime(time.localtime())) # initialize the last alert time

while True: # run the monitoring function

    localtime = time.localtime()
    seconds = time.strftime('%S', localtime) # compute seconds integer
    minutes = time.strftime('%M', localtime) # compute minutes integer
    now = datetime.datetime.fromtimestamp(time.mktime(localtime)) # convert to datetime

    if any(seconds == x for x in config.display_update): # run the loop on 30 second intervals
        
        # read the upper and lower temperatures and display
        upperT = read_temperature(upperPin)
        lowerT = read_temperature(lowerPin)

        print_message(["U: %s"%(round(upperT,1)),"L: %s"%(round(lowerT,1))],disp,draw,font,width,height,image)
        
        if any(minutes == x for x in config.data_log_interval): # print values to the spreadsheet 

            fmtTime = time.strftime(config.time_fmt,localtime)
            temp,voc,eco2 = read_atm() 
            flow = read_flow()

            data = [fmtTime, upperT, lowerT, flow, voc, eco2] # data for google sheets
            
            sheet = initializeGsheet(gc,key)
            sheet.append_rows(data, value_input_option="USER_ENTERED")

            del sheet

            # run the warning system here!
            warning_system(data, lastAlert, config)
    
    time.sleep(1) # pause for 1 second
    