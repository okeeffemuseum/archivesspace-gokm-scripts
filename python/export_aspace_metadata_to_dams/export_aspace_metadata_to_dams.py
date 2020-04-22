# -*- coding: utf-8 -*-
"""
Author: Rana Chan for the Georgia O'Keeffe Museum
Created: 11/27/2019
Last updated: 12/16/2019

PURPOSE: This script takes the required files listed below and creates a .txt file that can be imported into the DAMS to update the metadata
fields of archival object digital surrogates. While the script handles bulk archival object records, it is limited to digital objects
linked to archival objects in a *single collection*. 

REQUIRED FILES (stored in "files_in" folder of this script's directory):
(1) EAD .xml file from ArchivesSpace (script has NOT been tested with EAD3)
(2) Field values .txt file from DAMS

PREREQUISITES: 
The script assumes the following: 
- Archival objects have been created at the item level
- Digital surrogates have been uploaded to the DAMS
- Digital objects have been created in ASpace, with unique IDs pulled from the DAMS assets IDs, and which are linked to their associated archival objects

"""
import csv
import xml.etree.ElementTree as ET
import requests
import json
import os
import getpass


def eadToDict(ead_xml):
    tree = ET.parse(ead_xml)
    root = tree.getroot() 
    ead_dict = dict()
    refid_list = []

    #get collection info and add to ead_dict
    #could make a function for this...
    collection_title = root.find("./{urn:isbn:1-931666-22-9}archdesc/{urn:isbn:1-931666-22-9}did/{urn:isbn:1-931666-22-9}unittitle")
    if collection_title is not None:
        ead_dict['collection_title'] = collection_title.text

    collection_id = root.find("./{urn:isbn:1-931666-22-9}archdesc/{urn:isbn:1-931666-22-9}did/{urn:isbn:1-931666-22-9}unitid")
    if collection_id is not None:
        ead_dict['collection_id'] = collection_id.text

    repository = root.find("./{urn:isbn:1-931666-22-9}archdesc/{urn:isbn:1-931666-22-9}did/{urn:isbn:1-931666-22-9}repository/{urn:isbn:1-931666-22-9}corpname")
    if repository is not None:
        ead_dict['owning_institution'] = repository.text

    abstract = root.find("./{urn:isbn:1-931666-22-9}archdesc/{urn:isbn:1-931666-22-9}did/{urn:isbn:1-931666-22-9}abstract")
    if abstract is not None:
        ead_dict['description'] = abstract.text

    #get archival objects (item level) stored in series
    #make sure to put {urn:isbn:1-931666-22-9} (aka uniform resource name) in front of all tags
    filechildren = root.findall("./{urn:isbn:1-931666-22-9}archdesc/{urn:isbn:1-931666-22-9}dsc/{urn:isbn:1-931666-22-9}c[@id = 'aspace_b19b5a9039eef4403f767bb54df9f608']/{urn:isbn:1-931666-22-9}c/{urn:isbn:1-931666-22-9}c[@level = 'item']")

    for filechild in filechildren:
        ref_id = filechild.attrib['id'][7:]
        refid_list.append(ref_id) 

    ead_dict['refid_list'] = refid_list
    
    return(ead_dict)

def mapMetadataToImportFile(ead_dict, dams_file):
    # Create nested dict for all AOs from ref IDs
    refid_dict = dict()

    #Get metadata from EAD 
    refid_list = ead_dict.get("refid_list")
    collection_title = ead_dict.get('collection_title')
    collection_id = ead_dict.get('collection_id')
    description = ead_dict.get('description')
    owning_institution = ead_dict.get('owning_institution')

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
        print("Hello, you authenticated as: " + auth["user"]["name"]) 

    session = auth["session"]
    headers = {'X-ArchivesSpace-Session':session}

    for ref_id in refid_list:
        print('Processing Ref ID '+ ref_id)
        # Use the find_by_id endpoint (only availble in v1.5+) to  use the ref_ID in the CSV to retrieve the archival object's URI
        params = {"ref_id[]":ref_id}
        lookup = requests.get(aspace_url+'/repositories/2/find_by_id/archival_objects',headers=headers, params=params).json()

        # Grab the archival object uri from the search results
        archival_object_uri = lookup['archival_objects'][0]['ref']
        archival_object_uri_stripped = archival_object_uri.replace('/repositories/2/archival_objects/','')

        # Submit a get request for the archival object and store the JSON
        archival_object_json = requests.get(aspace_url+archival_object_uri,headers=headers).json()

        # Get metadata from JSON
        title = archival_object_json['title']
        creation_date = archival_object_json['dates'][0].get('expression')

        physical_description = archival_object_json['extents'][0].get('physical_details')

        # notes = archival_object_json['notes']
        # for note in notes:
        #     if note.get('type') == 'physdesc':
        #         physical_description = note.get('content')
        #     else: physical_description = ""
        #     # Place holder for rights status note
        #     #if note.get('type') == 'legalstatus'
        #     #    rights_status = note.get('content')

        refid_dict[archival_object_uri_stripped] = {'title': title, 'creation_date': creation_date, 'physical_description': physical_description, 'collection_id': collection_id, 'collection_title': collection_title, 'description': description, 'owning_institution': owning_institution}


    # Convert DAMS txt file to dict
    dams_list_dict = txtFileToListDict(dams_file)

    #from DAMS dict, if asset filename contains "ASAO_"+URI, append metadata IF it exists in AO JSON
    for asset in dams_list_dict:
        # Get AO URI from digital asset filename
        ao_uri_delim = asset.get('Filename').replace('.', '_')
        ao_uri_list = ao_uri_delim.split('_')
        ao_uri = ao_uri_list[1]

        # If filename contains URI, get collections and AO metadata and reassign dict values
        if ao_uri in list(refid_dict.keys()):
            asset['Title'] = refid_dict.get(ao_uri).get('title')
            asset['Creation Date'] = refid_dict.get(ao_uri).get('creation_date')
            asset['Physical Description'] = refid_dict.get(ao_uri).get('physical_description')
            asset['Archives Collection ID'] = refid_dict.get(ao_uri).get('collection_id')
            asset['GOKM Collection'] = refid_dict.get(ao_uri).get('collection_title')
            asset['Description'] = refid_dict.get(ao_uri).get('description')
            asset['Owning Institution'] = refid_dict.get(ao_uri).get('owning_institution')
            #asset['Caption'] = refid_dict.get(ao_uri).get('title')+", "+refid_dict.get(ao_uri).get('creation_date')+". "+refid_dict.get(ao_uri).get('collection_title')+". "+refid_dict.get(ao_uri).get('owning_institution')+"."

    # Write list to txt file to import into the DAMS
    listDictToTxtFile(dams_list_dict)
    print("DAMS import file created")


def txtFileToListDict(text_file):
    txt_list = []
    asset_dict = {}

    with open(text_file) as f:
        lines = list(f)
        header = lines[0]
        header_list = header.split("\t")

        for line in lines[1:]:
            line_list = line.split("\t")
            for item in header_list:
                asset_dict[item] = line_list[header_list.index(item)]
            txt_list.append(asset_dict)
            asset_dict = {}

    return txt_list


def listDictToTxtFile(list_dict):
    header_list = list(list_dict[0].keys())
    tab = "\t"
    header = tab.join(header_list)

    with open("dams_import_file.txt", "w", encoding = "utf-8") as file:
        file.write(header)

        for dict_item in list_dict:
            new_line = ""
            for field in header_list:
                new_line = new_line+str(dict_item.get(field))+tab
            new_line = new_line + "\n"
            file.write(new_line)


def main():

    ead_file = "files_in/"+input("Enter the full filename (including file extension) of the EAD xml file: ") 
    dams_file = "files_in/"+input("Enter the full filename (including file extension) of the DAMS txt file: ")
    
    ead_dict = eadToDict(ead_file)

    mapMetadataToImportFile(ead_dict, dams_file)


if __name__ == '__main__':
    main()