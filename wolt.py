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
import urllib.parse
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import termcolor
if os.name == 'nt':
        os.system('color')

CMD = '''
on run argv
  display notification (item 2 of argv) with title (item 1 of argv)
end run
'''

arglist=sys.argv
if len(arglist) < 2:
    print("usage: wolt [-p] restaurant-name [restaurant-name] ...")
    sys.exit(1)

apobj = apprise.Apprise()

def notify(title, text):
  subprocess.call(['osascript', '-e', CMD, title, text])

config = configparser.RawConfigParser()
config.read('config.properties')

def get_location_from_freetext(freetext):
    print("Attempting to get location from freetext: " + freetext)
    getlocid = json.loads(requests.get("https://restaurant-api.wolt.com/v1/google/places/autocomplete/json?input="+urllib.parse.quote(freetext)).text)
    place_id = getlocid["predictions"][0]["place_id"]
    place_geo = json.loads(requests.get("https://restaurant-api.wolt.com/v1/google/geocode/json?place_id="+place_id).text)
    # add check if not empty
    global latitude,longitude
    latitude = place_geo["results"][0]["geometry"]["location"]["lat"]
    longitude = place_geo["results"][0]["geometry"]["location"]["lng"]

sys.tracebacklimit = 0
notifiers = {}
notifiers = config.get('Push','push.notifiers')

freetext = config.get('Location','location.freetext')
if freetext == '':
    longitude = config.get('Location','workplace.longitude')
    latitude = config.get('Location','workplace.latitude')
    if (longitude == '' or latitude == ''):
       print("No Workplace defined, workplace check will be ignored and checkup may be inaccurate")
    else:
       work_location = Point(Decimal(longitude), Decimal(latitude))
       print("Location: latitude " + str(latitude) + ", longitude " + str(longitude))
else:
    get_location_from_freetext(freetext)
    work_location = Point(Decimal(longitude), Decimal(latitude))
    print("Location: latitude " + str(latitude) + ", longitude " + str(longitude))

def show_toast(rest, title, newstate):
    global rests
    wsl_notification_path = config.get('General','wsl.notification.path')
    if rests[rest] != newstate:
       rests[rest] = newstate
       if exists("/usr/bin/osascript"):
           notify("Wolt checker", title + " is " + rests[rest])
       if exists(wsl_notification_path + 'wsl-notify-send.exe'):
           subprocess.call([wsl_notification_path + 'wsl-notify-send.exe','--appId',"Wolt Checker",'-c',"Restaurant status Changed",title + ' is now ' + newstate])
       if push == True:
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

arglist.pop(0)
push=False
if arglist[0] == '-p':
    print("PUSH Mode")
    push=True
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
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + RESTNAME+" is " + termcolor.colored("Open", "green"))
            show_toast(rest, RESTNAME, 'Open')
        else:
            show_toast(rest, RESTNAME, 'Closed')
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + RESTNAME+" is " + termcolor.colored("Closed ", "red"), end='')
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
