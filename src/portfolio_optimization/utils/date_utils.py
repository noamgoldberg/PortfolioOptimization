from typing import Optional
import datetime
import pandas as pd
from portfolio_optimization.consts import DATE_FORMAT

def get_end_date(end_date: Optional[str], format: str = DATE_FORMAT) -> str:
    end_date = datetime.datetime.today() if end_date is None else end_date
    return format_date(end_date, format=format)

def format_date(date, format: str = DATE_FORMAT) -> str:
    if isinstance(date, str):
        date = pd.to_datetime(date)
    if isinstance(date, (datetime.datetime, pd.Timestamp)):
        return date.strftime(format)
    raise ValueError(f"{date} ({type(date)}): Invalid value for date parameter")
    