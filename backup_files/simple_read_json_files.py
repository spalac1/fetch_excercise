import gzip
import json
import csv

all_files = ['brands.json.gz','receipts.json.gz','users.json.gz']

# Loop through each of our files
for file in all_files:
    # open gzip file to read content
    with gzip.GzipFile(file, 'rb') as infile:
        file_content = infile.read().decode('utf-8')
    
    # Parse out multiple json objects (i.e. each line looks like new json object)
    # all_objs = file_content.split_lines()
    all_objs = file_content.split("\n")

    
    with open(file.split('.')[0]+'_new.json', 'w', newline='') as fout:       # 4. fewer bytes (i.e. gzip)
        # loop through all objects to pull json data for each line
        for json_obj in all_objs:
            try:
                new_content = json.loads(json_obj)
                json.dump(new_content, fout, indent = 4)
            except:
                print('Error writing json objects')

