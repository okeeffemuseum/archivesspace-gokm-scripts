# -*- coding: utf-8 -*-
"""
Authors: Colton and Rana
(And https://www.geeksforgeeks.org/xml-parsing-python/)
"""
import csv
import xml.etree.ElementTree as ET
xmlfile = input('Please enter path to input CSV: ')



def save(refid_component_array, csv_file_name): 
  
    # specifying the fields for csv file 
    fields = ['refid', 'component_id', 'title'] 
  
    # writing to csv file 
    with open(csv_file_name, 'w') as csvfile: 
  
        # creating a csv dict writer object 
        writer = csv.DictWriter(csvfile, fieldnames = fields) 
  
        # writing headers (field names) 
        writer.writeheader() 
  
        # writing data rows 
        writer.writerows(refid_component_array)


tree = ET.parse(xmlfile)
root = tree.getroot() 
refid_components = []

#get archival objects (item level) stored in series
#make sure to put {urn:isbn:1-931666-22-9} (aka uniform resource name) in front of all tags
filechildren = root.findall("./{urn:isbn:1-931666-22-9}archdesc/{urn:isbn:1-931666-22-9}dsc/{urn:isbn:1-931666-22-9}c[@level = 'item']")

for filechild in filechildren:
    ref_id = filechild.attrib['id'][7:]
    component_id = filechild.findall('./{urn:isbn:1-931666-22-9}did/{urn:isbn:1-931666-22-9}unitid')[0].text
    title = filechild.findall('./{urn:isbn:1-931666-22-9}did/{urn:isbn:1-931666-22-9}unittitle')[0].text
    refid_components.append({"refid":ref_id, "component_id":component_id, "title":title})

#get archival objects not stored in files
# children = root.findall("./{urn:isbn:1-931666-22-9}archdesc/{urn:isbn:1-931666-22-9}dsc/{urn:isbn:1-931666-22-9}c/{urn:isbn:1-931666-22-9}c[@level='item']")

# for child in children:
#     ref_id = child.attrib['id'][7:]
#     component_id = child.findall('./{urn:isbn:1-931666-22-9}did/{urn:isbn:1-931666-22-9}unitid')[0].text
#     title = child.findall('./{urn:isbn:1-931666-22-9}did/{urn:isbn:1-931666-22-9}unittitle')[0].text
#     refid_components.append({"refid":ref_id, "component_id":component_id, "title":title})

    
save(refid_components, "AS_in.csv")