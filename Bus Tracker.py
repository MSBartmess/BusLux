#!/usr/bin/python
from xml.etree.ElementTree import ElementTree #For parsing the XML
import urllib2 #For retreiving the XML
import smtplib 
import numpy as np
import time
import traceback
import sys, os
from datetime import datetime, timedelta
from datetime import time as tm
from dotstar import Adafruit_DotStar

apiKey = "fa033289945c4af587b0e1799c5e9040" #This should be changed to your API Key
stopID = 'ARYWRT' #This should be changed to your stop ID.

# Initialize the LED Strip, datapin should be on 23, clockpin should be on 24
numpixels = 30 # Number of LEDs in strip
datapin   = 23
clockpin  = 24
#Aparently due to manufacturing differences, the LED's may not take the colors
#in RGB order, so you may have to test this a few times to get the colors correct
strip     = Adafruit_DotStar(numpixels, datapin, clockpin, order='bgr')
strip.begin()

#busXML: This will retreive the data from a given request URL
def busXML(request):
    XMLDoc = urllib2.urlopen(request) #use the urllib2 module to retreive the data
    contents = XMLDoc.read() #Read the documents into a string
    file = open("bus.xml",'w') #Open a file for writing and write the contents
    file.write(contents)
    file.close()
    return 'bus.xml' #Return the file name

#Represents the color of an LED and its name, and provides a method for generating the
#Color Hex
class Pixel:
    #Initialization Method
    def __init__ (self, red, green, blue, name):
        self.red = red;
        self.blue = blue;
        self.green = green;
        self.name = name;
    #Returns the RGB String to be sent to the LED strip
    def colorHex(self):
        color = self.red;
        color = color << 8;
        color = color + self.green;
        color = color << 8;
        color = color + self.blue;
        return color
#Object to handle when multiple buses are the same distance away
#Holds an array of pixels to flash between
class Blinker:
    def __init__ (self):
	self.colors = []
	#Includes a off pixel when no color is assigned
	self.colors.append(Pixel(0,0,0,"off"));
	#curColor keeps track of which color is being displayed
	self.curColor = 0;
    
    #Adds a pixel to the blinker
    def addColor(self,color):
        #If the blinker was empty, remove the off pixel
	if(self.colors[0].name == "off"):
            del self.colors[:]
        #Add the new color
        self.colors.append(color)
    
    #This returns the RGB string of the next color
    def nextColor(self):
        outColor = self.colors[self.curColor] #Get the pixel to be displayed
        #Increment the current color, if it is outside the max number of colors set to 0
	self.curColor = (1+self.curColor) % len(self.colors)
	outHex = outColor.colorHex(); #Get the RGB string
	return outHex

lightList = [];        
#List of bus headsigns and their associated color
northBuses = {"100N Yellow": Pixel(255,255,0,"yellow")
              ,"1N Yellow": Pixel(255,255,0,"yellow")
              ,"1N YELLOWhopper": Pixel(255,255,0,"yellow")
              ,"4E Blue": Pixel(0,0,255,"blue")
              ,"9B Brown": Pixel(102,51,0,"brown")
              ,"130N Silver": Pixel(190,190,190,"silver")
              ,"13N Silver": Pixel(190,190,190,"silver")
	      ,"22N Illini": Pixel(80,0,80,"purple")
              ,"220N Illini": Pixel(90,0,90,"purple")}
#continuously loop this
while True:
    #Get the current time in CMT
    now = datetime.now() - timedelta(hours=6)
    now_time = now.time()
    #durring the day, set the brightness to 5
    if now_time >= tm(7,30) and now_time <= tm(22,00):
	strip.setBrightness(5)
    #At night, reduce the brightness to 1
    else:
        strip.setBrightness(1)
        
    #Clear the list of blinkers, and append a list of empty ones
    del lightList[:]
    for i in range(numpixels):
        lightList.append(Blinker());
    #Generate the URL
    url = "https://developer.cumtd.com/api/v2.2/xml/GetDeparturesByStop?key="\
      +apiKey+"&stop_id=" + stopID
    #Attempt to connect to the API and access the approaching buses
    try:
        tree = ElementTree() #Create an ElementTree
        tree.parse(busXML(url)) #Parse the returned XML file
        root = tree.getroot() #Find the Root Node
        for departure in root.iter("departure"): #Iterate throught the buses returned
            headsign = departure.get('headsign')
            expectedMins = departure.get('expected_mins')
            expMins = int(expectedMins) #Cast the number of expected minutes as an int
            if(expMins < numpixels): #Only display the bus if it is within the LED strips range
                #if the headsign is recognized, then add it to the LED strip
                if (headsign in northBuses):
                        pixel = northBuses[headsign]
                        lightList[numpixels-1-expMins].addColor(pixel)
        #now iterate through the lightList and update the colors for 30 seconds
	for i in range(30):
	    #Get the next color of each pixel and set the internal model of the light strip
            for i in range(numpixels):
		outHex = lightList[i].nextColor()
		strip.setPixelColor(i,outHex)
	   #synchronize the internal model of the light strip with the physical one
	    strip.show();
	    #Wait one second to update again
            time.sleep(1);
	    
   
    except KeyboardInterrupt:
        #Allow the program to be killed
        raise
    except:
        #Otherwise, write the error to a log file
        #Open the log file
        log = open("BusErrors.txt","a")
        #Add a line for legibility
	log.write("__________________________\n")
	log.write("Log: \n");
	#Get the exception info and write it to the file
	tb = sys.exc_info()[2]
	tbinfo = traceback.format_tb(tb)[0]
	errorMessage = "\n"+tbinfo+"\n"
	log.write(""+errorMessage)
	log.close()
	print "error"
	#Sleep for 15 seconds before trying again
	time.sleep(15);
	
#When killed, clean up the GPIO outputs on the raspberry pi
GPIO.cleanup()        
        
