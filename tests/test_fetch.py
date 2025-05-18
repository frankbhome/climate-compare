# tests/test_fetch.py

from datetime import datetime
from unittest.mock import patch
import pandas as pd
from src.fetch import get_historical_weather


def test_get_historical_weather_returns_dataframe():
    """
    Tests that get_historical_weather returns the expected DataFrame with temperature data for a given location and date range.

    This test mocks the Daily class to ensure get_historical_weather interacts correctly with it and returns the correct DataFrame.
    """
    lat = 55.9533  # Edinburgh
    lon = -3.1883
    start = datetime(2023, 1, 1)
    end = datetime(2023, 1, 10)

    # Mock the Daily class to return a predictable DataFrame
    mock_df = pd.DataFrame(
        {
            "time": pd.date_range(start=start, end=end),
            "tavg": [10.5, 11.2, 9.8, 10.1, 12.3, 11.7, 10.9, 9.5, 10.3, 11.0],
        }
    )

    with patch("src.fetch.Daily") as mock_daily:
        mock_daily.return_value.fetch.return_value = mock_df
        df = get_historical_weather(lat, lon, start, end)
        # Assert the returned DataFrame matches the mock
        pd.testing.assert_frame_equal(df, mock_df)
        # Assert fetch was called once
        mock_daily.return_value.fetch.assert_called_once_with()
        # Assert Daily was called with correct parameters
        mock_daily.assert_called_once_with(lat, lon, start, end)
