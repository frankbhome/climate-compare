# tests/test_fetch.py

from datetime import datetime
from src.fetch import get_historical_weather

def test_get_historical_weather_returns_dataframe():
    lat = 55.9533  # Edinburgh
    lon = -3.1883
    start = datetime(2023, 1, 1)
    end = datetime(2023, 1, 10)

    df = get_historical_weather(lat, lon, start, end)

    assert df is not None
    assert not df.empty
    assert "tavg" in df.columns or "tmin" in df.columns or "tmax" in df.columns
