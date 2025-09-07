# Climate Database Backend

This document describes the backend database system for storing and retrieving climate datasets in the Climate Compare application.

## Overview

The climate database provides persistent storage for weather data fetched from external APIs (like Meteostat). This reduces API calls, improves performance, and enables offline operation for previously fetched data.

## Features

- **SQLite Database**: Lightweight, file-based database requiring no external server
- **Automatic Fallback**: Checks database first, falls back to API if data not found
- **Location Tolerance**: Finds nearby weather stations within configurable distance
- **Data Deduplication**: Prevents duplicate records for same location/date
- **Coverage Reporting**: Shows what data is available in the database
- **Management Tools**: CLI utilities for database administration

## Database Schema

### weather_data Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| latitude | REAL | Latitude in decimal degrees |
| longitude | REAL | Longitude in decimal degrees |
| time | TEXT | Date in YYYY-MM-DD format |
| tavg | REAL | Average temperature (°C) |
| tmin | REAL | Minimum temperature (°C) |
| tmax | REAL | Maximum temperature (°C) |
| prcp | REAL | Precipitation (mm) |
| snow | REAL | Snowfall (mm) |
| wdir | REAL | Wind direction (degrees) |
| wspd | REAL | Wind speed (km/h) |
| wpgt | REAL | Wind gust speed (km/h) |
| pres | REAL | Air pressure (hPa) |
| tsun | REAL | Sunshine duration (hours) |
| created_at | TEXT | Timestamp when record was created |

### Indexes

- `idx_weather_location_time`: Composite index on (latitude, longitude, time) for fast queries

## Usage

### Basic Usage

The database integration is automatic. When you fetch weather data using the existing `get_historical_weather()` function, it will:

1. Check the database for existing data
2. Return cached data if available
3. Fetch from API if not in database
4. Store API results in database for future use

```python
from src.fetch import get_historical_weather
from datetime import date

# This will check database first, then API if needed
df = get_historical_weather(
    lat=55.9533, 
    lon=-3.1883, 
    start=date(2023, 1, 1), 
    end=date(2023, 1, 10)
)
```

### Direct Database Access

```python
from src.database import ClimateDatabase
from datetime import date

db = ClimateDatabase()

# Check data coverage
coverage = db.get_data_coverage(55.9533, -3.1883)
print(f"Records available: {coverage['record_count']}")

# Retrieve data directly
data = db.get_weather_data(
    lat=55.9533, 
    lon=-3.1883,
    start_date=date(2023, 1, 1),
    end_date=date(2023, 1, 10)
)
```

### Database Management

Use the `manage_db.py` script for database administration:

```bash
# Initialize a new database
python manage_db.py init

# Show database information
python manage_db.py info

# List all locations with data
python manage_db.py locations

# Clean up duplicate records
python manage_db.py clean
```

## Configuration

### Database Location

By default, the database is stored as `climate_data.db` in the project root. You can specify a different location:

```python
from pathlib import Path
from src.database import ClimateDatabase

db = ClimateDatabase(Path("/path/to/my/database.db"))
```

### Location Tolerance

When querying by coordinates, the system uses a tolerance to find nearby data. Default is 0.01 degrees (~1km):

```python
# Find data within 5km (0.05 degrees)
data = db.get_weather_data(
    lat=55.9533, 
    lon=-3.1883,
    start_date=date(2023, 1, 1),
    end_date=date(2023, 1, 10),
    tolerance=0.05
)
```

## Integration with Existing Code

The database is integrated transparently with the existing codebase:

- **fetch.py**: Modified to check database before API calls
- **Streamlit app**: Works unchanged, benefits from faster data access
- **Caching**: Works alongside existing @lru_cache for memory caching

## Dependencies

- **Core**: Python 3.11+ with built-in sqlite3 module
- **Optional**: pandas (for DataFrame compatibility when available)
- **Optional**: meteostat (for API fallback functionality)

The database module is designed to work with or without pandas/meteostat, making it resilient to dependency issues.

## Performance Benefits

1. **Reduced API Calls**: Previously fetched data served from database
2. **Faster Response**: Local database queries are much faster than API calls
3. **Offline Operation**: Can work with cached data when API is unavailable
4. **Reduced Bandwidth**: No need to re-download the same data

## File Structure

```
src/
├── database.py          # Core database functionality
├── fetch.py            # Modified to use database first
└── ...

tests/
├── test_database.py        # Comprehensive database tests
├── test_database_simple.py # Basic tests without pandas
└── ...

manage_db.py            # Database management CLI tool
climate_data.db         # SQLite database file (created automatically)
```

## Error Handling

The database system includes comprehensive error handling:

- **Database Creation**: Automatically creates database and tables on first use
- **Connection Errors**: Gracefully handles database connection issues
- **Data Validation**: Validates data before insertion
- **API Fallback**: Falls back to API if database queries fail

## Future Enhancements

Potential improvements for future development:

1. **Data Compression**: Compress older records to save space
2. **Background Updates**: Periodic updates of existing data
3. **Data Export**: Export data to CSV/JSON formats
4. **Backup/Restore**: Database backup and restoration tools
5. **Analytics**: Built-in data analysis and reporting features