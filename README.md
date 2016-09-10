# BusLux
UIUC Bus Tracking Indicator

This code is intended to be run on a raspberry pi with an Adafruit DotStar LED strip
The code will poll the API on the CUMTD website to find the list of buses approaching your stop and how long until they get there
It will then use this information to provide a visual indicator on the LED strip.
The number of LED's between the end of the strip and the lit LED gives you the number of minutes until the bus arrives,
while the color of the LED tells you which line it is.

IE: if the 6th LED from the end of the strip is lit blue, then the 4E Blue is 6 minutes away from your stop

Installation: This program is intended to be run on a raspberry pi 2 or higher. 
- Go to the CUMTD website to generate a personal API Key and determine the Stop ID number you wish to display
- Modify the values at the top of the file to be your API Key, your Stop ID, and the pins you have connected your LED strip to
- Enjoy not being late to class!