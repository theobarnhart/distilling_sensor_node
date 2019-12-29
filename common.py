#! /usr/bin/python3
# common functions to use

import board
import busio
import digitalio
import adafruit_max31865
import adafruit_ccs811
import Adafruit_SSD1306
import RPi.GPIO as GPIO
import time
import os
import json
import requests
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import yaml
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
	try:
		spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
		cs = digitalio.DigitalInOut(pin)
		sensor = adafruit_max31865.MAX31865(spi, cs, wires=wires)
		return sensor.temperature
	except:
		return -9999
	
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
	
def initialize_display(fontSize):
	try:
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
		width = 128
		height = 32
		image = Image.new('1', (width, height))
		
		draw = ImageDraw.Draw(image) # Get drawing object to draw on image.
		
		# Draw a black filled box to clear the image.
		draw.rectangle((0,0,width,height), outline=0, fill=0)
		
		font = ImageFont.truetype(font='/home/pi/fonts/gameovercre1.ttf',size=fontSize)
		
		return disp,draw,font,width,height,image
	except:
		raise

def print_message(message,disp,draw,font,width,height,image):
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
	try:
		draw.rectangle((0,0,width,height), outline=0, fill=0)
		x = 0
		top = 0
		# Write two lines of text.
		for l in message:
			draw.text((0, top),l,  font=font, fill=255)
			top += font.size

		# Display image.
		disp.image(image)
		disp.display()
	except:
		raise
	
def read_flow(seconds=30,pin=22, disp=False):
	'''
	Inputs:
		seconds - duration of time to monitor flow, defaults to 30.
		pin - GPIO pin to read (int).
		disp - display results (bool).

	Returns:
		time - the center of the interval over which the measurement was made
		rate - revolutions per second

	'''
	# initialize the
	try:
		boardRevision = GPIO.RPI_REVISION
		GPIO.setmode(GPIO.BCM) # use real GPIO numbering
		GPIO.setup(pin,GPIO.IN, pull_up_down=GPIO.PUD_UP)

		lastPinState = False
		pinState = 0
		lastPinChange = int(time.time() * 1000) # read time and convert to integer
		pinChange = lastPinChange
		pinDelta = 0
		hertz = 0
		flow = 0
		litersPoured = 0
		deltaSeconds = 0
		revs = 0

		lastTime = time.time()
		startTime = lastTime # save start time
		if disp: print("Starting Count")
		while deltaSeconds <= seconds: # while the elapsed time less than the measurement period
			currentTime = int(time.time() * 1000) # read the time, convert to an integer
			
			# read the pin state
			if GPIO.input(pin):
				pinState = True
			else:
				pinState = False

			if(pinState != lastPinState and pinState == True): # if the pin is different than before and is high
				# get the current time
				pinChange = currentTime
				pinDelta = pinChange - lastPinChange # compute the change in time since the last revolution 
				hertz = 1000.0000 / pinDelta # cycles / second
				flow = hertz / (60 * 7.5) # L/s, compute rate
				litersPoured += flow * (pinDelta / 1000.0000) # rate * (pinDelta /1000), conver delta back to seconds

				lastPinChange = pinChange # save the last pin change time

			lastPinState = pinState # save the current pin state
			now = time.time()
			deltaSeconds = now - startTime
			
			if disp: print('%s seconds: %s liters'%(round(deltaSeconds,3),round(litersPoured,2)))
			
		if disp: print(round(litersPoured,2))
		# return litersPoured
		return flow # in L/s
	except:
		return -9999

def read_atm():
	try:
		i2c = busio.I2C(board.SCL, board.SDA)
		ccs811 = adafruit_ccs811.CCS811(i2c)
		
		while not ccs811.data_ready: pass # Wait for the sensor to be ready and calibrate the thermistor

		temp = ccs811.temperature # deg C
		voc = ccs811.tvoc # PPM
		eco2 = ccs811.eco2 # PPM

		return temp,voc,eco2
	except:
		-9999,-9999,-9999

def send2slack(message, webhook):
	'''
	Sends a message to slack 
	
	Inputs:
		message - message to post to channel (string)
		webhook - webhook to post to (string)

	Returns:
		None
	'''
	slack_data = {'text':message}

	response = requests.post(webhook, data = json.dumps(slack_data),
				headers = {'Content-Type':'application/json'})

	if response.status_code != 200:
		raise ValueError(
			'Request to slack returned an error %s, the response is:\n%s'
			% (response.status_code, response.text))

def initializeGsheet(gc, key):
	"""
	Initialize the Google Sheet.

	Inputs:
		googleAPI_key [path] - path to the google API JSON file
		sheetCode [string] - code to identify the sheet you want to access

	Outputs:
		Sheet [object] - google sheet that has been accessed
	"""

	Sheet = gc.open_by_key(key).sheet1

	return Sheet

def initializeGspread(googleAPI_key):
	scope = ['https://spreadsheets.google.com/feeds',
	'https://www.googleapis.com/auth/drive']

	credentials = ServiceAccountCredentials.from_json_keyfile_name(googleAPI_key, scope)

	gc = gspread.authorize(credentials)

	return gc

def makeSheet(gc,maketime,config):
	"""
	make a spreadsheet based on the time 
	"""
	sh = gc.create('%s_%s'%(config.datasheet_prefix,time.strftime(config.datasheet_appendix,maketime))) # create new spreadsheet
	key = sh.fetch_sheet_metadata()['spreadsheetId']
	url = sh.fetch_sheet_metadata()['spreadsheetUrl']

	for email in config.shareEmails:
		sh.share(email, perm_type='user', role='writer')

	wks = sh.sheet1

	wks.append_row(config.datasheetCols) # make the table header

	return key,url

def warning_system(data, lastTime, config):
	"""
	Warn Steffen and Terrel if the flow stops or the temperature is too hot.
	
	Inputs:
		data
		limits
		lastTime [datetime] - when the last alert was issued
		config [configuration object] - holds all the lists etc...

	Outputs:
		Slack messages or nothing if all is well.

	"""

	fmtTime,upperT,lowerT,flow,voc,eco2 = data # unpack data

	# convert datetime string to datetime object

	t = datetime.datetime.strptime(fmtTime, config.time_fmt)

	td = t - lastTime
	minutes = td.seconds/60.
	if minutes < config.alert_limit:
		return lastTime # if not enough time has elapsed, return the last time.
	else:
		if lowerT > config.lowerT_limit or upperT > config.upperT_limit:
			message = 'Temperature Alert!\n\nUpper T: %s %s\nLower T: %s %s'%(upperT,config.Tunits,lowerT,config.Tunits)

			for webhook in config.alertWebhooks:
				send2slack(message,webhook)

		if flow < config.flow_limit and flow != -9999:
			message = 'Coolant Flow Alert!\n\nFlow: %s %s'%(flow,config.flowUnits)

			for webhook in config.alertWebhooks:
				send2slack(message,webhook)
	

class configuration:
	"""
	Generate a configuration class to parameterize the program.

	Inputs:
		configFile [path] - path to the configuration yaml file.

	Outputs:
		config [object] 
	"""
	def __init__(self, configFile):
		import yaml

		with open(configFile, 'r') as stream:
			try:
				params = yaml.load(stream)
			except yaml.YAMLError as exc:
				print(exc)

		self.people = params['Notifications']['Names']['People'] # pull the names of people
		self.channels = params['Notifications']['Names']['Channels'] # pull the names of the slack channels

		self.peopleData = params['Notifications']['People']
		self.channelData = params['Notifications']['Channels']

		assert len(self.peopleData) == len(self.people), 'People listed and supplied data are different lengths.'
		assert len(self.channelData) == len(self.channels), 'Channels listed and supplied data are different lengths.'

		self.parameters = params['Parameters']

		self.display_update = self.parameters['display_update']
		self.data_log_interval = self.parameters['data_log_interval']
		self.datasheet_prefix = self.parameters['datasheet_prefix']
		self.datasheet_appendix = self.parameters['datasheet_appendix']
		self.Tunits = self.parameters['Tunits']
		self.flowUnits = self.parameters['flowUnits']

		try: self.upperT_limit = float(self.parameters['upperT_limit'])
		except: self.upperT_limit = self.parameters['upperT_limit']

		try: self.lowerT_limit = float(self.parameters['lowerT_limit'])
		except: self.lowerT_limit = self.parameters['lowerT_limit']

		try: self.flow_limit = float(self.parameters['flow_limit'])
		except: self.flow_limit = self.parameters['flow_limit']

		try: self.alert_limit = float(self.parameters['alert_limit'])
		except: self.alert_limit = self.parameters['alert_limit']

		self.shareData = self.parameters['shareData']
		self.fontsize = self.parameters['fontsize']
		self.googleAPI_key = self.parameters['googleAPI_key']
		self.alertPeople = self.parameters['alertPeople']
		self.statusUpdate = self.parameters['statusUpdate']
		self.datasheetCols = self.parameters['datasheetCols']
		self.time_fmt = self.parameters['time_fmt']
		self.node_name = self.parameters['node_name']
		self.logPath = self.parameters['logPath']
		self.logName = self.parameters['logName']
		self.runProgram = self.parameters['runProgram']
		self.debug = self.parameters['debug']
		self.sendAlerts = self.parameters['sendAlerts']
		self.delay = self.parameters['delay']

		# generate a list of emails to share spreadsheed with
		emails = []
		for name in self.shareData:
			try:
				emails.append(self.peopleData[name]['email'])
			except:
				pass
		self.shareEmails = emails

		# generate a list of webhooks to alert people
		alertWebhooks = []

		for name in self.alertPeople:
			try:
				alertWebhooks.append(self.peopleData[name]['Key']) # look in the people data
			except:
				pass
			try:
				alertWebhooks.append(self.channelData[name]['Key']) # look in the channel data
			except:
				pass
		self.alertWebhooks = alertWebhooks

		# generate a list of webhooks to notify people that a distillation is starting
		notifyWebhooks = []

		for name in self.statusUpdate:
			try:
				notifyWebhooks.append(self.peopleData[name]['Key'])
			except:
				pass
			try:
				notifyWebhooks.append(self.channelData[name]['Key'])
			except:
				pass

		self.notifyWebhooks = notifyWebhooks

		self.rawParams = params
