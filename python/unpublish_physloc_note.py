import csv
import requests
import json
import getpass

#Script slightly modified from script provided by Duke Libraries, Alicia Detelich, Yale Manuscripts and ArchivesSpace

#Script reads CSV input with following column: archival_object_ref_ID
#Script unpublishes physical location notes 
#Script will write out log of actions to CSV file (updated_notes.csv) including: 


def opencsv():
    '''This function opens a csv file'''
    input_csv = input('Please enter path to input CSV: ')
    file = open(input_csv, 'r')
    csvin = csv.reader(file)
    #Skip header row
    next(csvin, None)
    return csvin


def delete_note():
    aspace_url = input('Please enter the ArchivesSpace API URL: ')
    username = input('Please enter your username: ')
    password = getpass.getpass(prompt='Please enter your password: ')
    auth = requests.post(aspace_url+'/users/'+username+'/login?password='+password+'&expiring=false').json()
    
    #if session object is returned then login was successful; if not it failed.
    if 'session' in auth:
        session = auth["session"]
        headers = {'X-ArchivesSpace-Session':session}
        print('Login successful! Hello ' + auth["user"]["name"])
    else:
        print('Login failed! Check credentials and try again')
        exit()

    #replaces a note's content in ArchivesSpace using a persistent ID
    csvfile = opencsv()
    spreadsheet = input('Path to output CSV: ')
    print ('Creating a csv')
    writer = csv.writer(open(spreadsheet, 'w'))
    #write a header row
    writer.writerow(["ref_id", "status"])

    for row in csvfile:
        ref_id = row[0]
        print('Searching for '+ ref_id)
        params = {"ref_id[]":ref_id}
        lookup = requests.get(aspace_url+'/repositories/2/find_by_id/archival_objects',headers=headers, params=params).json()
        
        # Grab the archival object uri from the search results. It should be the first and only result
        archival_object_uri = lookup['archival_objects'][0]['ref']

        print('Found archival_object: ' + archival_object_uri)
        archival_object_json = requests.get(aspace_url+archival_object_uri,headers=headers).json()
        for note in archival_object_json['notes']:
            index = archival_object_json['notes'].index(note)
            if note['type'] == 'physloc':
                note['publish'] = False 
                
        archival_object_data = json.dumps(archival_object_json)
        row = []
        row.append(ref_id)
        
        try:
            archival_object_update = requests.post(aspace_url+archival_object_uri,headers=headers,data=archival_object_data).json()
            row.append(archival_object_update['status'])
            print('Archival Object Status: ' + archival_object_update['status'])
        except:
            row.append('FAILURE')
            print('*****FAILURE*****')
            pass
        writer.writerow(row)

delete_note()