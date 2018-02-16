import re
from datetime import datetime


def sap_date_to_datetime(sap_str: str) -> datetime or None:
    if sap_str is None:
        return None
    sap_str = sap_str.replace('/Date(', '')
    sap_str = sap_str.replace(')', '')
    sap_str = sap_str.split('+')[0]
    timestamp = int(sap_str) / 1000
    return datetime.fromtimestamp(timestamp)


def datetime_to_sap_date(date: datetime) -> str:
    timestamp = int(date.timestamp() * 1000)
    return f'/Date({timestamp}+0100)/'


# from https://stackoverflow.com/a/1176023/1843020
def convert_to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
