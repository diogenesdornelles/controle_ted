from datetime import datetime as dt
from functools import lru_cache


@lru_cache
def return_today_str() -> str:
    """Returns current date brl format"""
    return dt.now().strftime("%d/%m/%Y")
