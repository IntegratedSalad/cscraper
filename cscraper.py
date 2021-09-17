"""
This module provides basic functionality of scraping, retrieving and saving contact data (email addressess and phone numbers) from
a user provided query.

The usual execution proceeds as follows:

1. User inputs a query,
2. URL's are retrieved from google's search results,
3. These sites are then parsed for e-mails and phones.


"""

import urllib.request, os.path, csv, re, googlesearch
from urllib.parse import quote
from bs4 import BeautifulSoup
import argparse

from typing import List, Callable

# add this to a new file - cmdcscrape - cscraper.py should be just a module of functions
# write a class.

def get_html_from_url(url: str, debug=False) -> str:

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
		if debug:
			print(e)
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
			return f"!E: {str(e)}\n{url}"

def simple_get_links(search_string: str, number_of_search_results: int) -> List[str]:

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
								) if not ("youtube" in link or "facebook" in link or "olx" in link or "allegro" in link or "sprzedajemy" in link or "gumtree" in link)] # here add exceptions in list or in file

def parse_site(soup: BeautifulSoup, url: str):

	phone_regex = r'\d{3}\s\d{3}\s\d{3}|[+]48\s12\s\d{3}\s\d{3}|012\s\d{3}\s\d{2}\s\d{2}|[+]48\s\d{3}\s\d{3}\s\d{3}|[+]48\s\d{2}\s\d{3}\s\d{2}\s\d{2}|[+]48\s\d{3}-\d{3}-\d{3}|12\s\d{3}\s\d{2}\s\d{2}|[(]\d{2}[)]\s\d{3}\s\d{2}\s\d{2}\s\d{2}|\d{2}-\d{3}-\d{2}-\d{2}|\d{3}-\d{3}-\d{3}'
	mail_regex = r'\b[\w^.]+@\S+[.]\w+[.com|.pl|.eu|.org]+'

	mail_pattern = re.compile(mail_regex)
	phone_pattern = re.compile(phone_regex)

	""" Pass search functions as *args, and make dict programatically.  """

	options = { # this dict is redundant, for loop assures that it will try only once for each option.

			"search_through_a_tag": False,

			}

	functions = { # make this as a list, not dict

			"search_through_a_tag": search_through_a_tag_func,

			}


	html_document = soup.prettify() # it might be slow, because of searching through the whole html document - maybe reduce that to only "a" tags.

	first_url = url

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

	return {'emails': remove_duplicates(emails), 'phones': remove_duplicates(phones), 'url': first_url}


def is_empty(list):
	return len(list) < 1


def use_option(option: bool, func: Callable, url: str, soup: BeautifulSoup):
	# all functions return new search
	if not option: # if it's false - not used yet
		new_soup, new_url = func(url, soup)
		return new_soup, new_url
	else:
		return None

def check_for_email_protection(soup: BeautifulSoup):

	for a_tag in soup.find_all('a'):
		href = a_tag.get('href')

		if href is not None and "email-protection" in href: return True

	return False


def search_through_a_tag_func(url, soup):

	"""
	This function searches for "kontakt" or "contact" site.
	"""

	# TODO:
	# catch exceptions - test on various sites

	try:
		for a_tag in soup.find_all('a'):
			href = a_tag.get('href')
			if href is not None:
				if "email-protection" in a_tag.get('href'):
					return None, ""

				if ("kontakt" in href) or ("contact" in href):
					if href[0] and href[1] == "/": # prevent from entering links from "//"
						return BeautifulSoup(get_html_from_url("http://" + a_tag.get('href')[2:]), 'html.parser'), href
					else:
						return BeautifulSoup(get_html_from_url(a_tag.get('href')), 'html.parser'), href

	except ValueError: # link may be not full, only an extension from slash.
		new_link = url + "/" + href

		return BeautifulSoup(get_html_from_url(new_link), 'html.parser'), new_link

	return None, ""


def parse_result(is_emails_empty, is_phones_empty, dict_of_options):

	"""
	Control the result of parsing html document, in search for emails and phones.

	:param bool is_emails_empty: takes the boolean value of check if the list containing emails is not empty (lesser than 1)
	:param bool is_phones_empty: takes the boolean value of check if the list containing phones is not empty (lesser than 1)
	:param dict dict_of_options: dictionary of options that are used to find emails and phones
	:return: result string
	:rtype: str

	"""


	''' Basically - try every option if there are still options. '''
 
	if (is_emails_empty or is_phones_empty) and (all(dict_of_options.values()) is False): # if there are no emails or no values and there are still options
		return "trying"
	else:
		if (is_phones_empty or is_emails_empty) and all(dict_of_options.values()): # if there are no emails or no values and there are no options left
			return "got_some"
		
		elif (not is_phones_empty and not is_emails_empty):
			return "got_all"
	

def remove_duplicates(list_of_duplicates):
	return list(dict.fromkeys(list_of_duplicates))

def save_search_results(link_list, path_of_folder):
	with open(path_of_folder + "SearchResults.txt", 'w') as file:
		for x in link_list:
			file.write(x)
			file.write("\n")

def parse_through_sites(site_list, debug=False):

	data_list = []
	counter = 0

	for site in site_list:
		if debug: 
			print(site)
		site_html = get_html_from_url(site)
		if site_html is not None:
			site_soup = BeautifulSoup(site_html, 'html.parser')
			data_list.append(parse_site(site_soup, site))

	return data_list

def make_folder(path_of_folder):

	if not os.path.isdir(path_of_folder):
		os.mkdir(path_of_folder)

def write_info_txt(data, search_name, number_of_links, path_of_folder):

	phones_unfound = 0
	emails_unfound = 0

	if extension == ".txt":
		with open(os.path.join(path_of_folder, "results.txt"), 'w') as file:
			for dc in data:
				emails = dc['emails']
				phones = dc['phones']
				url = dc['url']

				if (emails and phones) != []: 
					file.write("Emails | Phones from {0}: {1} | {2}".format(url, emails, phones))
					file.write("\n")


def write_to_csv(data, search_name, number_of_links, path_of_folder, debug=True):

	phones_unfound = 0
	emails_unfound = 0

	name = f"results of +{search_name}+"
	with open(os.path.join(path_of_folder, f"{name}.csv"), mode='w', newline='') as csv_file:
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

	if debug:
		print(f"Emails unfound: {emails_unfound}/{number_of_links}\nPhones unfound: {phones_unfound}/{number_of_links}")


def write_debug_data(data, search_name, path_of_folder, extension=".csv"):

	print("DATA:")
	for d in data.values():
		print(remove_duplicates(d))

	if extension == ".csv":
		name = "results of +{0}+".format(search_name)
		with open(os.path.join(path_of_folder, name, ".csv"), mode='w', newline='') as csv_file:
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
