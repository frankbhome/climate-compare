# tests/test_fetch.py

import pytest
from unittest.mock import patch
import pandas as pd


def test_get_historical_weather_returns_dataframe():
    """Verify that get_historical_weather returns a non-empty DataFrame with temperature data."""
    lat = 55.9533  # Edinburgh
    lon = -3.1883
    start = datetime(2023, 1, 1)
    end = datetime(2023, 1, 10)

    # Mock the Daily class to return a predictable DataFrame
    mock_df = pd.DataFrame({
        'time': pd.date_range(start=start, end=end),
        'tavg': [10.5, 11.2, 9.8, 10.1, 12.3, 11.7, 10.9, 9.5, 10.3, 11.0],
    })
    
    with patch('src.fetch.Daily') as mock_daily:
        mock_daily.return_value.fetch.return_value = mock_df
        df = get_historical_weather(lat, lon, start, end)