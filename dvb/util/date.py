from datetime import datetime


def sap_date_to_datetime(sap_str: str) -> datetime or None:
    """Convert date as str in format '/Date(1518807600000+0100)/' to datetime obj"""
    if sap_str is None:
        return None
    sap_str = sap_str.replace('/Date(', '')
    sap_str = sap_str.replace(')', '')
    sap_str = sap_str.split('+')[0]
    sap_str = sap_str.split('-')[0]  # FIXME
    timestamp = int(sap_str) / 1000
    return datetime.fromtimestamp(timestamp)


def datetime_to_sap_date(date: datetime) -> str:
    """Convert datetime obj to date as str in format '/Date(1518807600000+0100)/'"""
    timestamp = int(date.timestamp() * 1000)
    return f'/Date({timestamp}+0100)/'
