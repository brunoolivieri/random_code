#!/usr/bin/env python
# -*- coding: utf-8 -*-





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

TEMPFOLDER = "TMPWORKFOLDER"
APMREPO = TEMPFOLDER + "/apmrepo"

# GitHub parameters
# fileRepoTags = TEMPFOLDER + "/ardupilotRepoTags.txt"
# releasesNegativeFilter = ["^" , "{" , "rc"] # only for github as a source

def setup():
	## Preseting the current folder
	path = os.getcwd()
	print ("\nThe current working directory is %s" % path)


	## Creating a temporary folder to work with some files and downloads
	try:
		os.mkdir(TEMPFOLDER)
	except OSError:
		print ("Creation of the directory %s failed" % TEMPFOLDER)
	else:
		print ("Successfully created the directory %s " % TEMPFOLDER)

    try:
        os.system("git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git  "  + APMREPO) # it is really necessary get all submodules? #TO-DO: remove submodules?
    except:
        print("An exception occurred: ArduPilot download error.")
        sys.exit(1)
	
# def fetchGitHub():
# 	## Listing releases commits from GITHUB
# 	try:
# 		tagsList = subprocess.run(['git ls-remote --tags https://github.com/ArduPilot/ardupilot.git > ' + fileRepoTags],  check=True, shell=True, universal_newlines=True)
# 	except:
# 		print("An exception occurred: tags download error.")
# 		sys.exit(1)
# 	finally:
# 		print("File with all tag generated on " + TEMPFOLDER + '/ardupilotRepoTags.txt')

# 	df =  pd.read_csv(fileRepoTags, sep='\t', header=None)
# 	df.columns = ["commits", "tags"]
# 	print(df)


# For a single vehicle get all folders in the first level
def fetchVehicleReleases(thisurl):

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

# For each vehicle in list, get STABLE folders
def fetchAllStableReleases(thisUrl, listOfVehicles):
	stableFirmwares = []
	for f in listOfVehicles:
		firmwares = fetchVehicleReleases(thisUrl + f)
		for l in firmwares:    #Non clever way to filter the strings
			foo = str(l)
			if (foo.find("stable")) > 0:
				stableFirmwares.append(thisUrl[:-1] + foo[10:-2])  

	return stableFirmwares

# Fetch a firmware coomitID and code/tag
def fectchAstableCommit(rootLink, board, file):
	fetchLink = rootLink + '/' + board + '/' + file
	try:
		with urllib.request.urlopen(fetchLink) as response:
			tmpResponse = response.read().decode("utf-8")	
			commitDetails = tmpResponse.split("\n")
			commitID = commitDetails[0][7:]
			version =  commitDetails[4]
			versionVehicle = version.split(":")[0]
			#versionNumber = version.split("to ")[1] # This lie is not standard between vechilces.
	
			## counter measures
			digits = re.match('.+([0-9])[^0-9]*$', version) # It is not clever		
			lastDigit = digits.start(1) 					#
			m = re.search(r"\d", version)					#
			firstDigit = m.start()							#
			###
	
			versionNumber = version[firstDigit:lastDigit+1]
			versionCode = versionVehicle.lstrip() + '-' + versionNumber
			#print('|' + commitID + '|' + versionCode + '|')
			return commitID, versionCode		
	except:
		print("An exception occurred: " + file + " download and decode error. Link: " + fetchLink)
		#sys.exit(1) #comment to make easer debug (temporary)	
		return "error", "error" # APM does not have the default board. Deal with it latter


#setup()

#allStableReleases = fetchAllStableReleases(BASEURL, VEHICLES)

commitsAndCodes = {}
# For each release get commit ID and releaseID
#for j in range(0,len(allStableReleases)-1):
#	commitsAndCodes[j] = fectchAstableCommit(allStableReleases[j], DEFAULTBOARD, COMMITFILE)

# mostra todos
#for i in commitsAndCodes:
#	if commitsAndCodes[i][0] != 'error':
#		print(commitsAndCodes[i][0] + '-' + commitsAndCodes[i][1])





