import requests
import json
import csv
import os
import getpass
import sys

# This script will take a CSV of archival object ref id's and return a CSV of ref id's and URI's

#DETAIL
# This was written under the assumption that you might have a csv (or similar), exported from ASpace or
# compiled from an ASpace exported EAD, with an existing archival object's ref_id.

# The 1 column csv should include a header row and be formatted with the columns below:
# refID
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


#FILE INPUT / OUTPUT STUFF:
#input filename (must be in same directory as this script)
archival_object_csv = "AS_in_no_URI.csv"

#output filename
archival_object_csv_with_URIs = "AS_in.csv"

#Open Input CSV and iterate over rows
with open(archival_object_csv,'rt', encoding="utf8") as csvfile, open(archival_object_csv_with_URIs, 'w') as csvout:
	csvin = csv.reader(csvfile)
	next(csvin, None) #ignore header row

	csvout = csv.writer(csvout, lineterminator='\n') # lineterminator removes the extra empty line between each row
	csvout.writerow(['ref_ID', 'URI'])

	for row in csvin:

		# Grab the archival object's ArchivesSpace ref_id from the csv
		ref_id = row[0] #column 1 in CSV

		# Use the find_by_id endpoint (only availble in v1.5+) to retrieve the archival object's URI
		params = {"ref_id[]":ref_id}
		lookup = requests.get(aspace_url+'/repositories/2/find_by_id/archival_objects',headers=headers, params=params).json()

		# Grab the archival object uri from the search results. It should be the first and only result
		archival_object_uri = lookup['archival_objects'][0]['ref']

		print('Found AO: ' + archival_object_uri)

		# Submit a get request for the archival object and store the JSON
		#archival_object_json = requests.get(aspace_url+archival_object_uri,headers=headers).json()

		# Write ref ID and URI to output file
		csvout.writerow([ref_id, archival_object_uri[33:]])




        