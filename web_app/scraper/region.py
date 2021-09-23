from dataclasses import dataclass
from typing import Tuple

@dataclass
class RegionData:
	"""Class that stores information about region-specific data about contacts"""

	accept_language_header: str
	accept_encoding_header: str
	tld: str
	lang: str
	contact_keywords: Tuple[str]
	city: str # for now only one city
