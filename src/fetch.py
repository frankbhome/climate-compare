from __future__ import annotations

import logging
from datetime import date, datetime
from functools import lru_cache

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

# Import database functionality
try:
    from src.database import ClimateDatabase
except ImportError:
    from database import ClimateDatabase  # type: ignore

logger = logging.getLogger(__name__)
DateLike = date | datetime

# Global database instance
_db_instance = None


def get_database() -> ClimateDatabase:
    """Get or create a database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = ClimateDatabase()
    return _db_instance


@lru_cache(maxsize=128)
def get_historical_weather(
    lat: float, lon: float, start: DateLike, end: DateLike
) -> pd.DataFrame | None:
    """
    Fetch historical daily weather data for a given location and date range.
    
    First checks the database for existing data, then falls back to API if needed.

    Args:
        lat: Latitude in decimal degrees.
        lon: Longitude in decimal degrees.
        start: Start date (date or datetime).
        end: End date (date or datetime).

    Returns:
        pd.DataFrame | None: A DataFrame with daily observations or None on error.
    """
    if not PANDAS_AVAILABLE:
        logger.warning("Pandas not available, database functionality limited")
        return None
        
    try:
        # Normalize dates to date objects for database queries
        if isinstance(start, datetime):
            start_date = start.date()
        else:
            start_date = start
            
        if isinstance(end, datetime):
            end_date = end.date()
        else:
            end_date = end

        # Try to get data from database first
        db = get_database()
        df_from_db = db.get_weather_data(lat, lon, start_date, end_date)
        
        if df_from_db is not None and (
            (hasattr(df_from_db, 'empty') and not df_from_db.empty) or
            (isinstance(df_from_db, list) and len(df_from_db) > 0)
        ):
            logger.info("Retrieved weather data from database for lat=%s lon=%s", lat, lon)
            # Return defensive copy to keep cache returns immutable for callers
            if hasattr(df_from_db, 'copy'):
                return df_from_db.copy(deep=True)
            else:
                return df_from_db

        # Fallback to API if no database data found
        logger.info("No database data found, fetching from API for lat=%s lon=%s", lat, lon)
        
        # Import meteostat only when needed (might not be available)
        try:
            from meteostat import Daily, Point
        except ImportError:
            logger.error("Meteostat not available for API fallback")
            return None
        
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
        
        if df is not None and not df.empty:
            # Store the fetched data in database for future use
            db.store_weather_data(lat, lon, df)
            logger.info("Stored fetched weather data in database for lat=%s lon=%s", lat, lon)
        
        # Defensive copy to keep cache returns immutable for callers
        return df.copy(deep=True) if df is not None else None

    except TimeoutError:
        logger.exception("Timeout while fetching weather for lat=%s lon=%s", lat, lon)
        return None
    except Exception:
        logger.exception(
            "Unexpected error fetching weather for lat=%s lon=%s", lat, lon
        )
        return None
