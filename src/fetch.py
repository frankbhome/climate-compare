from datetime import datetime
from functools import lru_cache

from meteostat import Point, Daily
import pandas as pd


@lru_cache(maxsize=128)
def get_historical_weather(
    lat: float,
    lon: float,
    start: datetime,
    end: datetime
) -> pd.DataFrame:
    """
    Fetch historical daily weather data for a given location and date range.

    Parameters:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        start (datetime): Start date (inclusive).
        end (datetime): End date (inclusive).

    Returns:
        pd.DataFrame: DataFrame containing daily weather data for the specified location and date range.

    Raises:
        ValueError: If input types are incorrect or start > end.
        RuntimeError: If data fetching fails due to API or network errors.
    """
    if not isinstance(lat, float):
        raise ValueError(f"lat must be a float, got {type(lat).__name__}")
    if not -90 <= lat <= 90:
        raise ValueError("lat must be between -90 and 90")
    if not isinstance(lon, float):
        raise ValueError(f"lon must be a float, got {type(lon).__name__}")
    if not -180 <= lon <= 180:
        raise ValueError("lon must be between -180 and 180")
    if not isinstance(start, datetime):
        raise ValueError(f"start must be a datetime object, got {type(start).__name__}")
    if not isinstance(end, datetime):
        raise ValueError(f"end must be a datetime object, got {type(end).__name__}")
    if start > end:
        raise ValueError("start date must be less than or equal to end date")

    location = Point(lat, lon)
    data = Daily(location, start, end)
    try:
        data = data.fetch()
    except Exception as e:
        raise RuntimeError(f"Failed to fetch weather data: {e}")
    if data is None or data.empty:
        raise RuntimeError("No weather data returned for the specified location and date range.")
    return data
