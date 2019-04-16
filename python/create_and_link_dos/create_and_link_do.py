import requests
import json
import csv
import os
import getpass

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
aspace_url = input('ASpace backend URL: ')
username = input('Username: ')
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
archival_object_csv = "linked_DAM_AS.csv"

#output filename
updated_archival_object_csv = "updated_AO_DO_report.csv"

#prompt for publishing digital objects and components (true or false)
publish_true_false = input("Publish Digital Objects? true or false?: ")


#Open Input CSV and iterate over rows
with open(archival_object_csv,'rt', encoding="utf8") as csvfile:
    csvin = csv.reader(csvfile)
    next(csvin, None) #ignore header row
    
    for row in csvin:

        # Grab the archival object's ArchivesSpace ref_id from the csv
        ref_id = row[0] #column 1 in CSV
        
        # Use an identifier and a file_uri from the csv to create the digital object
        digital_object_identifier = row[1] #column 2 in CSV
        #digital_object_title = row[2] #column 3 in CSV

        print('Searching for ' + ref_id)

        # Use the find_by_id endpoint (only availble in v1.5+) to retrieve the archival object's URI
        params = {"ref_id[]":ref_id}
        lookup = requests.get(aspace_url+'/repositories/2/find_by_id/archival_objects',headers=headers, params=params).json()

        # Grab the archival object uri from the search results. It should be the first and only result
        archival_object_uri = lookup['archival_objects'][0]['ref']

        print('Found AO: ' + archival_object_uri)

        # Submit a get request for the archival object and store the JSON
        archival_object_json = requests.get(aspace_url+archival_object_uri,headers=headers).json()

        # Continue only if the search-returned archival object's ref_id matches our starting ref_id, just to be safe
        # Note: probably no longer necessary when using the find_by_id endpoint
        if archival_object_json['ref_id'] == ref_id:

            # Add the archival object uri to the row from the csv to write it out at the end
            row.append(archival_object_uri)

            # Reuse the display string from the archival object as the digital object title
            # Note: a more sophisticated way of doing this would be to add the title and dates from the
            # archival object separately into the appropriate title and date records in the digital object
            # This also does not copy over any notes from the archival object
            title = archival_object_json['title']

            # Form the digital object JSON using the display string from the archival object and the identifier and the file_uri from the csv
            new_dig_obj_json = {'title':title, 'digital_object_id':digital_object_identifier}
            dig_obj_data = json.dumps(new_dig_obj_json)

            # Post the digital object
            dig_obj_post = requests.post(aspace_url+'/repositories/2/digital_objects',headers=headers, data=dig_obj_data).json()

            #print("New DO: " + dig_obj_post['status'])

            #Grab the digital object uri 
            dig_obj_uri = dig_obj_post['uri']

            #print('New DO URI: ' + dig_obj_uri)

            #publish the digital object
            if publish_true_false == 'true':
                print('Publishing: ' + dig_obj_uri)
                dig_obj_publish_all = requests.post(aspace_url + dig_obj_uri + '/publish',headers=headers)


            # Add the digital object uri to the row from the csv to write it out at the end
            row.append(dig_obj_uri)

            # Build a new instance to add to the archival object, linking to the digital object
            dig_obj_instance = {'instance_type':'digital_object', 'digital_object':{'ref':dig_obj_uri}}

            # Append the new instance to the existing archival object record's instances
            archival_object_json['instances'].append(dig_obj_instance)
            archival_object_data = json.dumps(archival_object_json)

            # Repost the archival object
            archival_object_update = requests.post(aspace_url+archival_object_uri,headers=headers,data=archival_object_data).json()

            #print 'Archival Object Status: ' + archival_object_update['status']

            # Write a new csv with all the info from the initial csv + the ArchivesSpace uris for the archival and digital objects
            with open(updated_archival_object_csv,'w') as csvout:
                writer = csv.writer(csvout)
                writer.writerow(row)

            #print a new line for readability in console
            print('\n')
