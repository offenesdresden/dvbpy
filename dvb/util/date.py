from datetime import datetime
import re


def sap_date_to_datetime(sap_str: str) -> datetime or None:
    """Convert date as str in format '/Date(1518807600000+0100)/' to datetime obj"""
    if sap_str is None:
        return None

    pattern = r'\/Date\((\d+)[+-](\d+)\)\/'
    matches = re.findall(pattern, sap_str)
    ts_str, tz = matches[0]
    # interestingly enough the timezone offset doesn't seem to be correct, so we're ignoring it for now 🤔
    timestamp = int(ts_str) / 1000
    return datetime.fromtimestamp(timestamp)


def datetime_to_sap_date(date: datetime) -> str:
    """Convert datetime obj to date as str in format '/Date(1518807600000+0100)/'"""
    timestamp = int(date.timestamp() * 1000)
    return f'/Date({timestamp}+0100)/'
