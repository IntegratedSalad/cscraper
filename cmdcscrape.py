import cscraper, time


path_of_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")

parser = argparse.ArgumentParser(description="Parse sites for contact data - emails and phones.")
parser.add_argument('-q', '--query', help="provide a search query.") # make possible providing multiple queries
parser.add_argument('-d', '--debug', help="display additional information.", action="store_true")
parser.add_argument('-n', '--num', help="provide a number of searches (defaults to 20).", type=int)
parser.add_argument('-p', '--print', help="print results", action="store_true")


def main():
	args = parser.parse_args()

	# quoted_search = "{0}{1}{2}".format(quote(args.name), quote(" "), quote(city))
	unquoted_search = "{0} {1}".format(args.query, city)

	links = simple_get_links(unquoted_search, 30)

	print("Finding emails and phones...")

	data = parse_through_sites(links)

	print("Writing file...")

	make_folder()
	write_data(data, unquoted_search, 30)

	print("File written.")

	#save_search_results(links)
	time.sleep(3)



def main():

	args = parser.parse_args()

	# quoted_search = "{0}{1}{2}".format(quote(args.name), quote(" "), quote(city))
	unquoted_search = "{0} {1}".format(args.query, city)

	links = simple_get_links(unquoted_search, 30)

	print("Finding emails and phones...")

	data = parse_through_sites(links)

	print("Writing file...")

	make_folder()
	write_data(data, unquoted_search, 30)

	print("File written.")



def debug():

	sample_site = "https://agencjailuzjonistow.pl/?fbclid=IwAR1_xZjY5hQTOKOnm-seHyd24G3arOFQvzPMuyUgU7GtUY0wjnzeQv3t9vA"
	sample_site_html = get_html_from_url(sample_site)

	sample_soup = BeautifulSoup(sample_site_html, 'html.parser')

	data = parse_site(sample_soup, sample_site)

	print(data)


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

