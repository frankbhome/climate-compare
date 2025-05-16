from meteostat import Point, Daily
from datetime import datetime

def get_historical_weather(lat, lon, start, end):
    """
    Retrieves daily historical weather data for a specified location and date range.
    
    Args:
        lat: Latitude of the location.
        lon: Longitude of the location.
        start: Start date of the period (datetime or string in 'YYYY-MM-DD' format).
        end: End date of the period (datetime or string in 'YYYY-MM-DD' format).
    
    Returns:
        A dataset containing daily weather data for the given location and date range.
    """
    location = Point(lat, lon)
    data = Daily(location, start, end)
    data = data.fetch()
    return data
