from typing import Optional
from typing import List
from rss_parser import RSSParser
from requests import get  # noqa
from rss_parser.models import XMLBaseModel
from rss_parser.models.rss import RSS
from rss_parser.models.types.tag import Tag
from bs4 import BeautifulSoup, PageElement
import re
import json
from dataclasses import dataclass
from dataclasses_json import dataclass_json
import csv
import pandas as pd
import sys
import codecs

@dataclass_json
@dataclass
class Address():
    addressLine1: str
    addressLine2: str
    city: str
    stateProvince: str
    postalCode: str
    country: str

    def __post_init__(self):
        if self.addressLine2 is None:
            self.b = ''

@dataclass_json
@dataclass
class FieldOffice():
    Name: str
    OfficeURL: str



@dataclass_json
@dataclass
class Port():
    Name: str
    PortNumber: str
    websiteURL: str
    address: Address
    fieldOffice: FieldOffice

@dataclass_json
@dataclass
class Ports():
    ports: List[Port]

@dataclass_json
@dataclass
class Crossing():
    Name: str
    PortNumber: str
    address: Address
    hours: str
    phoneNumber: str

@dataclass_json
@dataclass
class PostalFacility():
    Name: str
    NASSCd: str
    DropSiteKey: str
    address: Address



class ListOfListsEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, list):
            return obj
        return json.JSONEncoder.default(self, obj)




# sample_portList = 'https://www.cbp.gov/about/contact/ports/il'
# firmsList = 'https://www.cbp.gov/sites/default/files/assets/documents/2023-Jan/FIRMS30%20.TXT'
# brokersList = 'https://www.cbp.gov/sites/default/files/2024-03/TA-015%20Broker%20Permit%20Contact%20List.csv'
# portlist = get(sample_portList)
# soup = BeautifulSoup(portlist.text, 'html.parser')
# #table = "<table class="usa-table views-table views-view-table cols-3">"
# #ports = soup.find_all("table", class_="usa-table views-table views-view-table cols-3")
#
# rss_url = "https://bwt.cbp.gov/api/bwtRss/HTML/10,52,1,76,44,43,15,12,69,53,11,28,34,20,6,7,46,32,23,25,38,22,17,68,16,35,36,47,67,155,27,65,48,50,21,93,58,5,8,26,40,180,39,41,148,72,29,9,3,4,56/-1/-1"
# response = get(rss_url)

# rss = RSSParser.parse(response.text)
#
# # Print out rss meta data
# print("Language", rss.channel.language)
# print("RSS", rss.version)
#
# # Iteratively print feed items
# for item in rss.channel.items:
#     print(item.title)
#     print(item.description[:50])
#
# import csv
# with open('chocolate.csv') as f:
#     reader = csv.reader(f, delimiter=',')
#     for row in reader:
#         print(row)

def process_port_list(state_port_url):
    portlist = get(state_port_url)
    soup = BeautifulSoup(portlist.text, 'html.parser')
    table = soup.find('table', attrs={'class': 'usa-table views-table views-view-table cols-3'})
    if table is not None:
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        ports = []
        new_ports = []
        for row in rows:
            header = row.find('th')
            port_url = header.find('a').get('href')
            port_ref_name = header.get_text().strip()
            port_format = r'(.*) [\–\-] ([0-9]*)'
            port_name_format = r'^(.*)\, (.*)$'
            if re.search(port_format, port_ref_name) is not None:
                port_name = re.search(port_format, port_ref_name).group(1)
                port_number = re.search(port_format, port_ref_name).group(2)
                if re.search(port_name_format,port_name) is not None:
                    port_name = re.search(port_name_format,port_name).group(1)
            else:
                port_name = port_ref_name
                port_number = ""
            cols = row.find_all('td')
            for ele in cols:
                if ele.p is not None:
                    port_ref_addr = ele.find("p", class_="address")
                    raw_addr = port_ref_addr.find_all('span')
                    addr = []
                    for i in raw_addr:
                        addr_key = i['class']
                        addr_value = i.get_text().strip()
                        addressLine2 = ''
                        addr.append([addr_key, addr_value])
                        if addr_key == ['address-line1']:
                            addressLine1 = addr_value
                        if addr_key == ['address-line2']:
                            addressLine2 = addr_value
                        if addr_key == ['locality']:
                            city = addr_value
                        if addr_key == ['administrative-area']:
                            stateProvince = addr_value
                        if addr_key == ['postal-code']:
                            postalCode = addr_value
                        if addr_key == ['country']:
                            country = addr_value
                    portAddr = Address(addressLine1, addressLine2, city, stateProvince, postalCode, country)
                elif ele.a is not None:
                    port_office_url = ele.find('a').get('href')
                    port_office_ref_name = ele.get_text().strip()
                    newFO = FieldOffice(port_office_ref_name, port_office_url)
                else:
                    port_office_url = ""
                    port_office_ref_name = ""
                    newFO = FieldOffice(port_office_ref_name, port_office_url)
            ports.append([port_name, port_number, port_url, addr, port_office_ref_name, port_office_url])
            new_port = Port(port_name, port_number, port_url, portAddr, newFO)
            new_ports.append(new_port)
        ListOfPorts = Ports(new_ports)
        return new_ports
    else:
        return

def get_all_US_ports():
    all_US_ports = []
    with open("states.txt", "r") as file1:
        states = file1.readlines()
    for state in states:
        portList = 'https://www.cbp.gov/about/contact/ports/' + state.strip()
        statePorts = process_port_list(portList)
        print(f"State {state.strip()} complete.")
        for port in statePorts:
            all_US_ports.append(port)
    with open("ports.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["Port Name", "Port Number", "Port URL", "Address Line 1", "Address Line 2", "City", "State", "Postal",
             "Country", "Assigned Field Office", "Field Office URL"])  # Write header row
        for port in all_US_ports:
            writer.writerow([port.Name, port.PortNumber, port.websiteURL, port.address.addressLine1, port.address.addressLine2, port.address.city, port.address.stateProvince, port.address.postalCode, port.address.country, port.fieldOffice.Name, port.fieldOffice.OfficeURL])

def get_port_crossings(portURL, portNumber):
    cbp_site = 'https://www.cbp.gov'
    facAndCrossing = r'Facilities and Crossings'
    phoneNumber = r'Phone'
    faxNumber = r'Fax'
    hoursSearch = r'Hours'
    phone_format = r'((\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4})\'?'
    hours_format = r':\s+(.*)'
    address_format = r'(Address:)\s+(.*)\s+(.*)'
    address2_format = r'(Address:)\s+(.*)\s+(.*)\s+(.*)'
    address3_format = r'(Address:)\s+(.*)\s+(.*)\s+(.*)\s+(.*)'
    citystate_format = r'(.*),\s+([A-Za-z]{2,})\s+(\d{,5})'
    address1liner_format = r'(.*),\s+(.*),\s+(\w{2})\s+(\d{5})'
    portlist = get(cbp_site+portURL)
    print(f"Port {portNumber} started.")
    soup = BeautifulSoup(portlist.text, 'html.parser')

    if re.search(facAndCrossing, soup.text) is not None:
        crossings = soup.find_all("table", class_="usa-table usa-table--striped")
        if crossings is not None:
            new_crossings = []
            crossings1 = soup.find_all("div", class_="field__label")
            for k in crossings1:
                if k.get_text() == "Facilities and Crossings":
                    crossings = k.parent.find_all("table", class_="usa-table usa-table--striped")
                    for row in crossings:
                        header = row.find('th')
                        crossing_ref_name = ''
                        if header is not None:
                            crossing_ref_name = header.get_text().strip().replace("&nbsp;", "").replace("&amp;", "and").replace("&", "and")
                            crossing_ref_name = re.sub(r'\s',' ',crossing_ref_name)
                        info = row.find_all('tr')
                        if info is not None:
                            crossingHours = ''
                            crossingPhone = ''
                            crossingAddressLn1 = ''
                            crossingAddressLn2 = ''
                            city =''
                            state = ''
                            postal = ''
                            country = "United States"
                            for i in info:

                                raw = i.get_text().strip()
                                if crossing_ref_name == '':
                                    crossing_ref_name = raw.replace(u'\xa0', ' ')

                                if (re.search(phoneNumber, raw) and re.search(phone_format, raw)) is not None:
                                    crossingPhone = re.search(phone_format, raw).group(1)
                                if (re.search(faxNumber, raw) and re.search(phone_format, raw)) is not None:
                                    crossingFax = re.search(phone_format, raw).group(1)
                                if (re.search(hoursSearch, raw) and re.search(hours_format, raw)) is not None:
                                    crossingHours = re.search(hours_format, raw).group(1)
                                if re.search(address_format, raw) is not None:
                                    br_count = len(i.find_all('br'))
                                    if br_count == 1:
                                        crossingAddressLn1 = re.search(address_format, raw).group(2)
                                        crossingAddressCitySt = re.search(address_format, raw).group(3)
                                        city = re.search(citystate_format, crossingAddressCitySt).group(1)
                                        state = re.search(citystate_format, crossingAddressCitySt).group(2)
                                        postal = re.search(citystate_format, crossingAddressCitySt).group(3)
                                if re.search(address1liner_format,raw) is not None:
                                    br_count = len(i.find_all('br'))
                                    if br_count == 0:
                                        crossingAddressLn1 = re.search(address1liner_format, raw).group(1)
                                        city = re.search(address1liner_format, raw).group(2)
                                        state = re.search(address1liner_format, raw).group(3)
                                        postal = re.search(address1liner_format, raw).group(4)
                                if (re.search(address2_format, raw)) is not None:
                                    br_count = len(i.find_all('br'))
                                    crossingAddressLn1 = re.search(address2_format, raw).group(2)
                                    if br_count == 2:
                                        crossingAddressLn2 = re.search(address2_format, raw).group(3)
                                        crossingAddressCitySt = re.search(address2_format, raw).group(4)
                                        city = re.search(citystate_format, crossingAddressCitySt).group(1)
                                        state = re.search(citystate_format, crossingAddressCitySt).group(2)
                                        postal = re.search(citystate_format, crossingAddressCitySt).group(3)
                                if (re.search(address3_format, raw)) is not None:
                                    br_count = len(i.find_all('br'))
                                    if br_count == 3:
                                        crossingAddressLn1 = re.search(address3_format, raw).group(2)
                                        crossingAddressLn2 = re.search(address3_format, raw).group(3)
                                        crossingAddressLn3 = re.search(address3_format, raw).group(4)
                                        crossingAddressCitySt = re.search(address3_format, raw).group(5)
                                        city = re.search(citystate_format, crossingAddressCitySt).group(1)
                                        state = re.search(citystate_format, crossingAddressCitySt).group(2)
                                        postal = re.search(citystate_format, crossingAddressCitySt).group(3)
                            crossingAddr = Address(crossingAddressLn1, crossingAddressLn2, city, state, postal, country)
                            new_crossing = Crossing(crossing_ref_name,portNumber,crossingAddr,crossingHours,crossingPhone)
                            new_crossings.append(new_crossing)
                            print(new_crossing)

        return new_crossings
def get_all_US_crossings():
    cbp_site = 'https://www.cbp.gov'
    df = pd.read_csv('ports.csv', dtype={
        'Port Name': 'string',
        'Port Number': 'string',
        'Port URL': 'string',
        'Address Line 1': 'string',
        'Address Line 2': 'string',
        'City': 'string',
        'State': 'string',
        'Postal': 'string',
        'Country': 'string',
        'Assigned Field Office': 'string',
        'Field Office URL': 'string',
})

    portList = df[['Port Number','Port URL']]

    crossings = []
    for index, row in portList.iterrows():
        port = get_port_crossings(row['Port URL'], row['Port Number'])
        if (port is not None and port != []):
            for crossing in port:
                crossings.append(crossing)

    print("hi")
    with open("crossings.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["Crossing Name", "Port Number", "Address Line 1", "Address Line 2", "City", "State", "Postal",
             "Country", "Crossing Hours", "Crossing Phone Number"])  # Write header row
        for crossing in crossings:
            writer.writerow([crossing.Name, crossing.PortNumber,  crossing.address.addressLine1, crossing.address.addressLine2, crossing.address.city, crossing.address.stateProvince, crossing.address.postalCode, crossing.address.country, crossing.hours, crossing.phoneNumber])



#get_all_US_ports()
# get_all_US_crossings()

# sample_portList = '/about/contact/ports/alcan-alaska-3104'
# port = get_port_crossings(sample_portList, "3104")
# print("hi")


def split_fixed_width(text, widths):
    """Splits a fixed-width text string into columns based on given widths."""
    start = 0
    columns = []
    for width in widths:
        columns.append(text[start:start + width].strip())
        start += width
    return columns


def get_firms_list():
    firmsList = 'https://www.cbp.gov/sites/default/files/assets/documents/2023-Jan/FIRMS30%20.TXT'
    import pandas as pd
    # import urllib.request
    # # firms = urllib.request.urlretrieve(firmsList, "firms.txt")
    # # import urllib.request
    # # with urllib.request.urlopen(firmsList) as f:
    # #     html = f.read().decode('utf-8')
    # # with urlopen(firmsList) as r:
    # #     s = r.read().decode('utf-8')
    # testfile = urllib.request.URLopener()
    # testfile.retrieve(firmsList, "firms.txt")
    # # Method 1: Using pandas.read_fwf()
    # df = pd.read_fwf('your_file.txt', widths=[10, 20, 15],  # Specify column widths
    #                  names=['Column1', 'Column2', 'Column3'])  # Specify column names
    regionDistPortFormat = r'REGION: (\d+)\s+DIST\/PORT: (\d{3,4})'

    # Method 2: Using colspecs for more control
    colspecs = [(1, 5), (7, 44), (45, 83), (84,107), (108,110), (114,119), (124,126), (130,132)]  # Define column positions (start, end)
    df = pd.read_fwf("firms.txt", colspecs=colspecs,
                     names=['Firm', 'Name', 'AddrLine1', 'City', 'StateCd', 'PostalCd','Status', 'Type'], limit=2)
    file2 = open(r"firms.txt", "r")
    x = file2.readlines()
    file2.close()
    y = [['firms', 'region', 'port']]
    new_y = []
    good = []
    # Process the file, throw out the headers & footers, capture the region/port info by firmscode
    for line in x:
        if line[:11] == ' PROCESSING':
            continue
        elif line[:5] == '  FAC':
            continue
        elif line[:4] == ' ---':
            continue
        elif line[:4] == '    ':
            continue
        elif line[:5] == ' FIRM':
            continue
        elif line[:5] == ' ****':
            continue
        elif line[:7] == ' REGION':
            region = re.search(regionDistPortFormat,line).group(1)
            port = re.search(regionDistPortFormat,line).group(2)
            for j in y:
                if j[1] == '' and j[2] == '':
                    new_y.append([j[0], region, port])
            y.clear()

        else:
            y.append([line[:5].strip(),'',''])
            good.append(line)


    firm = []
    firmfilewidths = [8, 38, 38, 24, 6, 10, 6, 2]
    for line in good:
        firm.append(split_fixed_width(line, firmfilewidths))
    with open("firms.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for item in firm:
            writer.writerow(item)
    with open("firmsRegionPort.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for item in new_y:
            writer.writerow(item)
    factype = dict([("01", "Customs Container Station"),
                    ("02", "Foreign Trade Zone"),
                    ("03", "Pier"),
                    ("04", "Bonded Warehouse"),
                    ("05", "Inspection Facility"),
                    ("06", "Importer Premises"),
                    ("07", "DP Site"),
                    ("08", "Custom Admin Site")
                    ])




    print(df)


#get_firms_list()

def mixrange(s):
    r = []
    for i in s.split(','):
        if '-' not in i:
            r.append(int(i))
        else:
            l,h = map(int, i.split('-'))
            r+= range(l,h+1)
    return r

def mixedRangeToFiveDigitList(s):
    r = []
    for i in s.split(','):
        if '-' not in i:
            if len(i.strip()) == 5:
                threeDigit = i.strip()[:3]
                r.append(str(int(i)).zfill(5))
            if len(i.strip()) == 2:
                i = threeDigit + i.strip()
                r.append(str(int(i)).zfill(5))
        else:
            k = []
            w = []
            i = i.split('-')
            for j in i:
                if len(j.strip()) == 5:
                    threeDigit = j.strip()[:3]
                    k.append(int(j.strip()))
                if len(j.strip()) == 2:
                    fivedigit = threeDigit + j.strip()
                    k.append(int(fivedigit))
            l, h = map(int, k)
            w += range(l, h + 1)
            for item in w: r.append (str(int(item)).zfill(5))
    return r #make this 5 character leading zero string
def get_usps_l606():

    df = pd.read_csv("DMM_l606.csv", header=5 )
    # Strip whitespace from all text columns
    df = df.apply(lambda x: x.str.strip('\t') if x.dtype == "object" else x)
    ZIPlist = []
    Destination = []
    for idx, row in df.iterrows():
        ZIPlist.append(mixedRangeToFiveDigitList(row['Column A Destination ZIP Codes']))
        Destination.append(row['Column B Label Container To'])
    print(ZIPlist)
    print("hello")


print(mixedRangeToFiveDigitList("19850, 80, 84-87, 89, 91-93, 95-98"))


# get_usps_l606()

def get_usps_facilities():
    # df1 = pd.read_excel("facilityReport.xlsx", sheet_name="Sheet1", header=2)
    # df2 = pd.read_excel("facilityReport (1).xlsx", sheet_name="Sheet1", header=2)
    # df3 = pd.read_excel("facilityReport (2).xlsx", sheet_name="Sheet1", header=2)
    # df4 = pd.read_excel("facilityReport (3).xlsx", sheet_name="Sheet1", header=2)
    # df12 = df1.append(df2, ignore_index=True)
    # df123 = df12.append(df3, ignore_index=True)
    # df1234 = df123.append(df4, ignore_index=True)
    colspecs = [(0, 1), (1, 9), (10, 11), (11, 38), (39, 96), (97, 124), (125, 127),
                (127, 136)]  # Define column positions (start, end)
    df = pd.read_fwf("ADDRESS.txt", colspecs=colspecs,
                     names=['DetailCode', 'DropSiteKey', 'DropSiteTypeCode', 'DropSiteName', 'DeliveryAddressLine1', 'DeliveryAddressCity', 'DeliveryAddressState', 'DeliveryAddressPostal'], limit=2)
    df['DeliveryAddressPostalNine'] = df['DeliveryAddressPostal'].apply(lambda x: str(int(x)).zfill(9))
    df['DeliveryAddressPostalThree'] = df['DeliveryAddressPostalNine'].apply(lambda x: x[:3])
    df['DeliveryAddressPostalFive'] = df['DeliveryAddressPostalNine'].apply(lambda x: x[:5])
    df.drop(['DeliveryAddressPostal'], axis=1, inplace=True)
    # from geopy.geocoders import Nominatim
    # site = df.iloc[[0]].to_numpy(dtype=str)
    # geolocator = Nominatim(user_agent="location_dddddb")
    # addressA = site[0, 4] + " " + site[0, 5] + ", " + site[0, 6] + " " + site[0, 7]
    # locationA = geolocator.geocode(addressA)
    group_counts = df.groupby('DeliveryAddressState').size()
    print(group_counts)
    group_counts = df.groupby('DeliveryAddressPostalThree').size()
    print(group_counts)
    print("hi")
get_usps_facilities()