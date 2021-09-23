from dataclasses import dataclass

@dataclass
class RegionData:
	"""Class that stores information about region-specific data about contacts"""

	accept_language_header: str
	tld: str
	lang: str
	contact_keywords: str
	cities: list[str]
	