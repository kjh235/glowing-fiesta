import re
import csv
from typing import List, Optional
from requests import get
from bs4 import BeautifulSoup

from models import Address, FieldOffice, Port, Crossing, Ports
from constants import (CBP_SITE, PORT_BASE_URL, REGEX_PATTERNS,
                       PORTS_CSV_COLUMNS, CROSSINGS_CSV_COLUMNS)
from utils import parse_address_from_raw_text


def process_port_list(state_port_url: str) -> Optional[List[Port]]:
    """Scrape port information from a state port listing page."""
    try:
        portlist = get(state_port_url)
        portlist.raise_for_status()
    except Exception as e:
        print(f"Error fetching {state_port_url}: {e}")
        return None

    soup = BeautifulSoup(portlist.text, 'html.parser')
    table = soup.find('table', attrs={'class': 'usa-table views-table views-view-table cols-3'})

    if table is None:
        return None

    table_body = table.find('tbody')
    if table_body is None:
        return None

    rows = table_body.find_all('tr')
    new_ports = []

    patterns = REGEX_PATTERNS
    port_format_re = re.compile(patterns['port_format'])
    port_name_format_re = re.compile(patterns['port_name_format'])

    for row in rows:
        try:
            header = row.find('th')
            port_url = header.find('a').get('href')
            port_ref_name = header.get_text().strip()

            if port_format_re.search(port_ref_name):
                port_name = port_format_re.search(port_ref_name).group(1)
                port_number = port_format_re.search(port_ref_name).group(2)
                if port_name_format_re.search(port_name):
                    port_name = port_name_format_re.search(port_name).group(1)
            else:
                port_name = port_ref_name
                port_number = ""

            cols = row.find_all('td')
            addressLine1 = ''
            addressLine2 = ''
            city = ''
            stateProvince = ''
            postalCode = ''
            country = ''
            port_office_ref_name = ''
            port_office_url = ''

            for ele in cols:
                if ele.p is not None:
                    port_ref_addr = ele.find("p", class_="address")
                    if port_ref_addr:
                        raw_addr = port_ref_addr.find_all('span')
                        for i in raw_addr:
                            addr_key = i.get('class', [])
                            addr_value = i.get_text().strip()
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
                elif ele.a is not None:
                    port_office_url = ele.find('a').get('href')
                    port_office_ref_name = ele.get_text().strip()

            portAddr = Address(addressLine1, addressLine2, city, stateProvince, postalCode, country)
            newFO = FieldOffice(port_office_ref_name, port_office_url)
            new_port = Port(port_name, port_number, port_url, portAddr, newFO)
            new_ports.append(new_port)
        except (AttributeError, IndexError) as e:
            print(f"Error processing port row: {e}")
            continue

    return new_ports if new_ports else None


def get_all_US_ports():
    """Process all US state ports and export to CSV."""
    all_US_ports = []

    try:
        with open("states.txt", "r") as file1:
            states = file1.readlines()
    except FileNotFoundError:
        print("Error: states.txt not found")
        return

    for state in states:
        state_name = state.strip()
        if not state_name:
            continue
        portList = PORT_BASE_URL + state_name
        statePorts = process_port_list(portList)
        if statePorts:
            print(f"State {state_name} complete.")
            for port in statePorts:
                all_US_ports.append(port)
        else:
            print(f"No ports found for state {state_name}.")

    try:
        with open("ports.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(PORTS_CSV_COLUMNS)
            for port in all_US_ports:
                writer.writerow([
                    port.Name, port.PortNumber, port.websiteURL,
                    port.address.addressLine1, port.address.addressLine2,
                    port.address.city, port.address.stateProvince,
                    port.address.postalCode, port.address.country,
                    port.fieldOffice.Name, port.fieldOffice.OfficeURL
                ])
        print(f"Successfully wrote {len(all_US_ports)} ports to ports.csv")
    except IOError as e:
        print(f"Error writing to ports.csv: {e}")


def get_port_crossings(portURL: str, portNumber: str) -> Optional[List[Crossing]]:
    """Extract crossing information from a port page."""
    try:
        portlist = get(CBP_SITE + portURL)
        portlist.raise_for_status()
    except Exception as e:
        print(f"Error fetching port {portNumber}: {e}")
        return None

    print(f"Port {portNumber} started.")
    soup = BeautifulSoup(portlist.text, 'html.parser')
    patterns = REGEX_PATTERNS

    if not re.search(patterns['fac_and_crossing'], soup.text):
        return None

    crossings_divs = soup.find_all("div", class_="field__label")
    new_crossings = []

    for div in crossings_divs:
        if div.get_text() != "Facilities and Crossings":
            continue

        crossing_tables = div.parent.find_all("table", class_="usa-table usa-table--striped")
        for table_row in crossing_tables:
            header = table_row.find('th')
            crossing_ref_name = ''
            if header is not None:
                crossing_ref_name = header.get_text().strip()
                crossing_ref_name = crossing_ref_name.replace("&nbsp;", "").replace("&amp;", "and").replace("&", "and")
                crossing_ref_name = re.sub(r'\s', ' ', crossing_ref_name)

            info_rows = table_row.find_all('tr')
            if not info_rows:
                continue

            for info_row in info_rows:
                raw = info_row.get_text().strip()
                if crossing_ref_name == '':
                    crossing_ref_name = raw.replace(u'\xa0', ' ')

                crossingHours = ''
                crossingPhone = ''
                country = "United States"

                phone_match = re.search(patterns['phone_format'], raw)
                if re.search(patterns['phone_number'], raw) and phone_match:
                    crossingPhone = phone_match.group(1)

                hours_match = re.search(patterns['hours_format'], raw)
                if re.search(patterns['hours_search'], raw) and hours_match:
                    crossingHours = hours_match.group(1)

                if re.search(patterns['address_format'], raw):
                    addr_data = parse_address_from_raw_text(raw)
                    crossingAddr = Address(
                        addr_data['addressLine1'],
                        addr_data['addressLine2'],
                        addr_data['city'],
                        addr_data['state'],
                        addr_data['postal'],
                        country
                    )
                    new_crossing = Crossing(crossing_ref_name, portNumber, crossingAddr, crossingHours, crossingPhone)
                    new_crossings.append(new_crossing)
                    print(new_crossing)

    return new_crossings if new_crossings else None


def get_all_US_crossings():
    """Process all crossings from ports and export to CSV."""
    import pandas as pd

    try:
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
    except FileNotFoundError:
        print("Error: ports.csv not found. Run get_all_US_ports() first.")
        return
    except Exception as e:
        print(f"Error reading ports.csv: {e}")
        return

    portList = df[['Port Number', 'Port URL']]
    crossings = []

    for index, row in portList.iterrows():
        port = get_port_crossings(row['Port URL'], row['Port Number'])
        if port is not None and port != []:
            for crossing in port:
                crossings.append(crossing)

    try:
        with open("crossings.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CROSSINGS_CSV_COLUMNS)
            for crossing in crossings:
                writer.writerow([
                    crossing.Name, crossing.PortNumber,
                    crossing.address.addressLine1, crossing.address.addressLine2,
                    crossing.address.city, crossing.address.stateProvince,
                    crossing.address.postalCode, crossing.address.country,
                    crossing.hours, crossing.phoneNumber
                ])
        print(f"Successfully wrote {len(crossings)} crossings to crossings.csv")
    except IOError as e:
        print(f"Error writing to crossings.csv: {e}")
