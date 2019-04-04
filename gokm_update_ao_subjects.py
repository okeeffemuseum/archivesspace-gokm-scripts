import requests
import json
import csv
import os
import getpass

# USE AT YOUR OWN RISK - LIKELY REQUIRES FURTHER TESTING

# Script currently updates archival object subjects using 2 column CSV input file
# Column 1 contains the AO ref_id
# Column 2 contains the Subject Record ID (found at the end of subject URI, e.g., for URI http://localhost:8080/subjects/4, the subject record ID would be 4)

# PREREQUISITES
# This was written under the assumption that you might have a csv (or similar), exported from ASpace or
# compiled from an ASpace exported EAD, with an existing archival object's ref_id. 

# PROCESS
# Using only the ref_id, this will use the ASpace API to search for the existing archival object, retrieve its URI, store the archival
# object's JSON, and append to existing AO subject information,
# The script will then repost the archival object to ASpace using the update archival object endpoint
# PLEASE NOTE: As written, this script only appends ONE subject to the existing list of subjects

# The 2 column CSV should look like this (without a header row):
# [AO_ref_id],[subject_record_id]

# The archival_object_csv will be your starting 2 column CSV with the ASpace ref_id of the archival object's to be updated,
archival_object_csv = os.path.normpath("/Users/Jerry/Desktop/python/AS_tests/update_subjects/ao_subjects_update.csv")

# The updated_archival_object_csv will be an updated csv that will be created at the end of this script, containing all of the same
# information as the starting csv, plus the ArchivesSpace URIs for the updated archival objects
updated_archival_object_csv = os.path.normpath("/Users/Jerry/Desktop/python/AS_tests/update_subjects/processed/ao_subjects_updated.csv")

# Modify your ArchivesSpace backend url, username, and password as necessary
aspace_url = 'http://localhost:8089' #Backend URL for ASpace
username= 'user'
password = 'password'

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


#Open the CSV file and iterate through each row
with open(archival_object_csv,'rt', encoding ="utf8") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:

        # Grab the archival object's ArchivesSpace ref_id from the CSV
        ref_id = row[0] #column 1

        #Grab the subject record ID you want to add from the CSV
        subj_rec_id = row[1] #column 2 in CSV

        print('Ref ID: ' + ref_id)

        # Use the find_by_id endpoint (only availble in v1.5+) to  use the ref_ID in the CSV to retrieve the archival object's URI
        params = {"ref_id[]":ref_id}
        lookup = requests.get(aspace_url+'/repositories/2/find_by_id/archival_objects',headers=headers, params=params).json()

        
        # Grab the archival object uri from the search results
        archival_object_uri = lookup['archival_objects'][0]['ref']

        print('Archival Object: ' + archival_object_uri)

        # Submit a get request for the archival object and store the JSON
        archival_object_json = requests.get(aspace_url+archival_object_uri,headers=headers).json()

        #print the JSON reponse to see structure and figure out where you might want to add other notes or metadata values, etc.
        #print archival_object_json

        # Continue only if the search-returned archival object's ref_id matches our starting ref_id, just to be safe. Probably not necessary...
        if archival_object_json['ref_id'] == ref_id:

            # Grab the subject list and append to the CSV
            old_subjects = archival_object_json['subjects']
            row.append(old_subjects)

            # Add the archival object uri to the row from the CSV to write it out at the end
            row.append(archival_object_uri)

            # Build a new subject instance to add to the archival object
            subj_instance = {'ref':'/subjects/'+ subj_rec_id}

            # Append the new instance to the existing archival object record's instances
            archival_object_json['subjects'].append(subj_instance)
            archival_object_data = json.dumps(archival_object_json)

            #Repost the archival object containing the new subject
            archival_object_update = requests.post(aspace_url+archival_object_uri,headers=headers,data=archival_object_data).json()

            #print confirmation that archival object was updated. Response should contain any warnings
            print('Status: ' + archival_object_update['status'])

            # Write a new CSV with all the info from the initial csv + the ArchivesSpace uris for the updated archival objects
            with open(updated_archival_object_csv,'w') as csvout:
                writer = csv.writer(csvout)
                writer.writerow(row)
            #print a new line to the console, helps with readability
            print('\n')