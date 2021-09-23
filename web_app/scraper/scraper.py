
"""
Scraper is a base class, which object's task is to gather emails and phones with provided queries. 

"""

import urllib.request, os.path, csv, re, googlesearch
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup

from typing import List, Callable, Tuple

from utils import *

path_of_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")

class Scraper():

	"""

	

	"""


	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0',
				'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
       			'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       			'Accept-Encoding': 'none',
       			'Accept-Language': 'pl-PL,pl;q=0.8'}


	def __init__(self, query, num_links, region, path, mail_regex, phone_regex, write_error_file=False):
		self.query = query
		self.num_links = num_links
		self.region = region
		self.path = path
		self.mail_regex = mail_regex
		self.phone_regex = phone_regex
		self.write_error_file = write_error_file
		self.error_log = ""
		self.id = id(self)

	#TODO: use requests not urllib.request
	# def get_html_from_url(self, url: str, debug=False) -> str:

	# 	req = urllib.request.Request(url, headers=Scraper.headers)

	# 	try:
	# 		with urllib.request.urlopen(req, timeout=10) as google_binary:
	# 			html = google_binary.read().decode('utf-8')
	# 			return html

	# 	except Exception as e:
	# 		if debug:
	# 			print(e)

	# 		self.error_log += f"Site {url} threw {str(e)}\n"

	# 		return "" 

	def get_html_from_url(self, url: str, debug=False) -> str:

		try:

			with requests.Session() as session:

				req = session.request('GET', url, headers=Scraper.headers, timeout=10)
				html = req.text
				return html

		except requests.RequestException as e:
			if debug:
				print(e)

			self.error_log += f"Site {url} threw {str(e)}\n"

			return ""

	def get_links(self, search_string: str, number_of_search_results: int, sites_to_ignore: Tuple[str]) -> List[str]:

		"""
		Search google and retrieve URL's.

		"""

		return [link for link in googlesearch.search(search_string,
								tld="pl",
								lang="pl",
								num=number_of_search_results,
								pause=2.0,
								stop=number_of_search_results,
								user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0'
								) if not any(x in link for x in sites_to_ignore)]


	#TODO: provide phone regex and mail regex
	#TODO: provide a programatically created dictionary of tried/untried custom search functions
	#TODO: provide a protocol for that functions - what they have to have and what they have to return
	def parse_site(self, soup: BeautifulSoup, url: str, *search_funcs):

		mail_pattern = re.compile(self.mail_regex)
		phone_pattern = re.compile(self.phone_regex)

		options = {"search_through_a_tag": False}

		functions = {"search_through_a_tag": self.search_through_a_tag_func}

		html_document = soup.prettify()

		first_url = url

		emails = mail_pattern.findall(html_document)
		phones = phone_pattern.findall(html_document)

		email_protection = False

		if self.parse_result(is_empty(emails), is_empty(phones), options) == "trying":

			for option, was_used in options.items():

				if self.parse_result(is_empty(emails), is_empty(phones), options) == "trying":

					new_soup, new_url = self.use_option(was_used, functions[option], url, soup)

					if new_soup is not None:

						if not email_protection:
							email_protection = self.check_for_email_protection(new_soup)

						options[option] = True
						url = new_url
						soup = new_soup
						emails = mail_pattern.findall(new_soup.prettify())
						phones = phone_pattern.findall(new_soup.prettify())

				else:
					break

		if email_protection:
			emails = ["Protected"]

		return {'emails': remove_duplicates(emails), 'phones': remove_duplicates(phones), 'url': first_url}

	def use_option(self, option: bool, func: Callable, url: str, soup: BeautifulSoup):

		# all functions return new search

		if not option:
			new_soup, new_url = func(url, soup)
			return new_soup, new_url
		else:
			return None

	def check_for_email_protection(self, soup: BeautifulSoup):

		for a_tag in soup.find_all('a'):
			href = a_tag.get('href')

			if href is not None and "email-protection" in href: return True

		return False

	# TODO: TUPLE KEYWORDS
	def search_through_a_tag_func(self, url, soup):#, keywords):

		try:
			for a_tag in soup.find_all('a'):
				href = a_tag.get('href')
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

	def parse_result(self, is_emails_empty, is_phones_empty, dict_of_options):


		"""TODO: enum instead of strings"""

		if (is_emails_empty or is_phones_empty) and (all(dict_of_options.values()) is False):
			return "trying"

		else:
			if (is_phones_empty or is_emails_empty) and all(dict_of_options.values()):
				return "got_some"

			elif (not is_phones_empty and not is_emails_empty):
				return "got_all"


	def parse_through_sites(self, site_list, debug=False):

		data_list = []

		for site in site_list:
			if debug:
				print(site)

			site_html = self.get_html_from_url(site)
			if site_html is not None:
				site_soup = BeautifulSoup(site_html, 'html.parser')
				data_list.append(self.parse_site(site_soup, site))

		return data_list

	def write_to_csv(self, data, search_name, number_of_links, debug=False):

		phones_unfound = 0
		emails_unfound = 0

		name = f"results of +{search_name}+"

		with open(os.path.join(self.path, f"{name}.csv"), mode='w', newline='') as csv_file:

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
					if "\xa0" in number:
						phones.remove(number)

				writer.writerow({'site': url, 'emails': emails, 'phones': phones})

		if debug:
			print(f"Emails unfound: {emails_unfound}/{number_of_links}\nPhones unfound: {phones_unfound}/{number_of_links}")

	def scrape(self):

		headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0',
				'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
       			'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       			'Accept-Encoding': 'none',
       			'Accept-Language': 'pl-PL,pl;q=0.8'}

		city = "kraków"

		unqouted_search = f"{self.query} {city}"

		links = self.get_links(unqouted_search, self.num_links, ("youtube", "facebook", "olx", "allegro", "sprzedajemy", "gumtree", "ceneo", "instagram"))

		print("Finding emails and phones...")
		data = self.parse_through_sites(links)

		print("Writing file...")
		make_folder(self.path)
		self.write_to_csv(data, unqouted_search, self.num_links)

		print("File written.")

	def write_error_file(self):
		with open(os.path.join(self.path, f"error_log{self.id}.txt"), 'a') as error_file:
			error_file.write(error_log)


def main():

	phone_regex = r'\d{3}\s\d{3}\s\d{3}|[+]48\s12\s\d{3}\s\d{3}|012\s\d{3}\s\d{2}\s\d{2}|[+]48\s\d{3}\s\d{3}\s\d{3}|[+]48\s\d{2}\s\d{3}\s\d{2}\s\d{2}|[+]48\s\d{3}-\d{3}-\d{3}|12\s\d{3}\s\d{2}\s\d{2}|[(]\d{2}[)]\s\d{3}\s\d{2}\s\d{2}\s\d{2}|\d{2}-\d{3}-\d{2}-\d{2}|\d{3}-\d{3}-\d{3}'
	mail_regex = r'\b[\w^.]+@\S+[.]\w+[.com|.pl|.eu|.org]+'

	s_one = Scraper("sklep elektroniczny", 10, None, path_of_folder, mail_regex, phone_regex)
	s_one.scrape()

if __name__ == '__main__':
	main()











