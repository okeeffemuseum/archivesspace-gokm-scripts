import csv
import requests
import json
import getpass

def opencsv():
    '''This function opens a csv file'''
    input_csv = input('Please enter path to input CSV: ')
    file = open(input_csv, 'r')
    csvin = csv.reader(file)
    #Skip header row
    next(csvin, None)
    return csvin

def ref_ids_to_field_csv():
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

    as_in_csv = opencsv()

    item_fields_list = []
    
    for row in as_in_csv:
        title = None
        component_id = None 
        date_expression = None
        date_begin = None
        date_end = None
        date_certainty = None
        physical_details = None
        dimensions = None
        agent_1_role = None
        agent_1_relator = None
        agent_1_ref = None
        agent_2_role = None
        agent_2_relator = None
        agent_2_ref = None
        agent_3_role = None
        agent_3_relator = None
        agent_3_ref = None
        agent_4_role = None 
        agent_4_relator = None
        agent_4_ref = None
        subjects = None
        abstract_note = None
        ownership_rights_note = None
        rights_explanation_note = None
        cr_management_note = None
        general_note = None
        rights_statement = None
        digital_objects = None

        ref_id = row[0]
        print('Searching for '+ ref_id)
        params = {"ref_id[]":ref_id}
        lookup = requests.get(aspace_url+'/repositories/2/find_by_id/archival_objects',headers=headers, params=params).json()
        
        # Grab the archival object uri from the search results. It should be the first and only result
        archival_object_uri = lookup['archival_objects'][0]['ref']

        print('Found archival_object: ' + archival_object_uri)
        dict = requests.get(aspace_url+archival_object_uri,headers=headers).json()

        title = dict.get('title')
        component_id = dict.get('component_id')
        date_expression = dict.get('dates')[0].get('expression')
        date_begin = dict.get('dates')[0].get('begin')
        date_end = dict.get('dates')[0].get('end')
        date_certainty = dict.get('dates')[0].get('certainty')
        if 'physical_details' in dict.get('extents'):
            physical_details = dict.get('extents')[0].get('physical_details')
        if 'dimensions' in dict.get('extents'):
            dimensions = dict.get('extents')[0].get('dimensions')
        subjects = dict.get('subjects')
        if 'notes' in dict.get('rights_statements'):
            rights_statement = dict.get('rights_statements')[0].get('notes')[0].get('content')[0]


        # Creating list of digital objects
        instances = dict.get('instances')
        digital_objects = []
        for instance in instances:
            if 'digital_object' in instance:
                digital_objects.append(instance.get('digital_object'))

        # Creating list of linked agents
        linked_agents = dict.get('linked_agents')
        linked_agent_list= [{'role': None, 'relator': None, 'ref': None}, 
                        {'role': None, 'relator': None, 'ref': None}, 
                        {'role': None, 'relator': None, 'ref': None}, 
                        {'role': None, 'relator': None, 'ref': None}, 
                        {'role': None, 'relator': None, 'ref': None}]
        for agent in linked_agents:
            index = linked_agents.index(agent)
            linked_agent_list[index]['role'] = agent.get('role')
            linked_agent_list[index]['relator'] = agent.get('relator')
            linked_agent_list[index]['ref'] = agent.get('ref')

        # Extracting information from notes
        notes = dict.get('notes')

        for note in notes:
            if note.get('type') == 'abstract':
                abstract_note = note.get('content')[0]
            elif note.get('type') == 'odd':
                general_note = note.get('subnotes')[0].get('content')
            elif note.get('label') == 'Copyright Management':
                cr_management_note = note.get('subnotes')[0].get('content')
            elif note.get('label') == 'Ownership and Rights':
                ownership_rights_note = note.get('subnotes')[0].get('content')
            elif note.get('label') == 'Explanation of Rights':
                rights_explanation_note = note.get('subnotes')[0].get('content')

        item_fields_list.append({'ref_id': ref_id, 'title': title, 'component_id': component_id, 'date_expression': date_expression, 'date_begin': date_begin, 'date_end': date_end,
                        'date_certainty': date_certainty, 'physical_details': physical_details, 'dimensions': dimensions, 'agent_1_role': linked_agent_list[0].get('role'),
                        'agent_1_relator': linked_agent_list[0].get('relator'), 'agent_1_ref': linked_agent_list[0].get('ref'), 'agent_2_role': linked_agent_list[1].get('role'), 'agent_2_relator': linked_agent_list[1].get('relator'),
                        'agent_2_ref': linked_agent_list[1].get('ref'), 'agent_3_role': linked_agent_list[2].get('role'), 'agent_3_relator': linked_agent_list[2].get('relator'), 'agent_3_ref': linked_agent_list[2].get('ref'),
                        'agent_4_role': linked_agent_list[3].get('role'), 'agent_4_relator': linked_agent_list[3].get('relator'), 'agent_4_ref': linked_agent_list[3].get('ref'), 'subjects': subjects, 'abstract_note': abstract_note,
                        'ownership_rights_note': ownership_rights_note, 'rights_explanation_note': rights_explanation_note, 'cr_management_note': cr_management_note,
                        'general_note': general_note, 'rights_statement': rights_statement, 'digital_objects': digital_objects})
    
    return item_fields_list

def save(csv_list, csv_filename, csv_fields):
    # Write field info to csv
    with open(csv_filename, 'w') as csvfile:
        # creating a csv dict writer object 
        writer = csv.DictWriter(csvfile, fieldnames = csv_fields) 
    
        # writing headers (field names) 
        writer.writeheader() 
    
        # writing data rows 
        writer.writerows(csv_list)

# CSV fields
fields = ['ref_id', 'title', 'component_id', 'date_expression', 'date_begin', 'date_end',
                'date_certainty', 'physical_details', 'dimensions', 'agent_1_role',
                'agent_1_relator', 'agent_1_ref', 'agent_2_role', 'agent_2_relator',
                'agent_2_ref', 'agent_3_role', 'agent_3_relator', 'agent_3_ref',
                'agent_4_role', 'agent_4_relator', 'agent_4_ref', 'subjects', 'abstract_note',
                'ownership_rights_note', 'rights_explanation_note', 'cr_management_note',
                'general_note', 'rights_statement', 'digital_objects']

item_fields_list = ref_ids_to_field_csv()
save(item_fields_list, '/Users/rchan/Desktop/mfah_scripts/test_spreadsheet.csv', fields)
