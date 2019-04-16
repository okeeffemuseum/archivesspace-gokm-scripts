import os

print('Turning ASpace EAD into a CSV file')
os.system (r"python ead_to_csv\.py")
print('ASpace CSV created')

print('Mapping AOs to DOs')
os.system (r"python map_ao_to_do\.py")
print('Mapping completed')

print("Creating and linking AOs to DOs in ASpace")
os.system (r"python create_and_link_do\.py")
print('Linking completed')

print('Renaming all csv and xml files and moving them to the \"old_imports\" file')
os.system (r"python rename_and_move_files\.py")
print('\nProcess completed')