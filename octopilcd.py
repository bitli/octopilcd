#  octopilcd
# 
# An utility to display status of OctoPrint on PI LCD
#
# License; See file LICENSE
#

import time

import Adafruit_CharLCD as LCD
import json
import urllib2

VERSION = "0.1-a"

# TODO Make configurable
HOST="192.168.2.45"
PORT=5000

LCD_COLS=16
LCD_ROWS=2

DEBUG=False

# Connection parameters
def load_info():
   
   #headers = { 'X-Api-Key' : '165872B421084BB8B17C9FD24C6A3928' }
   #req = urllib2.Request("http://"+HOST+":"+PORT+"/api/state", None, headers)
   req = urllib2.Request('http://' + HOST + ':' + str(PORT) + '/api/state?apikey=' +apikey )
   res = json.load( urllib2.urlopen(req))
   if DEBUG:
      print json.dumps(res, sort_keys=False,indent=4, separators=(',', ': '))
   return res

# read apikey
# TODO Handle errors
with open('apikey') as apikeyfile:
   apikey = apikeyfile.read().replace('\n','').replace('\r','')

# Initialize the LCD using the pins
# TODO Clear error message if library not present
lcd = LCD.Adafruit_CharLCDPlate()

lcd.set_color(0.0, 0.0, 1.0)
lcd.clear()
lcd.message('Octopi LCD ' + VERSION + '\nloading ...')
time.sleep(1.0)

# If menu is NONE, then cycle trhough information pages
# Otherwise the menu object controls what is displayed and actions
menu = None
page = 0

def page0(res):
       lcd.set_cursor(0,0)
       lcd.message(str(state[u'stateString']).ljust(16))
       if file_name is None:
           lcd.set_color(1.0,1.0,0);
           m = ' '
       else:
           lcd.set_color(0.0,1.0,0.0);
           m = str(file_name)
       lcd.set_cursor(0,1)
       lcd.message(m.ljust(16))

def page1(res):
       lcd.set_cursor(0,0)
       m = str(res[u'progress'][u'printTime'])
       lcd.message(("T done: " + m).ljust(16))
       lcd.set_cursor(0,1)
       m = "      " + str(res[u'progress'][u'printTimeLeft'])
       lcd.message(("  left: " + m).ljust(16))

def page2(res):
       lcd.set_cursor(0,0)
       m = str(res[u'temperatures'][u'extruder'][u'current'])
       lcd.message(("C extruder: " + m).ljust(16))
       lcd.set_cursor(0,1)
       m = "      " + str(res[u'temperatures'][u'bed'][u'current'])
       lcd.message(("       bed: " + m).ljust(16))


connected = False
step = 0
while True:
   res = load_info()
   if not connected:
      lcd.clear()
      lcd.set_color(0.0,1.0,0.0);
      connected = True
   job = res[u'job']
   #print "JOB KEYS"
   # print job.keys()
   # print "JOB"
   #print json.dumps(job, sort_keys=False,indent=4, separators=(',', ': '))
   state = res[u'state']
   file_name = job[u'filename']
   if step == 0:
      page0(res)
   elif step == 1:
      page1(res)
   elif step == 2:
      page2(res)

   if lcd.is_pressed(LCD.SELECT):
       print "SELECT"

   time.sleep(2.0)
   step = step + 1
   if step > 2:
      step = 0
