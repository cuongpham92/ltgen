#! usr/bin/python
# -*- coding: ISO-8859-1 -*-

# Function for writing file
def write_file(config_file, mode, context):
	with open(config_file, mode, encoding='utf-8') as f:
		f.write(context)

# Function for reading file
def read_file(file_name):
    new_list = []
    with open(file_name, 'r') as file:
        for line in file:
            if ("#" not in line):
                line=line.replace('\n','')
                new_list.append(line)
    return new_list

def read_file_2(file_name):
	content = ""
	with open(file_name, 'r', encoding='utf-8') as file:
		content = file.read()
	return content
