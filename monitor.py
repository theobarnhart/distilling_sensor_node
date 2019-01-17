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
    import logging

    time.sleep(45)
except:
    print('Imports Failed!')
    raise

try:
    configFile = sys.argv[1]

    # load the configuration file:
    config = configuration(configFile)
    debug = config.debug
except:
    print('Configuration Failed!')
    raise

if not config.runProgram:
    print('Exiting Program.')
    sys.exit()

try: # setup logging:
    if not os.path.exists(config.logPath): # if the path does not exist, make the folder
        os.makedirs(config.logPath)

    logFile = os.path.join(config.logPath,'%s_%s.log'%(config.logName,time.strftime(config.datasheet_appendix,time.localtime())))
    
    if config.debug:
        logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',filename=logFile,level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',filename=logFile,level=logging.INFO)
    logging.info('Logging initiated.')
except:
    print('Logging failed.')
    raise

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
    logging.info('Datalogging initialization failed.')
    raise

lastReading = 70

while True: # run the monitoring function
    try:
        localtime = time.localtime()
        seconds = time.strftime('%S', localtime) # compute seconds integer
        minutes = time.strftime('%M', localtime) # compute minutes integer
        now = datetime.datetime.fromtimestamp(time.mktime(localtime)) # convert to datetime
        #if debug: print('%s:%s'%(minutes,seconds))
    except:
        logging.debug('Time acquisition failed.')
        raise

    try:
        if any(int(seconds) == x for x in config.display_update): # Display update loop
            try:
                if debug: logging.info('Updating display.')
                # read the upper and lower temperatures and display
                upperT = read_temperature(upperPin)
                lowerT = read_temperature(lowerPin)

                print_message(["U: %s"%(round(upperT,1)),"L: %s"%(round(lowerT,1))],disp,draw,font,width,height,image)

                if any(int(minutes) == x for x in config.data_log_interval): # datalogger loop.

                    if lastReading != minutes:
                        try:
                            if debug: logging.info('Logging Data.')

                            fmtTime = time.strftime(config.time_fmt,localtime)
                            temp,voc,eco2 = read_atm() 
                            flow = read_flow()

                            data = [fmtTime, round(upperT,2), round(lowerT,2), round(flow,2), round(voc,2), round(eco2,2)] # data for google sheets
                        except: 
                            logging.debug('Additional data acquisition failed.')
                            raise 
                        try:
                            sheet = initializeGsheet(gc,key)
                            sheet.append_row(data, value_input_option="USER_ENTERED")

                            del sheet
                        except:
                            logging.debug('Datalogging failure.')

                        try:
                            # run the warning system here!
                            if config.sendAlerts:
                                warning_system(data, lastAlert, config)
                        except:
                            logging.debug('Warning system failure.')

                        try: # update configuration
                            config = configuration(configFile)
                            debug = config.debug
                        except:
                            logging.warning('Configuration update failure')
                        lastReading = minutes
                    else: 
                        pass
            except:
                logging.debug('Display loop failure.')
        
        time.sleep(0.4) # pause for 1 second
    except:
        logging.debug('Main loop failure.')
    