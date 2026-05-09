import re
from constants import REGEX_PATTERNS


def split_fixed_width(text, widths):
    """Splits a fixed-width text string into columns based on given widths."""
    start = 0
    columns = []
    for width in widths:
        columns.append(text[start:start + width].strip())
        start += width
    return columns


def parse_address_from_raw_text(raw_text):
    """Parse address from raw crossing text with multiple format handling."""
    city = ''
    state = ''
    postal = ''
    addressLine1 = ''
    addressLine2 = ''

    patterns = REGEX_PATTERNS
    citystate_re = re.compile(patterns['citystate_format'])
    address_re = re.compile(patterns['address_format'])
    address1liner_re = re.compile(patterns['address1liner_format'])
    address2_re = re.compile(patterns['address2_format'])
    address3_re = re.compile(patterns['address3_format'])

    try:
        if address_re.search(raw_text):
            match = address_re.search(raw_text)
            addressLine1 = match.group(2)
            city_state_str = match.group(3)
            city_match = citystate_re.search(city_state_str)
            if city_match:
                city = city_match.group(1)
                state = city_match.group(2)
                postal = city_match.group(3)

        if address1liner_re.search(raw_text):
            match = address1liner_re.search(raw_text)
            addressLine1 = match.group(1)
            city = match.group(2)
            state = match.group(3)
            postal = match.group(4)

        if address2_re.search(raw_text):
            match = address2_re.search(raw_text)
            addressLine1 = match.group(2)
            addressLine2 = match.group(3)
            city_state_str = match.group(4)
            city_match = citystate_re.search(city_state_str)
            if city_match:
                city = city_match.group(1)
                state = city_match.group(2)
                postal = city_match.group(3)

        if address3_re.search(raw_text):
            match = address3_re.search(raw_text)
            addressLine1 = match.group(2)
            addressLine2 = match.group(3)
            city_state_str = match.group(5)
            city_match = citystate_re.search(city_state_str)
            if city_match:
                city = city_match.group(1)
                state = city_match.group(2)
                postal = city_match.group(3)
    except (AttributeError, IndexError):
        pass

    return {
        'addressLine1': addressLine1,
        'addressLine2': addressLine2,
        'city': city,
        'state': state,
        'postal': postal
    }


def mixrange(s):
    """Convert a comma-separated string with ranges into a list of integers."""
    r = []
    for i in s.split(','):
        if '-' not in i:
            r.append(int(i))
        else:
            l, h = map(int, i.split('-'))
            r += range(l, h + 1)
    return r


def mixedRangeToFiveDigitList(s):
    """Convert mixed format range string to list of 5-digit zero-padded strings."""
    r = []
    threeDigit = ''
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
            i_parts = i.split('-')
            for j in i_parts:
                if len(j.strip()) == 5:
                    threeDigit = j.strip()[:3]
                    k.append(int(j.strip()))
                if len(j.strip()) == 2:
                    fivedigit = threeDigit + j.strip()
                    k.append(int(fivedigit))
            l, h = map(int, k)
            w = range(l, h + 1)
            for item in w:
                r.append(str(int(item)).zfill(5))
    return r
