import os.path

def is_empty(list):
	return len(list) < 1

def remove_duplicates(list_of_duplicates):
	return list(dict.fromkeys(list_of_duplicates))

def make_folder(path):

	if not os.path.isdir(path):
		os.mkdir(path)

def timeit(orig_func):
	import time

	def wrapper(*args, **kwargs):
		t1 = time.perf_counter()

		return_val = orig_func(*args, **kwargs)

		t2 = time.perf_counter()

		print(f"FUNCTION {orig_func.__name__} RAN IN {t2 - t1}s.")

		return return_val

	return wrapper

