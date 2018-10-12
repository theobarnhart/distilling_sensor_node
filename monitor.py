from common import *
import board

# parameters
upperPin = board.D5
#lowerPin = board.D6?
db = '/home/pi/distDat.db'
upperTemp = 'upperTemp'
lowerTemp = 'lowerTemp'

insert_db(db, upperTemp, read_temperature(upperPin)) # read upper temperature
#insert_db(db, lowerTemp, read_temperature(lowerPin)) # read the lower temperature