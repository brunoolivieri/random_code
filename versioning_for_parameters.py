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
VEHICLES = ["Copter"] #,  "Plane", "Rover"]   # not tested yet: "AntennaTracker", "Sub"

TEMPFOLDER = "TMPWORKFOLDER"
APMREPO = TEMPFOLDER + "/apmrepo"
BASEPATH = os.getcwd()

truename_map = { # Used because "param_parse.py" args expect old names
    "Rover": "APMrover2",
    "Sub": "ArduSub",
    "Copter":"ArduCopter",
    "Plane":"ArduPlane",
    "Tracker":"AntennaTracker",
}

def setup():
	"""
    Prepare a temporary folder and get Ardupilot repo.

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
		os.system("git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git  "  + APMREPO) #  # TO-DO: use GitPyhton? it is really necessary get all submodules? #TO-DO: remove submodules?
	except:
		print("An exception occurred: ArduPilot download error.")
		sys.exit(1)
	
def fetch_stable_releases(thisUrl, listOfVehicles):
	"""
    Select folders which are named as stable for older versions.

    """

	def fetch_vehicle_subfolders(thisurl):
		"""
		Fetch firmware.ardupilot.org/baseURL all first level folders for a given base URL.

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

	stableFirmwares = []
	for f in listOfVehicles:
		firmwares = fetch_vehicle_subfolders(thisUrl + f)
		for l in firmwares:    # Non clever way to filter the strings for filter only stable folders
			foo = str(l)
			if (foo.find("stable")) > 0:
				stableFirmwares.append(thisUrl[:-1] + foo[10:-2])  

	return stableFirmwares

def get_commit_dict(stableReleases):
	"""
	For informed releases, return a dict git hashs of its build.

	"""    	

	def fetch_commit_hash(rootLink, board, file):
		"""
		For a binnary folder, gets a git hash of its build.

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
				#versionNumber = version.split("to ")[1] # This is not standard between vechicles.
		
				## workaround
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
	####################################################################################################

	commitsAndCodes = {}
	cleanRegisters = {}

	for j in range(0,len(stableReleases)-1):
		commitsAndCodes[j] = fetch_commit_hash(stableReleases[j], DEFAULTBOARD, COMMITFILE)

	for i in commitsAndCodes:
		if commitsAndCodes[i][0] != 'error':
			cleanRegisters[i] = commitsAndCodes[i] 
			#print(commitsAndCodes[i][0] + ' - ' + commitsAndCodes[i][1] + ' - ' + commitsAndCodes[i][2])
    
	return cleanRegisters

def generate_rst_files(commits_to_checkout_and_parse):


	def inplace_change(filename, old_string, new_string):
		# Safely read the input filename using 'with'
		with open(filename) as f:
			s = f.read()
			if old_string not in s:
				print('"{old_string}" not found in {filename}.'.format(**locals()))
				return

		# Safely write the changed content, if found in the file
		with open(filename, 'w') as f:
			s = f.read()
			print('Changing "{old_string}" to "{new_string}" in {filename}'.format(**locals()))
			s = s.replace(old_string, new_string)
			f.write(s)


	file_flag = "Copter-3.6.171"

	# Checkout an Commit ID # TO-DO: use GitPyhton?
	try:
		os.chdir(BASEPATH + "/" + APMREPO)
		os.system("git checkout --force 71093b86366942e2793217a02b53cc442bf29148")
		os.chdir(BASEPATH)
	except:
		print("An exception occurred: GIT checkout error")
		traceback.print_exc()
		sys.exit(1)

	# Run param_parse.py tool from Autotest set
	try:
		os.chdir(BASEPATH + "/" + APMREPO + "/Tools/autotest/param_metadata" )
		os.system("python param_parse.py --format rst --vehicle ArduCopter")
		#os.rename("Parameters.rst", "Parameters-" + file_flag + ".rst")
		#os.chdir(BASEPATH)
	except:
		print("An exception occurred: Error while parsing Parameters.rst ")
		traceback.print_exc()
		sys.exit(1)

	# parei aqui!!!
	# Rename file anchors and move it
	try:
		os.chdir(BASEPATH + "/" + APMREPO + "/Tools/autotest/param_metadata" )
		inplace_change("Parameters.rst","_parameters","_parameters-" + file_flag)
		os.rename("Parameters.rst", "Parameters-" + file_flag + ".rst")
		os.chdir(BASEPATH)
	except:
		print("An exception occurred: Error while dealing with Parameters-" + file_flag + ".rst")
		traceback.print_exc()
		sys.exit(1)



	return 1
    	



# 1 - prepare
#setup()
################################################################

# 2 - get releases
fetched_stable_releases = fetch_stable_releases(BASEURL, VEHICLES)
commits_to_checkout_and_parse = get_commit_dict(fetched_stable_releases)

# Partial results
print("\n List of parameters files to generate:")
for i in commits_to_checkout_and_parse:
    print(commits_to_checkout_and_parse[i][0] + ' - ' + commits_to_checkout_and_parse[i][1] + ' - ' + commits_to_checkout_and_parse[i][2])
print("")
################################################################

# 3 - Generate RST file for each commit ID
generate_rst_files(commits_to_checkout_and_parse)



# 4 - For each parameter file parse it and rename for the vehicle and version .RST - Question: 
# 5 - Create a new page structure for mutiple parameters page in each vehicle
# 5.1 - A landinpage that always link the present Parameters.rst schema
# 5.2 -  





