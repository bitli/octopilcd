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

# read apikey
with open('apikey') as apikeyfile:
   apikey = apikeyfile.read().replace('\n','').replace('\r','')

# Initialize the LCD using the pins
lcd = LCD.Adafruit_CharLCDPlate()

lcd.set_color(0.0, 0.0, 1.0)
lcd.clear()
lcd.message('Octopi...')
time.sleep(1.0)

connected = False
step = 0
while True:
   #headers = { 'X-Api-Key' : '165872B421084BB8B17C9FD24C6A3928' }
   #req = urllib2.Request("http://192.168.2.45:5000/api/state", None, headers)
   req = urllib2.Request("http://192.168.2.45:5000/api/state?apikey=" +apikey )
   res = json.load( urllib2.urlopen(req))
   #print "RES"
   print json.dumps(res, sort_keys=False,indent=4, separators=(',', ': '))
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
   elif step == 1:
       lcd.set_cursor(0,0)
       m = str(res[u'progress'][u'printTime'])
       lcd.message(("T done: " + m).ljust(16))
       lcd.set_cursor(0,1)
       m = "      " + str(res[u'progress'][u'printTimeLeft'])
       lcd.message(("  left: " + m).ljust(16))
   elif step == 2:
       lcd.set_cursor(0,0)
       m = str(res[u'temperatures'][u'extruder'][u'current'])
       lcd.message(("C extruder: " + m).ljust(16))
       lcd.set_cursor(0,1)
       m = "      " + str(res[u'temperatures'][u'bed'][u'current'])
       lcd.message(("       bed: " + m).ljust(16))

   if lcd.is_pressed(LCD.SELECT):
       print "SELECT"

   time.sleep(2.0)
   step = step + 1
   if step > 2:
      step = 0
