from __future__ import annotations

import logging
from datetime import date, datetime
from functools import lru_cache

import pandas as pd
from meteostat import Daily, Point

logger = logging.getLogger(__name__)
DateLike = date | datetime

try:
    from .cache_config import WEATHER_CACHE_SIZE
except ImportError:
    # Fallback if cache_config is not available
    WEATHER_CACHE_SIZE = 512

# Enhanced cache size for better performance
# Default cache can hold ~512 unique weather requests
# Each request typically covers 1-30 days of data
@lru_cache(maxsize=WEATHER_CACHE_SIZE)
def get_historical_weather(
    lat: float, lon: float, start: DateLike, end: DateLike
) -> pd.DataFrame | None:
    """
    Fetch historical daily weather data for a given location and date range.

    Args:
        lat: Latitude in decimal degrees.
        lon: Longitude in decimal degrees.
        start: Start date (date or datetime).
        end: End date (date or datetime).

    Returns:
        pd.DataFrame | None: A DataFrame with daily observations or None on error.
    """
    try:
        # Meteostat expects datetimes; normalise dates to midnight datetimes
        if isinstance(start, date) and not isinstance(start, datetime):
            start_dt = datetime(start.year, start.month, start.day)
        else:
            start_dt = start  # already datetime

        if isinstance(end, date) and not isinstance(end, datetime):
            end_dt = datetime(end.year, end.month, end.day)
        else:
            end_dt = end  # already datetime

        location = Point(lat, lon)
        df = Daily(location, start_dt, end_dt).fetch()
        # Defensive copy to keep cache returns immutable for callers
        return df.copy(deep=True)

    except TimeoutError:
        logger.exception("Timeout while fetching weather for lat=%s lon=%s", lat, lon)
        return None
    except Exception:
        logger.exception(
            "Unexpected error fetching weather for lat=%s lon=%s", lat, lon
        )
        return None


def get_cache_info() -> dict[str, int]:
    """
    Get cache statistics for the weather data cache.
    
    Returns:
        dict: Cache statistics including hits, misses, maxsize, and currsize
    """
    cache_info = get_historical_weather.cache_info()
    return {
        "hits": cache_info.hits,
        "misses": cache_info.misses,
        "maxsize": cache_info.maxsize,
        "currsize": cache_info.currsize,
    }


def clear_weather_cache() -> None:
    """Clear the weather data cache."""
    get_historical_weather.cache_clear()
    logger.info("Weather data cache cleared")


def warm_cache_for_common_locations() -> dict[str, str]:
    """
    Pre-warm cache with data for common locations.
    
    Returns:
        dict: Status of cache warming for each location
    """
    from datetime import date, timedelta
    
    # Common locations from PRESETS in streamlit_app.py
    common_locations = [
        (55.9533, -3.1883),  # Edinburgh
        (51.5074, -0.1278),  # London
        (55.8642, -4.2518),  # Glasgow
    ]
    
    # Recent 30 days of data
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    results = {}
    for lat, lon in common_locations:
        try:
            df = get_historical_weather(lat, lon, start_date, end_date)
            if df is not None:
                results[f"{lat},{lon}"] = "success"
                logger.info("Cache warmed for location %s,%s", lat, lon)
            else:
                results[f"{lat},{lon}"] = "no_data"
        except Exception as e:
            results[f"{lat},{lon}"] = f"error: {e}"
            logger.error("Failed to warm cache for %s,%s: %s", lat, lon, e)
    
    return results
