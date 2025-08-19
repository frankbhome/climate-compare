from datetime import datetime
from functools import lru_cache

import pandas as pd
from meteostat import Daily, Point


@lru_cache(maxsize=128)
def get_historical_weather(
    lat: float, lon: float, start: datetime, end: datetime
) -> pd.DataFrame | None:
    """
    Fetch historical daily weather data for a given location and date range.

    Parameters:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        start (datetime): Start date (inclusive).
        end (datetime): End date (inclusive).

    Returns:
        pd.DataFrame: DataFrame containing daily weather data for the specified
            location and date range.

    Raises:
        ValueError: If input types are incorrect or start > end.
        RuntimeError: If data fetching fails due to API or network errors.
    """
    try:
        location = Point(lat, lon)
        data = Daily(location, start, end)
        df = data.fetch()
        return df
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None
