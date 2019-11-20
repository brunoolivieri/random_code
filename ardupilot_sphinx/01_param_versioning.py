#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    This program enable parameters pages of the wiki to present older stable versions. 
    
    It works getting git hashs from firmware repository from each beta, lastest and stable version from each vehicle. Then it fecth Parameter.cpp from each (vehicle,version) tuple. After that it parser such parameter files to generate RST files for the wiki.

    It is supose to run from wiki repo. Would be better to run on Ardupilot repo and update the update.py script in wiki repo.

    It relies on Tools\autotest\param_metadata\param_parse.py from Ardupilot repo.

    It still on early tests... 
"""

import os
import shutil
import sys
import subprocess
import time
import pandas as pd
from html.parser import HTMLParser
import urllib.request
import re
from optparse import OptionParser



parser = OptionParser("python3 param_versioning.py [options]")
parser.add_option("-v", "--verbose", dest='verbose', action='store_true', default=False, help="show debugging output")
# TO-DO: single vehicle processing parser.add_option("--vehicle", default='*',  help="Vehicle type to generate for")
(opts, args) = parser.parse_args()

error_count = 0

## Parameters
COMMITFILE = "git-version.txt"
BASEURL = "http://firmware.ardupilot.org/"
ALLVEHICLES = ["Copter" ,  "Plane", "Rover", "AntennaTracker", "Sub"] 
vehicles_from_commandline = []


TEMPFOLDER = "TMPWORKFOLDER"
APMREPO = TEMPFOLDER + "/apmrepo"  # If we run this script in the server, would be clever do not download a repo.
BASEPATH = os.getcwd()


## Dicts for name replacing
vehicle_new_to_old_name = { # Used because "param_parse.py" args expect old names
    "Rover": "APMrover2",
    "Sub": "ArduSub",
    "Copter":"ArduCopter",
    "Plane":"ArduPlane",
    "Tracker":"AntennaTracker",
}

vehicle_old_to_new_name = { # Used because git-version.txt use APMVersion with old names
    "APMrover2":"Rover",
    "ArduRover":"Rover",
    "ArduSub":"Sub",
    "ArduCopter":"Copter",
    "ArduPlane":"Plane",
    "AntennaTracker":"Tracker",
}


def debug(str_to_print):
    """Debug output if verbose is set."""
    if opts.verbose:
        print(str_to_print)

def error(str_to_print):
    """Show and count the errors."""
    global error_count
    error_count += 1
    print(str_to_print)

def remove_folder(folder):
    debug("\nChecking directory %s for delete" % folder)
    if os.path.isdir(folder):
        debug("\nTrying to delete directory " + folder)
        try:
            shutil.rmtree(folder) # Does not work in Windos as expected. eate the directory   
            time.sleep(1)         # On linux/vagrant may delay time enough to setup() get error on re-create the folder
            debug("\nSuccessfully deleted folder " + folder)
        except OSError as e:  # if failed, report it back to the user 
            error("Error: %s - %s." % (e.filename, e.strerror))
            error("Failed to delete " + folder)
            #sys.exit(1)  

def setup():
    """
    Prepare a temporary folder and get Ardupilot repo.

    It happens because this script intent to run inside the Wiki repo, we would might change this idea

    """   
    ## Preseting the current folder
    path = os.getcwd()
    debug("\nThe current working directory is %s" % path)

    remove_folder(TEMPFOLDER)  # Cleanning up folder and subfolders. TO-DO: Check a possible update of a valid git repo?
    
    ## Creating a temporary folder to work with some files and downloads
    try:
        os.mkdir(TEMPFOLDER)
    except OSError:
        error("Creation of the directory %s failed" % TEMPFOLDER)
        sys.exit(1)
    else:
        debug("Successfully created the directory %s " % TEMPFOLDER)
    
    # Getting apm Repo
    # TO-DO: use GitPyhton?
    try:
        debug("GitHub Ardupilot clonning process finished")
        #os.system("git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git  "  + APMREPO) #  # TO-DO: use GitPyhton? it is really necessary get all submodules? #TO-DO: remove submodules?
        os.system("git clone https://github.com/ArduPilot/ardupilot.git  "  + APMREPO) # Needs to get all submodules? 
    except:
        error("An exception occurred: ArduPilot repo download error.")
        sys.exit(1)
    
def fetch_releases(firmware_url, vehicles):
    """
    Select folders which are named as stable for older versions.

    """

    def fetch_vehicle_subfolders(firmware_url):
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
            debug("Fetching " + firmware_url)
            lParser.feed(urllib.request.urlopen(firmware_url).read().decode('utf8'))
        except:
            error("An exception occurred: folders list download error.")
            sys.exit(1)    
        finally:
            lParser.links = []
            lParser.close()
            return links
    ######################################################################################    

    debug("Cleanning resfetched links for wanted folders")
    stableFirmwares = []
    for f in vehicles:
        page_links = fetch_vehicle_subfolders(firmware_url + f)
        for l in page_links:    # Non clever way to filter the strings for filter folders
            version_folder = str(l)
            #print(version_folder)
            if version_folder.find("stable")>0 and not version_folder.endswith("stable"): # If finish with
                stableFirmwares.append(firmware_url[:-1] + version_folder[10:-2])  
            elif version_folder.find("latest") > 0 :
                stableFirmwares.append(firmware_url[:-1] + version_folder[10:-2])  
            elif version_folder.find("beta") > 0:
                stableFirmwares.append(firmware_url[:-1] + version_folder[10:-2])  

    return stableFirmwares # links for the firmwares folders

def get_commit_dict(releases_parsed):
    """
    For informed releases, return a dict git hashs of its build.

    """        
    def get_last_board_folder(url):
        """
        For given URL returns the last folder which should be a board name. 

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
            debug("Fetching " + url)
            lParser.feed(urllib.request.urlopen(url).read().decode('utf8'))
        except:
            error("An exception occurred: folders list download error.")
            sys.exit(1) #comment to make easer debug (temporary)    
        finally:
            lParser.links = []
            lParser.close()
            last_item = links.pop()
            last_folder = last_item['href']
            debug("Returning link " + last_folder[last_folder.rindex('/')+1:])
            return last_folder[last_folder.rindex('/')+1:]  # clean the partial link
    ####################################################################################################
            

    def fetch_commit_hash(version_link, board, file):
        """
        For a binnary folder, gets a git hash of its build.

        """
        fetch_link = version_link + '/' + board + '/' + file

        print("Processing link...\t" + fetch_link)
        
        try:
            fecth_response = ""
            with urllib.request.urlopen(fetch_link) as response:
                fecth_response = response.read().decode("utf-8")    
            
            commit_details = fecth_response.split("\n")
            commit_hash = commit_details[0][7:]
            #version =  commit_details[6] the sizes cary
            version = commit_details.pop(-2)

            version_number =  version.split(" ")[2]
            vehicle = version.split(" ")[1]

            regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]') 

            if (regex.search(vehicle) == None):  # there are some non standart names
                vehicle = vehicle_old_to_new_name[vehicle.strip()]   # Names may not be standart as expected
            else:            
                # tries to fix automatically
                if re.search('copter', vehicle, re.IGNORECASE):
                    vehicle = "Copter"
                    debug("Bad vehicle name auto fixed to COPTER on:\t" + fetch_link)
                elif re.search('plane', vehicle, re.IGNORECASE):
                    vehicle = "Plane"
                    debug("Bad vehicle name auto fixed to PLANE on:\t" + fetch_link)                    
                elif re.search('rover', vehicle, re.IGNORECASE):
                    vehicle = "Rover"
                    debug("Bad vehicle name auto fixed to ROVER on:\t" + fetch_link)
                elif re.search('sub', vehicle, re.IGNORECASE):
                    vehicle = "Sub"
                    debug("Bad vehicle name auto fixed to SUB on:\t" + fetch_link)
                elif re.search('tracker', vehicle, re.IGNORECASE):
                    vehicle = "Tracker"
                    debug("Bad vehicle name auto fixed to TACKER on:\t" + fetch_link)
                else:
                    error("Nomenclature exception found in a vehicle name:\t" + vehicle + "\tLink with the exception:\t" + fetch_link)

            if "beta" in fetch_link:
                version_number = "beta-" + version_number

            if "latest" in fetch_link:
                version_number = "latest-" + version_number

            return vehicle, version_number, commit_hash        
        except:
            error("An exception occurred: " + file + " DECODE ERROR. Link: " + fetch_link)
            #sys.exit(1) #comment to make easer debug     
            return "error", "error","error"
    ####################################################################################################

    commits_and_codes = {}
    commite_and_codes_cleanned = {}

    for j in range(0,len(releases_parsed)-1):
        commits_and_codes[j] = fetch_commit_hash(releases_parsed[j], get_last_board_folder(releases_parsed[j]), COMMITFILE)

    for i in commits_and_codes:
        if commits_and_codes[i][0] != 'error':
            commite_and_codes_cleanned[i] = commits_and_codes[i] 
    
    return commite_and_codes_cleanned

def generate_rst_files(commits_to_checkout_and_parse):

    # it uses a Ardupilot clonned repo. It is slow and heavy to process. But I would like to get files from github like: https://raw.githubusercontent.com/ArduPilot/ardupilot_wiki/4dedc67f8734bae3318f803480b2c5d2dc0e38c5/common/source/docs/common-parameter-reset.rst

    for i in commits_to_checkout_and_parse:
    
        vehicle = str(commits_to_checkout_and_parse[i][0])
        version = str(commits_to_checkout_and_parse[i][1])
        commit_id = str(commits_to_checkout_and_parse[i][2])

        # These  have errors on parsing using param_parser.py 
        # TO-DO: exceptions to deal OR insert all at once in wiki repo because it is static data?    
        if  ( 
            "3.2.1" in version or #last stable APM Copter
            "3.4.0" in version or # last stable APM Plane
            "2.42" in version or # last stable APM Rover
            "2.51" in version or # last beta APM Rover?
            "0.7.2" in version or # last APM Antenna tracker???    
            ):
            debug("Ignoring APM version:\t" + vehicle + "\t" + version)
            continue

        # Checkout an Commit ID    
        # TO-DO: use GitPyhton?
        try:
            debug("Git checkout on " + vehicle + " version " + version + " id " + commit_id )
            os.chdir(BASEPATH + "/" + APMREPO)
            os.system("git checkout --force " + commit_id)
            os.chdir(BASEPATH)
        except:
            error("An exception occurred: GIT checkout error")
            sys.exit(1)
        debug("")

        # Run param_parse.py tool from Autotest set
        try:
            os.chdir(BASEPATH + "/" + APMREPO + "/Tools/autotest/param_metadata" )
            # option "param_parse.py --format rst" is not available in all commits where param_parse.py is found
            os.system("python param_parse.py --vehicle " + vehicle_new_to_old_name[vehicle])
            os.rename("Parameters.rst", "parameters-" + vehicle + "-" + version  +".rst")
            print("File " + "parameters-" + vehicle + "-" + version  +".rst generated...")    
            os.chdir(BASEPATH)
        except:
            error("An exception occurred: Error while parsing Parameters.rst | details:\t" +  vehicle + "\t" + version  + "\t" + commit_id)
            #sys.exit(1)
        print("")

    
    return 1
        



# Step 1 - prepare
setup()
################################################################

# Step 2 - get releases
feteched_releases = fetch_releases(BASEURL, ALLVEHICLES)
commits_to_checkout_and_parse = get_commit_dict(feteched_releases)
################################################################

# Between steps - Partial results
print("\n\tList of parameters files to generate:\n")
for i in commits_to_checkout_and_parse:
    print(commits_to_checkout_and_parse[i][0] + ' - ' + commits_to_checkout_and_parse[i][1] + ' - ' + commits_to_checkout_and_parse[i][2])
print("")
################################################################

# Step 3 - Generate RST file for each commit ID
generate_rst_files(commits_to_checkout_and_parse)
################################################################

# Step 4 - Run a anchor replacement. (a sed? re-uses the generate_rst_files()?)

# Step 5 option A - If runs at Ardupilot repo, creates a tgz to download by wiki build script.

# Step 5 option B - If runs at Wiki repo, just move generated files to right places.


#sys.exit(error_count)



