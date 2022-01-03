# woltcheck
Python script to check if a wolt restaurant is ready to deliver to your location

![alt text](https://user-images.githubusercontent.com/6189366/147935485-932caef9-9c83-4541-9c1e-449eadd340a8.png?raw=true)

Prerequisits:
- Install shapely and configparser (python3 -m pip install shapely configparser)
- Install libgeos-dev (apt-get install libgeos-dev)
- add your location to properties file

If you wold like to get a push to your phone, you will need to update the function 'sendpush' with a code from your provider
(I use pushover, you can use pushbullet or any other service that has an api)
If you use pushover, you can only update the user and token in the properties file

Usage:
./wolt.py [-p] restaurant [restaurant] ...
-p send push when the first restaurant is available
  NOTE - this requires edit of the sendpush function to use your push provider

restaurant name is taken from the wolt url
example: https://wolt.com/en/isr/tel-aviv/restaurant/cafe-noir
  in this case "cafe-noir" is the restaurant name

  
