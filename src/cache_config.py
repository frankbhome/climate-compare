# src/cache_config.py
"""
Caching configuration and utilities for the climate-compare application.
"""
from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# Cache configuration constants
DEFAULT_WEATHER_CACHE_SIZE = 512
DEFAULT_COMPASS_CACHE_SIZE = 256
DEFAULT_STREAMLIT_TTL = 3600  # 1 hour in seconds

# Environment-based configuration
WEATHER_CACHE_SIZE = int(
    os.getenv("CLIMATE_WEATHER_CACHE_SIZE", DEFAULT_WEATHER_CACHE_SIZE)
)
COMPASS_CACHE_SIZE = int(
    os.getenv("CLIMATE_COMPASS_CACHE_SIZE", DEFAULT_COMPASS_CACHE_SIZE)
)
STREAMLIT_CACHE_TTL = int(
    os.getenv("CLIMATE_STREAMLIT_TTL", DEFAULT_STREAMLIT_TTL)
)

# Enable/disable caching features
ENABLE_PERSISTENT_CACHE = os.getenv("CLIMATE_ENABLE_PERSISTENT_CACHE", "false").lower() == "true"
ENABLE_CACHE_STATS = os.getenv("CLIMATE_ENABLE_CACHE_STATS", "true").lower() == "true"


def get_cache_config() -> dict[str, Any]:
    """
    Get current cache configuration.
    
    Returns:
        dict: Current cache configuration settings
    """
    return {
        "weather_cache_size": WEATHER_CACHE_SIZE,
        "compass_cache_size": COMPASS_CACHE_SIZE,
        "streamlit_cache_ttl": STREAMLIT_CACHE_TTL,
        "enable_persistent_cache": ENABLE_PERSISTENT_CACHE,
        "enable_cache_stats": ENABLE_CACHE_STATS,
    }


def log_cache_config() -> None:
    """Log current cache configuration."""
    config = get_cache_config()
    logger.info("Cache configuration: %s", config)


# Export configuration for easy import
__all__ = [
    "WEATHER_CACHE_SIZE",
    "COMPASS_CACHE_SIZE", 
    "STREAMLIT_CACHE_TTL",
    "ENABLE_PERSISTENT_CACHE",
    "ENABLE_CACHE_STATS",
    "get_cache_config",
    "log_cache_config",
]