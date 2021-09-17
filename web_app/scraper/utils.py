import os.path

def is_empty(list):
	return len(list) < 1

def remove_duplicates(list_of_duplicates):
	return list(dict.fromkeys(list_of_duplicates))

def make_folder(path):

	if not os.path.isdir(path):
		os.mkdir(path)