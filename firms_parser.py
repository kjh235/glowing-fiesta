import re
import csv
import pandas as pd

from constants import (FIRMS_LIST_URL, REGEX_PATTERNS, FIRMS_COLSPECS,
                       FIRMS_FILE_WIDTHS, FACILITY_TYPES)
from utils import split_fixed_width


def get_firms_list():
    """Parse FIRMS facility list from fixed-width text file."""
    colspecs = FIRMS_COLSPECS
    patterns = REGEX_PATTERNS

    try:
        df = pd.read_fwf("firms.txt", colspecs=colspecs,
                         names=['Firm', 'Name', 'AddrLine1', 'City', 'StateCd', 'PostalCd', 'Status', 'Type'], limit=2)
    except FileNotFoundError:
        print("Error: firms.txt not found")
        return

    try:
        with open(r"firms.txt", "r") as file2:
            x = file2.readlines()
    except IOError as e:
        print(f"Error reading firms.txt: {e}")
        return

    y = [['firms', 'region', 'port']]
    new_y = []
    good = []

    region_format_re = re.compile(patterns['region_dist_port_format'])

    for line in x:
        if (line[:11] == ' PROCESSING' or line[:5] == '  FAC' or
            line[:4] == ' ---' or line[:4] == '    ' or
            line[:5] == ' FIRM' or line[:5] == ' ****'):
            continue
        elif line[:7] == ' REGION':
            try:
                region = region_format_re.search(line).group(1)
                port = region_format_re.search(line).group(2)
                for j in y:
                    if j[1] == '' and j[2] == '':
                        new_y.append([j[0], region, port])
                y.clear()
            except (AttributeError, IndexError):
                print(f"Error parsing region/port from line: {line}")
        else:
            y.append([line[:5].strip(), '', ''])
            good.append(line)

    firmfilewidths = FIRMS_FILE_WIDTHS
    firm = []
    for line in good:
        firm.append(split_fixed_width(line, firmfilewidths))

    try:
        with open("firms.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for item in firm:
                writer.writerow(item)
        print(f"Successfully wrote {len(firm)} firms to firms.csv")
    except IOError as e:
        print(f"Error writing to firms.csv: {e}")

    try:
        with open("firmsRegionPort.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for item in new_y:
                writer.writerow(item)
        print(f"Successfully wrote {len(new_y)} facility mappings to firmsRegionPort.csv")
    except IOError as e:
        print(f"Error writing to firmsRegionPort.csv: {e}")

    print(df)
