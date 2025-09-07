# Copyright (c) 2025 Francis Bain
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
from datetime import date, datetime
from functools import lru_cache

import pandas as pd
import requests
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
        # Validate latitude/longitude before making any network/API calls.
        try:
            lat_f = float(lat)
            lon_f = float(lon)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError(
                f"Invalid latitude/longitude types: {lat!r}, {lon!r}"
            ) from exc

        if not (-90.0 <= lat_f <= 90.0):
            raise ValueError(f"Latitude out of range: {lat_f}")
        if not (-180.0 <= lon_f <= 180.0):
            raise ValueError(f"Longitude out of range: {lon_f}")

        # Meteostat expects datetimes; normalise dates to midnight datetimes
        if isinstance(start, date) and not isinstance(start, datetime):
            start_dt = datetime(start.year, start.month, start.day)
        else:
            start_dt = start  # already datetime

        if isinstance(end, date) and not isinstance(end, datetime):
            end_dt = datetime(end.year, end.month, end.day)
        else:
            end_dt = end  # already datetime

        location = Point(lat_f, lon_f)
        df = Daily(location, start_dt, end_dt).fetch()
        # Defensive copy to keep cache returns immutable for callers
        return df.copy(deep=True)

    except TimeoutError:
        logger.exception("Timeout while fetching weather for lat=%s lon=%s", lat, lon)
        return None
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
        logger.exception(
            "HTTP error while fetching weather for lat=%s lon=%s: %s",
            lat,
            lon,
            exc,
        )
        return None
    except Exception:
        logger.exception(
            "Unexpected error fetching weather for lat=%s lon=%s", lat, lon
        )
        return None
