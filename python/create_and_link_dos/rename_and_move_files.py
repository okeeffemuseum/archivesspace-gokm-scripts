import os
import shutil

file_prefix = input("File prefix (e.g. 2018-11-01_MS.9): ") 
path = input("Path to folder with import files: ")

try: 
	os.rename('AS_in.csv', file_prefix + '_AS_in.csv')
	os.rename('AS_in.xml', file_prefix + '_AS_in.xml')
	os.rename('DAM_in.csv', file_prefix + '_DAM_in.csv')
	os.rename('linked_DAM_AS.csv', file_prefix + '_linked_DAM_AS.csv')
	os.rename('updated_AO_DO_report.csv', file_prefix + '_updated_AO_DO_report.csv')
except BaseException as exp: 
	print("Expected file not found")

destination = path + "/old_imports/" + file_prefix

try:  
    os.mkdir(destination)
except OSError:  
    print ("Creation of the directory %s failed" % destination)
else:  
    print ("Successfully created the directory %s " % destination)

for i in os.listdir(path):
    if os.path.isfile(os.path.join(path,i)) and file_prefix in i:
        shutil.move(i, destination)

print("File renaming and moving successful")