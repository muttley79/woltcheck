# woltcheck
Python script to check if a wolt restaurant is ready to deliver to your location

Prerequisits:
- Install shapely (python3 -m pip install shapely)
- Install libgeos-dev
- Get your desired location in the form of (longitude, latitude) - meaning longitude first

If you wold like to get a push to your phone, you will need to update the function 'sendpush' with a code from your provider
(I use pushover, you can use pushbullet or any other service that has an api)
