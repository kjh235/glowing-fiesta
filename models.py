from typing import List
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Address:
    addressLine1: str
    addressLine2: str
    city: str
    stateProvince: str
    postalCode: str
    country: str

    def __post_init__(self):
        if self.addressLine2 is None:
            self.addressLine2 = ''


@dataclass_json
@dataclass
class FieldOffice:
    Name: str
    OfficeURL: str


@dataclass_json
@dataclass
class Port:
    Name: str
    PortNumber: str
    websiteURL: str
    address: Address
    fieldOffice: FieldOffice


@dataclass_json
@dataclass
class Ports:
    ports: List[Port]


@dataclass_json
@dataclass
class Crossing:
    Name: str
    PortNumber: str
    address: Address
    hours: str
    phoneNumber: str


@dataclass_json
@dataclass
class PostalFacility:
    Name: str
    NASSCd: str
    DropSiteKey: str
    address: Address
