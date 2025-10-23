"""Utility functions"""
from datetime import datetime


def parse_money_str(s):
    """Parse a formatted money string back to float"""
    try:
        return float(str(s).split()[0].replace(".", "").replace(",", ""))
    except:
        return 0.0


def parse_date(s):
    """Parse a date string in YYYY-MM-DD format"""
    s = s.strip()
    if not s:
        return None
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return s
    except:
        return None
