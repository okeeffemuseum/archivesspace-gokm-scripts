import json
import requests
import time
import csv
import getpass



#Source of the majority of this file is from MIT getArchivalObjectRefIdsForResource script
#https://github.com/MITLibraries/archivesspace-api-python-scripts/blob/ba64b04d901698c0f564a49abd49ed9c6368c2c3/getArchivalObjectRefIdsForResource.py
#12/30/2021 Copied and modified by L.Neely
#Tested and known working
#documented in the CIM handbook ArchivesSpace API folder api_get_RefIDs_URIs_by_Resource.docX
#Output could be finessed (How could get the number instead of full URI path)

#AUTHENTICATION STUFF:
baseURL = 'http://archivesspace:8089'
#Prompt for backend URL ( e.g. http://localhost:8089) and login credentials
aspace_url = baseURL #input('ASpace backend URL: ')
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

startTime = time.time()


def findKey(d, key):
    """Find all instances of key."""
    if key in d:
        yield d[key]
    for k in d:
        if isinstance(d[k], list) and k == 'children':
            for i in d[k]:
                for j in findKey(i, key):
                    yield j


repository = '2'

session = auth['session']
headers = {'X-ArchivesSpace-Session': session,
           'Content_Type': 'application/json'}

resourceID = input('Enter resource ID: ')
csvfile = input('Please enter the filename for the output CSV, make sure to add a .csv extension: ')

f = csv.writer(open (csvfile, 'w', newline='', encoding='utf-8'))
f.writerow(['title'] + ['uri'] + ['ref_id'])

endpoint = '/repositories/' + repository + '/resources/' + resourceID + '/tree'

output = requests.get(baseURL + endpoint, headers=headers).json()
archivalObjects = []
for value in findKey(output, 'record_uri'):
    print(value)
    if 'archival_objects' in value:
        archivalObjects.append(value)

print('downloading aos')
for archivalObject in archivalObjects:
    output = requests.get(baseURL + archivalObject, headers=headers).json()
    print(json.dumps(output))
    title = output['title']
    uri = output['uri']
    ref_id = output['ref_id']
    f.writerow([title] + [uri] + [ref_id])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))