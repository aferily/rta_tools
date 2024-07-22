import configparser
import calendar
import argparse
from datetime import *

def split_period_by_month(start_date: date, end_date: date) -> list:
    periods = []
    while start_date <= end_date:
        local_start = datetime(
            year = start_date.year, 
            month = start_date.month, 
            day = 1)
        
        local_end = datetime(
            year = start_date.year, 
            month = start_date.month, 
            day = calendar.monthrange(year=start_date.year, month=start_date.month)[1])

        periods.append([local_start, local_end])

        last_month = start_date.month % 12 == 0
        start_date = datetime(
            year = start_date.year + 1 if last_month else start_date.year, 
            month = 1 if last_month else start_date.month + 1, 
            day = 1)
        
    return periods


def valid_date(s: str) -> datetime:
    try:
        return datetime.strptime(s, "%m.%Y")
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a valid date: {s!r}")