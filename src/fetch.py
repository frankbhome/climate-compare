from datetime import datetime
from functools import lru_cache
from meteostat import Point, Daily
from typing import Optional
import pandas as pd


@lru_cache(maxsize=128)
def get_historical_weather(
    lat: float, lon: float, start: datetime, end: datetime
) -> Optional[pd.DataFrame]:
    """
    Fetch historical weather data for a specific location and time period.

    Args:
        lat: Latitude of the location
        lon: Longitude of the location
        start: Start date for the data
        end: End date for the data

    Returns:
        A pandas DataFrame containing daily weather data or None if an error occurs

    Raises:
        ValueError: If latitude or longitude are invalid
        ValueError: If start date is after end date
    """
    try:
        # Validate inputs
        if not (-90 <= lat <= 90):
            raise ValueError(f"Latitude must be between -90 and 90, got {lat}")
        if not (-180 <= lon <= 180):
            raise ValueError(f"Longitude must be between -180 and 180, got {lon}")
        if start > end:
            raise ValueError(f"Start date ({start}) must be before end date ({end})")

        # Create location point and fetch data
        location = Point(lat, lon)
        weather_data = Daily(location, start, end)
        return weather_data.fetch()
    except Exception as e:
        # Consider logging the error here
        print(f"Error fetching weather data: {e}")
        return None
    """
    Fetch historical weather data for a specific location and time period.
    
    Args:
        lat: Latitude of the location
        lon: Longitude of the location
        start: Start date for the data
        end: End date for the data
        
    Returns:
        A pandas DataFrame containing daily weather data or None if an error occurs
        
    Raises:
        ValueError: If latitude or longitude are invalid
    """
    try:
        # Validate inputs
        if not (-90 <= lat <= 90):
            raise ValueError(f"Latitude must be between -90 and 90, got {lat}")
        if not (-180 <= lon <= 180):
            raise ValueError(f"Longitude must be between -180 and 180, got {lon}")

        # Create location point and fetch data
        location = Point(lat, lon)
        weather_data = Daily(location, start, end)
        return weather_data.fetch()
    except Exception as e:
        # Consider logging the error here
        print(f"Error fetching weather data: {e}")
        return None
