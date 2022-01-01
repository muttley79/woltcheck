#!/usr/bin/python3
import sys
import time
import requests
import json
import datetime
import http.client, urllib
import configparser
from decimal import Decimal

config = configparser.RawConfigParser()
config.read('config.properties')

# Must install shapely
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

sys.tracebacklimit = 0

#remember to change this
work_location = Point(Decimal(config.get('Location','workplace.longitude')), Decimal(config.get('Location','workplace.latitude')));

def isOpenNow(opening_times):
    today = datetime.datetime.now().strftime("%A").lower();
    if opening_times[today]==[]:
       return False;
    now = datetime.datetime.now();
    current=(((now.hour*60)+now.minute)*60000)
    for a in opening_times[today]:
        if a["value"]["$date"] > current:
           if a["type"] == "open":
              return False;
           else:
              return True;
        else:
           if a["type"] == "open":
              return True;
           else:
              return False;


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

def sendpush(text):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
    "token": config.get('Push','push.token'),
    "user": config.get('Push','push.user'),
    "message": text,
     }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

def locationAvailable(pointarray, point):
    polygon = Polygon(pointarray);
    return(polygon.contains(point));

def getEnglishName(arr,origname):
    for a in arr:
        if a["lang"] == 'en':
           return a["value"];
    return origname;


arglist=sys.argv
if len(arglist) < 2:
    print("usage: wolt [-p] restaurant-name [restaurant-name] ...");
    sys.exit(1);

arglist.pop(0);
push="false"
if arglist[0] == '-p':
    print("PUSH Mode");
    push="true";
    arglist.pop(0)

if len(arglist) == 0:
    print("No restaurant[s] supplied")
    sys.exit(1);

while(True):
    for rest in arglist:
        #print(rest);
        JSON=json.loads(requests.get("https://restaurant-api.wolt.com/v3/venues/slug/"+rest).text);
        RESTONLINE=JSON["results"][0]["online"];
        RESTALIVE=JSON["results"][0]["alive"];
        RESTDELV=JSON["results"][0]["delivery_specs"]["delivery_enabled"];
        RESTTOLOCATION=locationAvailable(JSON["results"][0]["delivery_specs"]["geo_range"]["coordinates"][0],work_location);
        RESTNAME=getEnglishName(JSON["results"][0]["name"],rest);
        RESTOPENHOURS=isOpenNow(JSON["results"][0]["opening_times"]);
        if ((RESTONLINE == True) and (RESTALIVE == 1) and (RESTDELV == True) and (RESTTOLOCATION == True) and (RESTOPENHOURS == True)):
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + RESTNAME+" is " + bcolors.OKGREEN + "Open" + bcolors.ENDC);
            if push=="true":
                sendpush(RESTNAME + " is Open");
                print("Push sent");
                sys.exit(0);
        else:
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + RESTNAME+" is " + bcolors.FAIL + "Closed " + bcolors.ENDC, end='');
            if RESTOPENHOURS == False:
                print("(Outside of open hours)");
            elif RESTONLINE == False:
                print("(Offline)");
            elif RESTALIVE != 1:
                print("(Not Alive)");
            elif RESTDELV == False:
                print("(No Delivery)");
            elif RESTTOLOCATION == False:
                print("(Not delivering to our location)");
    time.sleep(10);
