import pandas as pd

from constants import USPS_COLSPECS, USPS_COLUMN_NAMES
from utils import mixedRangeToFiveDigitList


def get_usps_l606():
    """Process USPS L606 DMM data with ZIP code ranges."""
    try:
        df = pd.read_csv("DMM_l606.csv", header=5)
    except FileNotFoundError:
        print("Error: DMM_l606.csv not found")
        return
    except Exception as e:
        print(f"Error reading DMM_l606.csv: {e}")
        return

    df = df.apply(lambda x: x.str.strip('\t') if x.dtype == "object" else x)
    ZIPlist = []
    Destination = []

    for idx, row in df.iterrows():
        try:
            ZIPlist.append(mixedRangeToFiveDigitList(row['Column A Destination ZIP Codes']))
            Destination.append(row['Column B Label Container To'])
        except (KeyError, ValueError) as e:
            print(f"Error processing row {idx}: {e}")
            continue

    print("ZIP Lists:", ZIPlist)
    print("Processing complete")


def get_usps_facilities():
    """Process USPS facility address data from fixed-width text file."""
    colspecs = USPS_COLSPECS
    column_names = USPS_COLUMN_NAMES

    try:
        df = pd.read_fwf("ADDRESS.txt", colspecs=colspecs,
                         names=column_names, limit=2)
    except FileNotFoundError:
        print("Error: ADDRESS.txt not found")
        return
    except Exception as e:
        print(f"Error reading ADDRESS.txt: {e}")
        return

    df['DeliveryAddressPostalNine'] = df['DeliveryAddressPostal'].apply(
        lambda x: str(int(x)).zfill(9))
    df['DeliveryAddressPostalThree'] = df['DeliveryAddressPostalNine'].apply(
        lambda x: x[:3])
    df['DeliveryAddressPostalFive'] = df['DeliveryAddressPostalNine'].apply(
        lambda x: x[:5])
    df.drop(['DeliveryAddressPostal'], axis=1, inplace=True)

    group_counts = df.groupby('DeliveryAddressState').size()
    print("Facilities by State:")
    print(group_counts)

    group_counts = df.groupby('DeliveryAddressPostalThree').size()
    print("Facilities by Postal 3-digit:")
    print(group_counts)
