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

# Buttons check period (in seconds)
BUTTON_POLL=0.2
# STATUS request period (in # of BUTTON_POLL periods)
STATUS_POLL=5
# Info page cycle rate (in # of STATUS_POLL periods=
PAGE_CYCLE=2

prev_button = None

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

# Control of LCD
def write_line(row, text):
   lcd.set_cursor(0,row)
   lcd.message(text.ljust(16))

def page0(res):
       write_line(0, str(state[u'stateString']))
       if file_name is None:
           lcd.set_color(1.0,1.0,0);
           m = ' '
       else:
           lcd.set_color(0.0,1.0,0.0);
           m = str(file_name)
       write_line(1, m)

def page1(res):
       m = str(res[u'progress'][u'printTime'])
       write_line(0, m)
       m = "      " + str(res[u'progress'][u'printTimeLeft'])
       write_line(1, "  left: " + m)

def page2(res):
       m = str(res[u'temperatures'][u'extruder'][u'current'])
       write_line(0,"C extruder: " + m)
       m = "      " + str(res[u'temperatures'][u'bed'][u'current'])
       write_line(1,"       bed: " + m)

# A button is returned if
#   There is one and only one button pressed
#   It is pressed and it was not pressed on previous check
def check_buttons():
   global prev_button
   new_button = None
   press_count = 0
   for b in [LCD.SELECT, LCD.RIGHT, LCD.DOWN, LCD.UP, LCD.LEFT]:
      if lcd.is_pressed(b):
         press_count = press_count + 1
         new_button = b
   if press_count == 1 and prev_button != new_button:
      prev_button = new_button
      return new_button
   else: 
      prev_button = new_button  
      return None


connected = False
step = 0

status_poll_count = 0
page_cycle_count = 0
while True:
   status_poll_count = status_poll_count + 1

   # Fast cycle (if nothing else to do)
   button = check_buttons()
   if not button is None:
      print "B 1 " + str(button)
   if status_poll_count < STATUS_POLL:
      continue

   status_poll_count = 0

   res = load_info()

   button = check_buttons()
   if not button is None:
      print "B 2 " + str(button)

   page_cycle_count = page_cycle_count + 1

   if not connected:
      lcd.clear()
      lcd.set_color(0.0,1.0,0.0);
      connected = True
   job = res[u'job']
   state = res[u'state']
   file_name = job[u'filename']
   if page == 0:
      page0(res)
   elif page == 1:
      page1(res)
   elif page == 2:
      page2(res)

   if page_cycle_count > PAGE_CYCLE:
      page_cycle_count = 0
      page = page + 1 
      if page > 2:
         page = 0

   time.sleep(BUTTON_POLL)
