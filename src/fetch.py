from __future__ import annotations

import logging
from datetime import date, datetime
from functools import lru_cache

import pandas as pd
from meteostat import Daily, Point

logger = logging.getLogger(__name__)
DateLike = date | datetime


@lru_cache(maxsize=128)
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
