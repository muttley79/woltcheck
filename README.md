# woltcheck
Python script to check if a wolt restaurant is ready to deliver to your location

![alt text](https://user-images.githubusercontent.com/6189366/147935485-932caef9-9c83-4541-9c1e-449eadd340a8.png?raw=true)

Prerequisits:
- Install shapely and configparser (python3 -m pip install shapely configparser apprise)
- Install libgeos-dev (apt-get install libgeos-dev)
- Add your location to properties file. You can add it as freetext or in longitude/latitude format. 
  You can find your longitude/latitude using this site https://www.latlong.net/

If you wold like to get a push to your phone, just add your provider to the config file under Push section.
You can use one or more providers using the [Apprise](https://github.com/caronc/apprise) supported configs. 

Usage:
./wolt.py [-p] restaurant [restaurant] ...
-p send push when the restaurant status change

restaurant name is taken from the wolt url
example: https://wolt.com/en/isr/tel-aviv/restaurant/cafe-noir
  in this case "cafe-noir" is the restaurant name

Added support for notifications for MAC or WINDOWS (via WSL only for now)
If you want WSL notifications you will need to download this project:
https://github.com/stuartleeks/wsl-notify-send
and set the path for the exe in the config file
