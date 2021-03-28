import urllib.request, os.path, csv, re, googlesearch, time
from urllib.parse import quote
from bs4 import BeautifulSoup
import time

city = "kraków" # dmake that optional
path_of_folder = os.path.dirname(os.path.realpath(__file__)) + '/data/'


class Crawler:

	"""
	Each crawler focuses on one query, gathering data from sites that it yields.

	"""

	def __init__(self, query, search_results_number):
		self.query = query
		self.search_results_number = search_results_number
		self.sites = []
		self.data = None

	def create_data_dict(self):
		self.data = dict.fromkeys(self.sites)

	def get_links(self):
		self.sites = [link for link in googlesearch.search(self.query,
								# tld="pl",
								lang="pl",
								num=self.search_results_number,
								pause=2.0,
								stop=self.search_results_number,
								user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0'
								) if not ("youtube" in link or "facebook" in link or "olx" in link or "allegro" in link or "sprzedajemy" in link or "gumtree" in link)]

	def parse_through_sites(self):

		for site in self.sites:
			print(site)
			site_html = self.get_html_from_url(site)
			if site_html is not None:
				site_soup = BeautifulSoup(site_html, 'html.parser')

				self.data[site] = self.parse_site(site_soup, site)


	def get_html_from_url(self, url):

		headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0',
					'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
	       			'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	       			'Accept-Encoding': 'none',
	       			'Accept-Language': 'pl-PL,pl;q=0.8'}

		req = urllib.request.Request(url, headers=headers)

		try:
			with urllib.request.urlopen(req, timeout=10) as google_binary:
				html = google_binary.read().decode('utf-8')
				return html
		except Exception as e:
			if "404" in str(e):
				return "404"
			elif "403" in str(e):
				pass
			elif "400" in str(e):
				pass
			elif "429" in str(e):
				pass
			elif "utf" in str(e):
				pass
			elif "timed" in str(e):
				pass
			elif "certificate" in str(e):
				pass
			elif "999" in str(e):
				pass
			elif "500" in str(e):
				return ""
			else:
				with open(path_of_folder + "crash.txt", 'w') as file:
					file.write(str(e))
					file.write("\n")
					file.write(url)
					file.close()
				#print("Something went wrong:")
				#print(str(e))
				#print(url)
				exit(0)

	def parse_site(self, soup, url):

		phone_regex = r'\d{3}\s\d{3}\s\d{3}|[+]48\s12\s\d{3}\s\d{3}|012\s\d{3}\s\d{2}\s\d{2}|[+]48\s\d{3}\s\d{3}\s\d{3}|[+]48\s\d{2}\s\d{3}\s\d{2}\s\d{2}|[+]48\s\d{3}-\d{3}-\d{3}|12\s\d{3}\s\d{2}\s\d{2}|[(]\d{2}[)]\s\d{3}\s\d{2}\s\d{2}\s\d{2}|\d{2}-\d{3}-\d{2}-\d{2}|\d{3}-\d{3}-\d{3}'
		mail_regex = r'\b[\w^.]+@\S+[.]\w+[.com|.pl|.eu|.org]+'

		mail_pattern = re.compile(mail_regex)
		phone_pattern = re.compile(phone_regex)

		options = { # this dict is redundant, for loop assures that it will try only once for each option.

				"search_through_a_tag": False,

				}

		functions = { # make this as a list, not dict

				"search_through_a_tag": self.search_through_a_tag_func,

				}


		html_document = soup.prettify() # it might be slow, because of searching through the whole html document - maybe reduce that to only "a" tags.

		first_url = url

		#print(html_document)

		emails = mail_pattern.findall(html_document) 	# first try
		phones = phone_pattern.findall(html_document)	# first try

		email_protection = False

		if parse_result(is_empty(emails), is_empty(phones), options) == "trying":

			for option, was_used in options.items():

				if parse_result(is_empty(emails), is_empty(phones), options) == "trying":

					new_soup, new_url = use_option(was_used, functions[option], url, soup) # all functions must return new_url - if none - ""

					if new_soup is not None:

						if not email_protection:
							email_protection = check_for_email_protection(new_soup)

						options[option] = True
						url = new_url
						soup = new_soup
						emails = mail_pattern.findall(new_soup.prettify())
						phones = phone_pattern.findall(new_soup.prettify())
				else:
					break


		if email_protection:
			emails = ["Protected"]

		return {'emails': self.remove_duplicates(emails), 'phones': self.remove_duplicates(phones), 'url': first_url}


	def search_through_a_tag_func(self, url, soup):

		"""
		This function searches for "kontakt" or "contact" site.
		"""

		# TODO:
		# catch exceptions - test on various sites


		try:
			for a_tag in soup.find_all('a'):
				#print(a_tag)
				href = a_tag.get('href')
				#print(href)
				if href is not None:
					if "email-protection" in a_tag.get('href'):
						return None, ""

					if ("kontakt" in href) or ("contact" in href):
						if href[0] and href[1] == "/": # prevent from entering links from "//"
							return BeautifulSoup(self.get_html_from_url("http://" + a_tag.get('href')[2:]), 'html.parser'), href
						else:
							return BeautifulSoup(self.get_html_from_url(a_tag.get('href')), 'html.parser'), href

		except ValueError: # link may be not full, only an extension from slash.
			new_link = url + "/" + href

			return BeautifulSoup(self.get_html_from_url(new_link), 'html.parser'), new_link

		return None, ""



	def crawl(self):

		start_links = time.perf_counter()
		self.get_links()
		end_links = time.perf_counter() - start_links

		self.create_data_dict()

		start_parse = time.perf_counter()
		self.parse_through_sites()
		end_parse = time.perf_counter() - start_parse

		print(f"Getting links took: {end_links}s\nParsing took: {end_parse}s")



	@staticmethod
	def remove_duplicates(list_of_duplicates):
		return list(dict.fromkeys(list_of_duplicates))


def is_empty(list):
	return len(list) < 1


def use_option(option, func, url, soup):
	# all functions return new search
	if not option: # if it's false - not used yet
		new_soup, new_url = func(url, soup)
		return new_soup, new_url
	else:
		return None

def check_for_email_protection(soup):

	for a_tag in soup.find_all('a'):
		href = a_tag.get('href')

		if href is not None and "email-protection" in href: return True

	return False


def parse_result(is_emails_empty, is_phones_empty, dict_of_options):

	"""
	Control the result of parsing html document, in search for emails and phones.

	:param bool is_emails_empty: takes the boolean value of check if the list containing emails is not empty (lesser than 1)
	:param bool is_phones_empty: takes the boolean value of check if the list containing phones is not empty (lesser than 1)
	:param dict dict_of_options: dictionary of options that are used to find emails and phones
	:return: result string
	:rtype: str
	"""


	# basically - try every option if there are still options.

	if (is_emails_empty or is_phones_empty) and (all(dict_of_options.values()) is False) : # if there are no emails or no values and there are still options
		return "trying"
	else:
		if (is_phones_empty or is_emails_empty) and all(dict_of_options.values()): # if there are no emails or no values and there are no options left
			return "got_some"
		
		elif (not is_phones_empty and not is_emails_empty):
			return "got_all"
	

def save_search_results(link_list):
	with open(path_of_folder + "SearchResults.txt", 'w') as file:
		for x in link_list:
			file.write(x)
			file.write("\n")
		file.close()

def parse_through_sites(site_list):

	data_list = []
	counter = 0

	for site in site_list:
		#time.sleep(1)
		print(site)
		site_html = get_html_from_url(site)
		if site_html is not None:
			site_soup = BeautifulSoup(site_html, 'html.parser')
			data_list.append(parse_site(site_soup, site))

	return data_list

def make_folder():

	if not os.path.isdir(path_of_folder):
		os.mkdir(path_of_folder)

def write_data(data, search_name, number_of_links, extension=".csv"):

	phones_unfound = 0
	emails_unfound = 0

	if extension == ".txt":
		with open(path_of_folder + 'results.txt', 'w') as file:
			for dc in data:
				emails = dc['emails']
				phones = dc['phones']
				url = dc['url']


				if (emails and phones) != []: 
					file.write("Emails | Phones from {0}: {1} | {2}".format(url, emails, phones))
					file.write("\n")

			file.close()

	elif extension == ".csv":
		name = "results of +{0}+".format(search_name)
		with open(path_of_folder + name + ".csv", mode='w', newline='') as csv_file:
			fieldnames = ['site', 'emails', 'phones']
			writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
			writer.writeheader()

			for dc in data:
				emails = dc['emails']
				phones = dc['phones']
				if is_empty(phones):
					phones_unfound += 1
				if is_empty(emails):
					emails_unfound += 1
				url = dc['url']
				for number in phones:
					if "\xa0" in number: # TODO - SOMETIMES NUMBER IS SAVED WITH THIS SYMBOL ONLY, CANNOT DELETE, BECAUSE WE DELETE THE NUMBER!
						phones.remove(number)
				writer.writerow({'site': url, 'emails': emails, 'phones': phones})

			csv_file.close()

	print("Emails unfound: {0}/{1}\nPhones unfound: {2}/{1}".format(emails_unfound, number_of_links, phones_unfound))


def write_debug_data(data, search_name, extension=".csv"):

	print("DATA:")
	for d in data.values():
		print(remove_duplicates(d))

	if extension == ".csv":
		name = "results of +{0}+".format(search_name)
		with open(path_of_folder + name + ".csv", mode='w', newline='') as csv_file:
			fieldnames = ['site', 'emails', 'phones']
			writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
			writer.writeheader()
			emails = data['emails']
			phones = data['phones']
			url = data['url']
			if (emails and phones) != []:
				writer.writerow({'site': url, 'emails': emails, 'phones': phones})
			else:
				writer.writerow({'site': url, 'emails': None, 'phones': None})

		csv_file.close()

def main():

	search = get_search_name()

	quoted_search = "{0}{1}{2}".format(quote(search), quote(" "), quote(city))
	unquoted_search = "{0} {1}".format(search, city)

	links = simple_get_links(unquoted_search, 110)

	print("Finding emails and phones...")

	data = parse_through_sites(links)

	print("Writing file...")

	make_folder()
	write_data(data, unquoted_search)

	print("File written.")

	#save_search_results(links)
	time.sleep(3)


def debug():

	sample_site = "https://hotelkossak.pl/"
	sample_site_html = get_html_from_url(sample_site)

	sample_soup = BeautifulSoup(sample_site_html, 'html.parser')

	data = parse_site(sample_soup, sample_site)

	print(data)

def crawler_debug():
	crawler = Crawler("hotel kraków", 20)
	crawler.crawl()
	# print(crawler.data)


	# 100 links - 6s geeting links, 92s parsing.


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
	#main()
	# help(googlesearch.search)
	crawler_debug()
	#debug_search_parse_write()


# https://python-googlesearch.readthedocs.io/en/latest/

# Scraper 2.0:
#	Poprawiony wyglad danych wyrzucanych ()
#	Multiple searches.
#	Custom number of Google results - np. chce wyszukac pola golfowe, domy weselne i kluby nocne. ()
#	Add exceptions to search. ()
#	E-mail feedback from application ()
#	Add data to search RRRR/MM/DD ()
#	Wyświetlić ile znalazło z ilu wyszukało()
#	Shorten that phone regex by placing 'or" in different places.

