import cscraper, time, os, argparse

path_of_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")

parser = argparse.ArgumentParser(description="Parse sites for contact data - emails and phones.")
parser.add_argument('-q', '--query', help="provide a search query.") # make possible providing multiple queries.
parser.add_argument('-d', '--debug', help="display additional information.", action="store_true")
parser.add_argument('-n', '--num', help="provide a number of searches (defaults to 30).", type=int)

def main():

	args = parser.parse_args()
	city = "kraków"

	unquoted_search = "{0} {1}".format(args.query, city)

	if args.num is not None:
		links_num = args.num
	else:
		links_num = 30

	links = cscraper.simple_get_links(unquoted_search, links_num)

	print("Finding emails and phones...")

	data = cscraper.parse_through_sites(links)

	print("Writing file...")

	cscraper.make_folder(path_of_folder)
	cscraper.write_to_csv(data, unquoted_search, args.num, path_of_folder)

	print("File written.")

	time.sleep(3)

def debug_search_parse_write():

	search = "agencje reklamowe kraków"

	number_of_links = 70

	links = simple_get_links(search, number_of_links)

	print("Finding emails and phones...")
	data = parse_through_sites(links)
	print("Writing file...")
	make_folder()
	write_data(data, search, number_of_links)
	print("File written.")


if __name__ == '__main__':
	main()
