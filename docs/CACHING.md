# Caching Configuration

The climate-compare application implements several caching layers to improve performance:

## Cache Types

### 1. Weather Data Cache (`fetch.py`)
- **Function**: `get_historical_weather()`
- **Type**: LRU Cache
- **Default Size**: 512 entries
- **Configurable**: Via `CLIMATE_WEATHER_CACHE_SIZE` environment variable
- **Purpose**: Caches weather API responses to avoid redundant Meteostat API calls

### 2. Compass Direction Cache (`formatters.py`)
- **Function**: `deg_to_compass()`
- **Type**: LRU Cache
- **Default Size**: 256 entries
- **Configurable**: Via `CLIMATE_COMPASS_CACHE_SIZE` environment variable
- **Purpose**: Caches compass direction calculations

### 3. Streamlit Data Cache (`streamlit_app.py`)
- **Function**: `_load_data()`
- **Type**: Streamlit cache_data
- **Default TTL**: 3600 seconds (1 hour)
- **Configurable**: Via `CLIMATE_STREAMLIT_TTL` environment variable
- **Purpose**: Caches processed data for the UI

## Environment Variables

Configure caching behavior with these environment variables:

```bash
# Weather data cache size (default: 512)
export CLIMATE_WEATHER_CACHE_SIZE=1024

# Compass cache size (default: 256)  
export CLIMATE_COMPASS_CACHE_SIZE=512

# Streamlit cache TTL in seconds (default: 3600)
export CLIMATE_STREAMLIT_TTL=7200

# Enable persistent caching (default: false)
export CLIMATE_ENABLE_PERSISTENT_CACHE=true

# Enable cache statistics display (default: true)
export CLIMATE_ENABLE_CACHE_STATS=true
```

## Cache Monitoring

When `CLIMATE_ENABLE_CACHE_STATS=true`, the application displays cache performance metrics in the sidebar:

- **Hit Rate**: Percentage of cache hits vs total requests
- **Cache Size**: Current entries vs maximum entries
- **Hits/Misses**: Raw cache statistics

## Cache Management

The application provides several cache management features:

### Clear Cache
Manually clear the weather data cache to force fresh data retrieval.

### Warm Cache
Pre-load cache with recent weather data for common locations (Edinburgh, London, Glasgow).

## API Functions

### `get_cache_info() -> dict`
Returns cache statistics:
```python
{
    "hits": 150,
    "misses": 50,
    "maxsize": 512,
    "currsize": 45
}
```

### `clear_weather_cache() -> None`
Clears the weather data cache.

### `warm_cache_for_common_locations() -> dict`
Pre-loads cache with data for common locations.

### `get_cache_config() -> dict`
Returns current cache configuration.

## Performance Impact

The caching improvements provide:

1. **Reduced API Calls**: Weather data is cached, reducing Meteostat API usage
2. **Faster Response Times**: Cached data loads instantly
3. **Improved User Experience**: Less waiting for repeated requests
4. **Configurable Behavior**: Tune cache sizes based on usage patterns

## Best Practices

1. **Monitor Hit Rates**: Aim for >80% cache hit rate
2. **Adjust Cache Sizes**: Increase if hit rates are low
3. **Use Cache Warming**: Pre-load data during low-traffic periods
4. **Monitor Memory Usage**: Large caches consume more memory