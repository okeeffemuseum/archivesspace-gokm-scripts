'''
	Author: Rana Chan
	Date created: 7/16/2019
	Date last modified: 7/23/2019
	Python Version: 3.7
'''

from bs4 import BeautifulSoup as Soup
import pdb
import csv

# This script was written to take ref ids and titles of archival object photos from
# an ArchivesSpace EAD and assign subject ids of subjects that are depicted in the photographs 
# to the ref ids. The output is a two column CSV (no header) that contains the following:
# Column 1: ref id of archival object
# Column 2: subject id of subject depicted in archival object

# Create a nested dictionary of subject records where the key is the subject record id
def create_subject_dict():
    subject_dict = dict()

    # Adding depicted subjects with subject records
    subject_dict[16] = {'name':'Georgia O\'Keeffe', 'excluded_text': {'Georgia O\'Keeffe\'s', 'by Georgia O\'Keeffe', 'Georgia O\'Keeffe Exhibition', 'of Georgia O\'Keeffe'}}
    subject_dict[19] = {'name':'Alfred Stieglitz', 'excluded_text': {'Possibly Alfred Stieglitz'}}
    subject_dict[187] = {'name':'Carl Van Vechten', 'excluded_text': {'Carl Van Vechten gallery'}}
    subject_dict[104] = {'name':'Todd Webb', 'excluded_text':{'%'}}
    subject_dict[111] = {'name':'Helen Woodruff', 'excluded_text':{'%'}}

    return subject_dict

# Create a dictionary of archival objects where the key is the ref id and the value is the title
def create_aspace_dict_from_ead(aspace_xml):
    aspace_dict = dict()

    with open(aspace_xml) as filepath:
        soup = Soup(filepath, "xml", from_encoding="utf-8")


    soup_records = soup.find_all('c', level="item")
    number_of_records = len(soup_records)

    for index, record in enumerate(soup_records):   
        # find ref id
        ref_id = soup_records[index]['id'][7:]
        
        # get title
        for title_field in record.find_all('unittitle'):
            title = title_field.get_text()

        # if record is a photograph, add to dictionary
        if record.find_all('container', label = "photographs"):
            aspace_dict[ref_id] = title

    return aspace_dict

# Check for false positives that a subject is depicted in a photo
def excluded_text_not_in_title(title, excluded_text_list):
    for word in excluded_text_list:
        if word in title:
            return False

    return True

# Create a dictionary of archival objects and their depicted subjects where the key is the ref id of the archival object
def create_archival_object_subject_dict(subject_dictionary, aspace_dictionary):
    ao_subject_dict = dict()

    for ref_id,title in aspace_dictionary.items():
        for key,value in subject_dictionary.items():
            if value.get('name') in title and excluded_text_not_in_title(title, value.get('excluded_text')):
                if ref_id in ao_subject_dict:
                    ao_subject_dict.get(ref_id).append(key)
                else:
                    ao_subject_dict[ref_id] = [key]

    return ao_subject_dict

def main():
    #pdb.set_trace()

    aspace_dict = create_aspace_dict_from_ead('MS.37_20190723_190858_UTC__ead.xml')
    subject_dict = create_subject_dict()

    linked_dict = create_archival_object_subject_dict(subject_dict, aspace_dict)

    with open('depicted_subjects_update.csv', 'w') as f:
        for key,value in linked_dict.items():
            for elem in value:
                f.write("%s,%s\n"%(key,elem))


if __name__ == '__main__': main()

