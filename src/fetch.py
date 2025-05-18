from datetime import datetime
from functools import lru_cache
from typing import Optional

import pandas as pd
from meteostat import Daily, Point


@lru_cache(maxsize=128)
def get_historical_weather(
    lat: float, lon: float, start: datetime, end: datetime
) -> Optional[pd.DataFrame]:
    """
    Fetch historical weather data for the given latitude, longitude, and date range.
    Returns a pandas DataFrame or None if fetching fails.
    """
    try:
        location = Point(lat, lon)
        data = Daily(location, start, end)
        df = data.fetch()
        return df
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None
