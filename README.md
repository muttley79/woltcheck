# woltcheck
Python script to check if a wolt restaurant is ready to deliver to your location

Prerequisits:
- Install shapely and configparser (python3 -m pip install shapely configparser)
- Install libgeos-dev
- add your location to properties file

If you wold like to get a push to your phone, you will need to update the function 'sendpush' with a code from your provider
(I use pushover, you can use pushbullet or any other service that has an api)

Usage:
./wolt.py [-p] restaurant [restaurant] ...
-p send push when the first restaurant is availeble
  NOTE - this requires edit of the sendpush function to use your push provider

restaurant name is taken from the wolt url
example: https://wolt.com/en/isr/tel-aviv/restaurant/cafe-noir
  in this case "cafe-noir" is the restaurant name
  
