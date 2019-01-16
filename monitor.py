#! /bin/python
"""
Script to run the monitoring script and insert the data into the gsheet.

Things that occur:
- update temperature display every 30 seconds w/ instantaneous values
- every 15 minutes update temperature, flow, voc to gsheet
"""
try:
    from common import *
    import board
    import time
    import numpy as np
    import sys
    import datetime
except:
    print('Imports Failed!')

try:
    configFile = sys.argv[1]

    debug = False
    if len(sys.argv) == 3:
        debug = sys.argv[2]

    # load the configuration file:
    config = configuration(configFile)
except:
    print('Configuration Failed!')

try:
    # Wiring parameters, do not change without rewiring!
    upperPin = board.D5
    lowerPin = board.D6

    disp,draw,font,width,height,image = initialize_display(config.fontsize)

    # take a reading and turn the display on 
    upperT = read_temperature(upperPin)
    lowerT = read_temperature(lowerPin)
    print_message(["U: %s"%(round(upperT,1)),"L: %s"%(round(lowerT,1))],disp,draw,font,width,height,image)

    # create a new spreadsheet based on the date...
    gc = initializeGspread(config.googleAPI_key)
    key,url = makeSheet(gc,time.localtime(),config)

    for webhook in config.notifyWebhooks:
        send2slack('A Distillation has begun. Data can be found at: %s'%(url), webhook)

    lastAlert = datetime.datetime.fromtimestamp(time.mktime(time.localtime())) # initialize the last alert time

    if debug: print('Initialization Complete')
except:
    print('Initialization Failed!')

while True: # run the monitoring function
    try:
        localtime = time.localtime()
        seconds = time.strftime('%S', localtime) # compute seconds integer
        minutes = time.strftime('%M', localtime) # compute minutes integer
        now = datetime.datetime.fromtimestamp(time.mktime(localtime)) # convert to datetime
        #if debug: print('%s:%s'%(minutes,seconds))

        if any(int(seconds) == x for x in config.display_update): # run the loop on 30 second intervals
            
            if debug: print('Updating Display.')
            # read the upper and lower temperatures and display
            upperT = read_temperature(upperPin)
            lowerT = read_temperature(lowerPin)

            print_message(["U: %s"%(round(upperT,1)),"L: %s"%(round(lowerT,1))],disp,draw,font,width,height,image)
            
            if any(int(minutes) == x for x in config.data_log_interval): # print values to the spreadsheet 
                if debug: print('Logging Data.')

                fmtTime = time.strftime(config.time_fmt,localtime)
                temp,voc,eco2 = read_atm() 
                flow = read_flow()

                data = [fmtTime, round(upperT,2), round(lowerT,2), round(flow,2), round(voc,2), round(eco2,2)] # data for google sheets
                
                sheet = initializeGsheet(gc,key)
                sheet.append_row(data, value_input_option="USER_ENTERED")

                del sheet

                # run the warning system here!
                warning_system(data, lastAlert, config)
        
        time.sleep(0.4) # pause for 1 second
    except:
        pass
    