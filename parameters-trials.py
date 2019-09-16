#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    This program enable extend the parameters pages of the wiki 
    to present older stable versions.

    It is intended to be run on the main wiki server or
    locally within the project's Vagrant environment. 

    It relies on Tools\autotest\param_metadata\param_parse.py

    It still on early tests...
"""

import os
import sys
import subprocess
import pandas as pd
from html.parser import HTMLParser
import urllib.request
import re

## Parameters
DEFAULTBOARD = "Pixhawk1"
COMMITFILE = "git-version.txt"
BASEURL = "http://firmware.ardupilot.org/"
VEHICLES = ["Copter"]  #,  "Plane", "Rover"]   # not supported yet: "AntennaTracker", "Sub"

TRUENAME_MAP = {
#    "APMrover2": "Rover",
#   "ArduSub": "Sub",
    "ArduCopter": "Copter",
#    "ArduPlane": "Plane",
#    "AntennaTracker": "Tracker",
}

TEMPFOLDER = "TMPWORKFOLDER"
APMREPO = TEMPFOLDER + "/apmrepo"


def setup():
	"""
    Prepare folders and get Ardupilot repo.

    """
    
    ## Preseting the current folder
	path = os.getcwd()
	print ("\nThe current working directory is %s" % path)

	## Creating a temporary folder to work with some files and downloads
	try:
		os.mkdir(TEMPFOLDER)
	except OSError:
		print ("Creation of the directory %s failed" % TEMPFOLDER)
		sys.exit(1)
	else:
		print ("Successfully created the directory %s " % TEMPFOLDER)
    
    # Getting apm Repo
	try:
		os.system("git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git  "  + APMREPO) # it is really necessary get all submodules? #TO-DO: remove submodules?
	except:
		print("An exception occurred: ArduPilot download error.")
		sys.exit(1)
	
def fetchVehicleReleases(thisurl):
	"""
    Fetch firmware.ardupilot.org all first level folders for each vehicle.

    """
	links = []
	#Define HTML Parser
	class parseText(HTMLParser):
		def handle_starttag(self, tag, attrs):
			if tag != 'a':
				return
			attr = dict(attrs)
			links.append(attr)

	#Create instance of HTML parser
	lParser = parseText()
	#Feed HTML file into parsers
	try:
		lParser.feed(urllib.request.urlopen(thisurl).read().decode('utf8'))
	except:
		print("An exception occurred: folders list download error.")
		#sys.exit(1) #comment to make easer debug (temporary)	
	finally:
		lParser.links = []
		lParser.close()
		return links

def fetchAllStableReleases(thisUrl, listOfVehicles):
	"""
    Select folders which are named as stable for older versions.

    """
	stableFirmwares = []
	for f in listOfVehicles:
		firmwares = fetchVehicleReleases(thisUrl + f)
		for l in firmwares:    #Non clever way to filter the strings
			foo = str(l)
			if (foo.find("stable")) > 0:
				stableFirmwares.append(thisUrl[:-1] + foo[10:-2])  

	return stableFirmwares

def fectchAstableCommit(rootLink, board, file):
	"""
    For a stable folder, gets a git hash of its build.

    It relies on a default board.

    """

	fetchLink = rootLink + '/' + board + '/' + file
	try:
		with urllib.request.urlopen(fetchLink) as response:
			tmpResponse = response.read().decode("utf-8")	
			commitDetails = tmpResponse.split("\n")
			commitID = commitDetails[0][7:]
			version =  commitDetails[4]
			versionVehicle = version.split(":")[0]
			#versionNumber = version.split("to ")[1] # This lie is not standard between vechicles.
	
			## counter measures
			digits = re.match('.+([0-9])[^0-9]*$', version) # It is not clever		
			lastDigit = digits.start(1) 					#
			m = re.search(r"\d", version)					#
			firstDigit = m.start()							#
			###
	
			versionNumber = version[firstDigit:lastDigit+1]
			#versionCode = versionVehicle.lstrip() #+ '-' + versionNumber
			#print('|' + commitID + '|' + versionCode + '|')
			return versionVehicle.lstrip(), versionNumber, commitID		
	except:
		print("An exception occurred: " + file + " download and decode error. Link: " + fetchLink)
		#sys.exit(1) #comment to make easer debug (temporary)	
		return "error", "error" # APM does not have the default board. Deal with it latter

def getCommitsToCheckout(stableReleases):
    
    commitsAndCodes = {}
    cleanRegisters = {}

    for j in range(0,len(stableReleases)-1):
        commitsAndCodes[j] = fectchAstableCommit(stableReleases[j], DEFAULTBOARD, COMMITFILE)

    for i in commitsAndCodes:
        if commitsAndCodes[i][0] != 'error':
            cleanRegisters = commitsAndCodes[i] # print(commitsAndCodes[i][0] + ' - ' + commitsAndCodes[i][1] + ' - ' + commitsAndCodes[i][2])
    
    return cleanRegisters


# 1 - prepare
#setup()

# 2 - get releases
allStableReleases = fetchAllStableReleases(BASEURL, VEHICLES)
commitsToGetParameters = getCommitsToCheckout(allStableReleases)

for i in commitsToGetParameters:
    print(commitsToGetParameters[i][0] + ' - ' + commitsToGetParameters[i][1] + ' - ' + commitsToGetParameters[i][2])








