#!/usr/bin/env python3
import sys
import time
import requests
import json
import datetime
import configparser
from decimal import Decimal
from os.path import exists
import os
import subprocess
import apprise

CMD = '''
on run argv
  display notification (item 2 of argv) with title (item 1 of argv)
end run
'''

apobj = apprise.Apprise()

def notify(title, text):
  subprocess.call(['osascript', '-e', CMD, title, text])


config = configparser.RawConfigParser()
config.read('config.properties')

# Must install shapely
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

sys.tracebacklimit = 0
notifiers = {}
notifiers = config.get('Push','push.notifiers')
longitude = config.get('Location','workplace.longitude')
latitude = config.get('Location','workplace.latitude')
if (longitude == '' or latitude == ''):
   print("No Workplace defined, workplace check will be ignored and checkup may be inaccurate")
else:
   work_location = Point(Decimal(longitude), Decimal(latitude))

def show_toast(rest, title, newstate):
    global rests
    wsl_notification_path = config.get('General','wsl.notification.path')
    if rests[rest] != newstate:
       rests[rest] = newstate
       if exists("/usr/bin/osascript"):
           notify("Wolt checker", title + " is " + rests[rest])
       if exists(wsl_notification_path + 'wsl-notify-send.exe'):
           subprocess.call([wsl_notification_path + 'wsl-notify-send.exe','--appId',"Wolt Checker",'-c',"Restaurant status Changed",title + ' is now ' + newstate])
       if push=="true":
           send_push(RESTNAME + " is " + newstate)    

def create_apobj(apobj, notifiers):
    if len(notifiers)!=0:
        for notifier in notifiers.split():
            apobj.add(notifier)
    return apobj      
          
def is_open_now(opening_times):
    today = datetime.datetime.now().strftime("%A").lower()
    if opening_times[today]==[]:
       return False
    now = datetime.datetime.now()
    current=(((now.hour*60)+now.minute)*60000)
    for a in opening_times[today]:
        if a["value"]["$date"] > current:
           if a["type"] == "open":
              return False
           else:
              return True
        elif (len(opening_times[today])==1 or opening_times[today].index(a) == len(opening_times[today])-1):
           if a["type"] == "open":
              return True
           else:
              return False

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

create_apobj(apobj, notifiers)

def send_push(text):
    apobj.notify(
            body=text,
            title='Restaurant state has changed',
            )

def location_available(pointarray, point):
    polygon = Polygon(pointarray)
    return(polygon.contains(point))

def get_english_name(arr,origname):
    for a in arr:
        if a["lang"] == 'en':
           return a["value"]
    return origname

arglist=sys.argv
if len(arglist) < 2:
    print("usage: wolt [-p] restaurant-name [restaurant-name] ...")
    sys.exit(1)

arglist.pop(0)
push="false"
if arglist[0] == '-p':
    print("PUSH Mode")
    push="true"
    arglist.pop(0)

if len(arglist) == 0:
    print("No restaurant[s] supplied")
    sys.exit(1)

rests={}
for rest in arglist:
    print("Adding resturant "+rest+" for monitoring")
    rests[rest]="Closed"

print()

while(True):
    for rest in rests:
        JSON=json.loads(requests.get("https://restaurant-api.wolt.com/v3/venues/slug/"+rest).text)
        RESTONLINE=JSON["results"][0]["online"]
        RESTALIVE=JSON["results"][0]["alive"]
        RESTDELV=JSON["results"][0]["delivery_specs"]["delivery_enabled"]
        if 'work_location' in locals(): 
             RESTTOLOCATION=location_available(JSON["results"][0]["delivery_specs"]["geo_range"]["coordinates"][0],work_location)
        RESTNAME=get_english_name(JSON["results"][0]["name"],rest)
        RESTOPENHOURS=is_open_now(JSON["results"][0]["opening_times"])
        if ((RESTONLINE == True) and (RESTALIVE == 1) and (RESTDELV == True) and ('RESTTOLOCATION' in locals() and RESTTOLOCATION == True) and (RESTOPENHOURS == True)):
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + RESTNAME+" is " + bcolors.OKGREEN + "Open" + bcolors.ENDC)
            show_toast(rest, RESTNAME, 'Open')
        else:
            show_toast(rest, RESTNAME, 'Closed')
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + RESTNAME+" is " + bcolors.FAIL + "Closed " + bcolors.ENDC, end='')
            if RESTOPENHOURS == False:
                print("(Outside of open hours)")
            elif RESTONLINE == False:
                print("(Offline)")
            elif RESTALIVE != 1:
                print("(Not Alive)")
            elif RESTDELV == False:
                print("(No Delivery)")
            elif ('RESTTOLOCATION' in locals() and RESTTOLOCATION == False):
                print("(Not delivering to our location)")
            else:
                print('(Unknown reason, most likely coordinates)')
    time.sleep(10)
