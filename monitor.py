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
	import traceback

except Exception as e:
	print('Imports Failed!')
	print(e)
	print(traceback.format_exc())
	
try:
	configFile = sys.argv[1]

	# load the configuration file:
	config = configuration(configFile)
	debug = config.debug
except Exception as e:
	print('Configuration Failed!')
	print(e)
	print(traceback.format_exc())

time.sleep(config.delay) # delay to let the internet connect

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
except Exception as e:
	logging.info('Logging failed.')
	print('Logging failed.')
	print(e)
	print(traceback.format_exc())

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
	gcTime = time.localtime() # get the time the gc was created
	gc = initializeGspread(config.googleAPI_key)
	key,url = makeSheet(gc,time.localtime(),config)

	for webhook in config.notifyWebhooks:
		send2slack('A Distillation has begun. Data can be found at: %s'%(url), webhook)

	lastAlert = datetime.datetime.fromtimestamp(time.mktime(time.localtime())) # initialize the last alert time

	if debug: print('Initialization Complete')
except Exception as e:
	print('Datalogging initialization failed.')
	print(e)
	print(traceback.format_exc())

lastReading = 70

while True: # run the monitoring function
	try:
		localtime = time.localtime()
		seconds = time.strftime('%S', localtime) # compute seconds integer
		minutes = time.strftime('%M', localtime) # compute minutes integer
		now = datetime.datetime.fromtimestamp(time.mktime(localtime)) # convert to datetime
		#if debug: print('%s:%s'%(minutes,seconds))
	except Exception as e:
		print('Time acquisition failed.')
		print(e)
		print(traceback.format_exc())

	try:
		if any(int(seconds) == x for x in config.display_update): # Display update loop
			try:
				if debug: logging.info('Updating display.')
				# read the upper and lower temperatures and display
				upperT = read_temperature(upperPin)
				lowerT = read_temperature(lowerPin)

				#print("Upper Temperature: %f.2"%upperT)
				#print("Lower Temperature: %f.2"%lowerT)
				print_message(["U: %s"%(round(upperT,1)),"L: %s"%(round(lowerT,1))],disp,draw,font,width,height,image)

				if any(int(minutes) == x for x in config.data_log_interval): # datalogger loop.

					if lastReading != minutes:
						try:
							if debug: logging.info('Logging Data.')

							fmtTime = time.strftime(config.time_fmt,localtime)
							temp,voc,eco2 = read_atm()
							flow = read_flow()

							print('**********')
							print(fmtTime)
							print("Upper Temperature: %.2f"%upperT)
							print("Lower Temperature: %.2f"%lowerT)
							print('ATM temp.: %.2f'%(temp))
							print('ATM voc: %.2f'%(voc))
							print('ATM eco2: %.2f'%(eco2))
							print('Flow: %.2f'%(flow))
						except Exception as e:
							print('atm data failed.')
							print(e)

						try:
							data = [fmtTime, round(upperT,2), round(lowerT,2), round(flow,2), round(voc,2), round(eco2,2)] # data for google sheets
						except Exception as e:
							print('Data Construct Failed')
							print(e)
							print(traceback.format_exc())

						try:
							if (time.localtime() - gcTime)/60. > 55: # if its been about an hour, get new credentials 
								gcTime = time.localtime() # replace gcTime with current time
								gc.login() # update credentials
							sheet = initializeGsheet(gc,key)
							sheet.append_row(data, value_input_option="USER_ENTERED")
							del sheet
						except Exception as e:
							print('Datalogging failure.')
							print(e)
							print(traceback.format_exc())
						
						try:
							# run the warning system here!
							if config.sendAlerts:
								warning_system(data, lastAlert, config)
						except Exception as e:
							print('Warning system failure.')
							print(e)
							print(traceback.format_exc())
						
						try: # update configuration
							config = configuration(configFile)
							debug = config.debug
						except Exception as e:
							print('Configuration update failure')
							print(e)
							print(traceback.format_exc())
						
						lastReading = minutes
					else: 
						pass
			except Exception as e:
				print('Display loop failure.')
				print(e)
				print(traceback.format_exc())
			
		time.sleep(0.4) # pause for 1 second
	
	except Exception as e:
		print('Main loop failure.')
		print(e)
		print(traceback.format_exc())
	
	