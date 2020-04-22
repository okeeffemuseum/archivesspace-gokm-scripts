import requests
import json
import csv
import os
import getpass
import sys

# This script will batch create new digital object records in ArchivesSpace (from CSV input) and link them as instances of an existing archival object

#DETAIL
# This was written under the assumption that you might have a csv (or similar), exported from ASpace or
# compiled from an ASpace exported EAD, with an existing archival object's ref_id.

# Using only the archival object's ref_id, this script will:
#1. use the ASpace API to search for the existing archival object (find_by_id endpoint), retrieve its URI, and store the archival object's JSON
#2. create a new digital object record using the title and an identifier supplied in the input CSV
#3. grab the URI for the newly created digital object and publish the digital object and all file version components (based on true or false input)
#4. link the digital object as an instance to the archival object JSON
#5. repost the archival object to ASpace using the update archival object endpoint
#6. write out a CSV containing the same information as the starting CSV plus the ARchivesSpace URIs for the new digital object and updated archival object

# The 4 column csv should include a header row and be formatted with the columns below:
# refID, digital object identifier, digital object title, publish?
# The first column is row[0] in Python

#AUTHENTICATION STUFF:

#Prompt for backend URL ( e.g. http://localhost:8089) and login credentials
aspace_url = "http://archivesspace:8089" #input('ASpace backend URL: ')
username = input('ASpace Username: ')
password = getpass.getpass(prompt='Password: ')

#Authenticate and get a session token
try:
    auth = requests.post(aspace_url+'/users/'+username+'/login?password='+password).json()
except requests.exceptions.RequestException as e:
    print("Invalid URL, try again")
    exit()
#test authentication
if auth.get("session") == None:
    print("Wrong username or password! Try Again")
    exit()
else:
#print authentication confirmation
    print("Hello " + auth["user"]["name"]) 

session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

ref_id = "ref94_qmv"

print('Searching for ' + ref_id)

# Use the find_by_id endpoint (only availble in v1.5+) to retrieve the archival object's URI
params = {"ref_id[]":ref_id}
lookup = requests.get(aspace_url+'/repositories/2/find_by_id/archival_objects',headers=headers, params=params).json()

# Grab the archival object uri from the search results. It should be the first and only result
archival_object_uri = lookup['archival_objects'][0]['ref']

print('Found AO: ' + archival_object_uri)

# Submit a get request for the archival object and store the JSON
archival_object_json = requests.get(aspace_url+archival_object_uri,headers=headers).json()

print(archival_object_json)

        