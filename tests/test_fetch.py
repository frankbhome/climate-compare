from datetime import datetime
from unittest.mock import ANY, patch

import pandas as pd

from src.fetch import get_historical_weather, get_cache_info, clear_weather_cache


def test_get_historical_weather_returns_dataframe():
    """
    Tests that get_historical_weather returns the expected DataFrame with
    temperature data for a given location and date range.
    """
    lat = 55.9533  # Edinburgh
    lon = -3.1883
    start = datetime(2023, 1, 1)
    end = datetime(2023, 1, 10)

    mock_df = pd.DataFrame(
        {
            "time": pd.date_range(start=start, end=end),
            "tavg": [10.5, 11.2, 9.8, 10.1, 12.3, 11.7, 10.9, 9.5, 10.3, 11.0],
        }
    )

    with patch("src.fetch.Daily") as mock_daily:
        mock_daily.return_value.fetch.return_value = mock_df
        df = get_historical_weather(lat, lon, start, end)

        pd.testing.assert_frame_equal(df, mock_df)
        mock_daily.return_value.fetch.assert_called_once_with()
        mock_daily.assert_called_once_with(ANY, start, end)  # Match Point


def test_cache_info_structure():
    """Test that cache info returns expected structure."""
    cache_info = get_cache_info()
    
    required_keys = {"hits", "misses", "maxsize", "currsize"}
    assert isinstance(cache_info, dict)
    assert required_keys.issubset(set(cache_info.keys()))
    
    # All values should be integers
    for key, value in cache_info.items():
        assert isinstance(value, int), f"{key} should be an integer"
        assert value >= 0, f"{key} should be non-negative"


def test_clear_weather_cache():
    """Test that cache clearing works."""
    # Clear cache to start fresh
    clear_weather_cache()
    
    initial_info = get_cache_info()
    assert initial_info["hits"] == 0
    assert initial_info["misses"] == 0
    assert initial_info["currsize"] == 0
    
    # Make a call that should add to cache
    with patch("src.fetch.Daily") as mock_daily:
        mock_df = pd.DataFrame({"time": [datetime.now()], "tavg": [10.0]})
        mock_daily.return_value.fetch.return_value = mock_df
        
        get_historical_weather(55.9533, -3.1883, datetime(2023, 1, 1), datetime(2023, 1, 2))
        
        after_call_info = get_cache_info()
        assert after_call_info["currsize"] == 1
        
        # Clear cache again
        clear_weather_cache()
        
        final_info = get_cache_info()
        assert final_info["currsize"] == 0
