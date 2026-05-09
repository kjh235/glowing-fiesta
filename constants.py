CBP_SITE = 'https://www.cbp.gov'
FIRMS_LIST_URL = 'https://www.cbp.gov/sites/default/files/assets/documents/2023-Jan/FIRMS30%20.TXT'

PORT_BASE_URL = 'https://www.cbp.gov/about/contact/ports/'

REGEX_PATTERNS = {
    'port_format': r'(.*) [\–\-] ([0-9]*)',
    'port_name_format': r'^(.*)\, (.*)$',
    'phone_number': r'Phone',
    'fax_number': r'Fax',
    'hours_search': r'Hours',
    'phone_format': r'((\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4})\'?',
    'hours_format': r':\s+(.*)',
    'address_format': r'(Address:)\s+(.*)\s+(.*)',
    'address2_format': r'(Address:)\s+(.*)\s+(.*)\s+(.*)',
    'address3_format': r'(Address:)\s+(.*)\s+(.*)\s+(.*)\s+(.*)',
    'citystate_format': r'(.*),\s+([A-Za-z]{2,})\s+(\d{,5})',
    'address1liner_format': r'(.*),\s+(.*),\s+(\w{2})\s+(\d{5})',
    'fac_and_crossing': r'Facilities and Crossings',
    'region_dist_port_format': r'REGION: (\d+)\s+DIST\/PORT: (\d{3,4})',
}

PORTS_CSV_COLUMNS = ["Port Name", "Port Number", "Port URL", "Address Line 1", "Address Line 2",
                     "City", "State", "Postal", "Country", "Assigned Field Office", "Field Office URL"]

CROSSINGS_CSV_COLUMNS = ["Crossing Name", "Port Number", "Address Line 1", "Address Line 2", "City",
                         "State", "Postal", "Country", "Crossing Hours", "Crossing Phone Number"]

FIRMS_CSV_COLUMNS = ['Firm', 'Name', 'AddrLine1', 'City', 'StateCd', 'PostalCd', 'Status', 'Type']

FACILITY_TYPES = {
    "01": "Customs Container Station",
    "02": "Foreign Trade Zone",
    "03": "Pier",
    "04": "Bonded Warehouse",
    "05": "Inspection Facility",
    "06": "Importer Premises",
    "07": "DP Site",
    "08": "Custom Admin Site"
}

FIRMS_COLSPECS = [(1, 5), (7, 44), (45, 83), (84, 107), (108, 110), (114, 119), (124, 126), (130, 132)]
FIRMS_FILE_WIDTHS = [8, 38, 38, 24, 6, 10, 6, 2]

USPS_COLSPECS = [(0, 1), (1, 9), (10, 11), (11, 38), (39, 96), (97, 124), (125, 127), (127, 136)]
USPS_COLUMN_NAMES = ['DetailCode', 'DropSiteKey', 'DropSiteTypeCode', 'DropSiteName',
                     'DeliveryAddressLine1', 'DeliveryAddressCity', 'DeliveryAddressState',
                     'DeliveryAddressPostal']
