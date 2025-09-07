import os
from unittest.mock import patch

from src.cache_config import (
    DEFAULT_WEATHER_CACHE_SIZE,
    DEFAULT_COMPASS_CACHE_SIZE,
    DEFAULT_STREAMLIT_TTL,
    get_cache_config,
    WEATHER_CACHE_SIZE,
    COMPASS_CACHE_SIZE,
    STREAMLIT_CACHE_TTL,
)


def test_default_cache_sizes():
    """Test that default cache sizes are reasonable."""
    assert DEFAULT_WEATHER_CACHE_SIZE == 512
    assert DEFAULT_COMPASS_CACHE_SIZE == 256
    assert DEFAULT_STREAMLIT_TTL == 3600


def test_get_cache_config():
    """Test that cache config returns expected structure."""
    config = get_cache_config()
    
    required_keys = {
        "weather_cache_size",
        "compass_cache_size", 
        "streamlit_cache_ttl",
        "enable_persistent_cache",
        "enable_cache_stats",
    }
    
    assert isinstance(config, dict)
    assert required_keys.issubset(set(config.keys()))
    assert isinstance(config["weather_cache_size"], int)
    assert isinstance(config["compass_cache_size"], int)
    assert isinstance(config["streamlit_cache_ttl"], int)
    assert isinstance(config["enable_persistent_cache"], bool)
    assert isinstance(config["enable_cache_stats"], bool)


def test_environment_variable_override():
    """Test that environment variables override default values."""
    with patch.dict(os.environ, {
        "CLIMATE_WEATHER_CACHE_SIZE": "1024",
        "CLIMATE_COMPASS_CACHE_SIZE": "512",
        "CLIMATE_STREAMLIT_TTL": "7200",
    }):
        # Re-import to pick up new env vars
        import importlib
        import src.cache_config
        importlib.reload(src.cache_config)
        
        assert src.cache_config.WEATHER_CACHE_SIZE == 1024
        assert src.cache_config.COMPASS_CACHE_SIZE == 512
        assert src.cache_config.STREAMLIT_CACHE_TTL == 7200


def test_cache_sizes_are_positive():
    """Test that all cache sizes are positive integers."""
    assert WEATHER_CACHE_SIZE > 0
    assert COMPASS_CACHE_SIZE > 0
    assert STREAMLIT_CACHE_TTL > 0