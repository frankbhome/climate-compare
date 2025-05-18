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

        print(f"Error fetching weather data: {e}")
        return None

