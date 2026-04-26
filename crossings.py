from bs4 import BeautifulSoup
from requests import get
import re
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from main import get_port_crossings

facAndCrossing = r'Facilities and Crossings'
phoneNumber = r'Phone Number:'
faxNumber = r'Fax'
phone_format = r'((\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4})\'?'
hours_format = r'(Hours of Operation[s]?:)\s+(.*)'
address_format = r'(Address:)\s+(.*)\s+(.*)'
address2_format = r'(Address:)\s+(.*)\s+(.*)\s+(.*)'
citystate_format = r'(.*),\s([A-Z]{2})\s(\d{,5})'
hoursSearch = r'Hours'

sample_portList = '/about/contact/ports/miami-international-airport-florida-5206'


port = get_port_crossings(sample_portList, 5206)





print("hello")