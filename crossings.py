# Test file for crossing scraping functionality
from cbp_scraper import get_port_crossings

sample_portList = '/about/contact/ports/miami-international-airport-florida-5206'

port = get_port_crossings(sample_portList, "5206")
print("Test completed")
