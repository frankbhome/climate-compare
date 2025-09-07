"""Database module for storing and retrieving climate data."""
from __future__ import annotations

import logging
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)

# Default database path
DEFAULT_DB_PATH = Path("climate_data.db")


class ClimateDatabase:
    """SQLite database for storing climate/weather data."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the database connection.
        
        Args:
            db_path: Path to SQLite database file. Defaults to 'climate_data.db'.
        """
        self.db_path = db_path or DEFAULT_DB_PATH
        self._ensure_database_exists()

    def _ensure_database_exists(self) -> None:
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS weather_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    time TEXT NOT NULL,
                    tavg REAL,
                    tmin REAL,
                    tmax REAL,
                    prcp REAL,
                    snow REAL,
                    wdir REAL,
                    wspd REAL,
                    wpgt REAL,
                    pres REAL,
                    tsun REAL,
                    created_at TEXT NOT NULL,
                    UNIQUE(latitude, longitude, time)
                )
            """)
            
            # Create index for faster queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_weather_location_time 
                ON weather_data(latitude, longitude, time)
            """)
            
            conn.commit()

    def store_weather_data_raw(
        self, 
        lat: float, 
        lon: float, 
        weather_records: List[Dict[str, Any]]
    ) -> int:
        """Store weather data in the database using raw Python data structures.
        
        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees  
            weather_records: List of dictionaries with weather data
            
        Returns:
            Number of records stored
        """
        if not weather_records:
            return 0
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                records_stored = 0
                current_time = datetime.now().isoformat()
                
                for record in weather_records:
                    # Prepare record for insertion
                    time_str = record.get("time", "")
                    if isinstance(time_str, datetime):
                        time_str = time_str.strftime("%Y-%m-%d")
                    elif isinstance(time_str, date):
                        time_str = time_str.strftime("%Y-%m-%d")
                    
                    try:
                        conn.execute("""
                            INSERT OR REPLACE INTO weather_data 
                            (latitude, longitude, time, tavg, tmin, tmax, prcp, snow, 
                             wdir, wspd, wpgt, pres, tsun, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, [
                            lat, lon, time_str,
                            record.get("tavg"), record.get("tmin"), record.get("tmax"),
                            record.get("prcp"), record.get("snow"), record.get("wdir"),
                            record.get("wspd"), record.get("wpgt"), record.get("pres"),
                            record.get("tsun"), current_time
                        ])
                        records_stored += 1
                    except sqlite3.IntegrityError:
                        # Record already exists, skip
                        pass
                
                conn.commit()
                logger.info(
                    "Stored %d weather records for lat=%.4f, lon=%.4f", 
                    records_stored, lat, lon
                )
                return records_stored
                
        except Exception as e:
            logger.error("Failed to store weather data: %s", e)
            return 0

    def get_weather_data_raw(
        self, 
        lat: float, 
        lon: float, 
        start_date: date, 
        end_date: date,
        tolerance: float = 0.01
    ) -> Optional[List[Dict[str, Any]]]:
        """Retrieve weather data from the database as raw Python data structures.
        
        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            start_date: Start date for data retrieval
            end_date: End date for data retrieval
            tolerance: Location tolerance in degrees (default 0.01 ≈ 1km)
            
        Returns:
            List of dictionaries with weather data or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Set row factory to get dict-like results
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute("""
                    SELECT time, tavg, tmin, tmax, prcp, snow, wdir, wspd, wpgt, pres, tsun
                    FROM weather_data 
                    WHERE ABS(latitude - ?) <= ? 
                      AND ABS(longitude - ?) <= ?
                      AND time >= ? 
                      AND time <= ?
                    ORDER BY time
                """, [
                    lat, tolerance, 
                    lon, tolerance,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d")
                ])
                
                records = []
                for row in cursor:
                    record = dict(row)
                    # Convert time string back to datetime
                    record["time"] = datetime.strptime(record["time"], "%Y-%m-%d")
                    records.append(record)
                
                if not records:
                    return None
                
                logger.info(
                    "Retrieved %d weather records for lat=%.4f, lon=%.4f", 
                    len(records), lat, lon
                )
                return records
                
        except Exception as e:
            logger.error("Failed to retrieve weather data: %s", e)
            return None

    def get_data_coverage(self, lat: float, lon: float, tolerance: float = 0.01) -> dict:
        """Get information about data coverage for a location.
        
        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            tolerance: Location tolerance in degrees
            
        Returns:
            Dictionary with coverage information
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT 
                        COUNT(*) as record_count,
                        MIN(time) as earliest_date,
                        MAX(time) as latest_date
                    FROM weather_data 
                    WHERE ABS(latitude - ?) <= ? 
                      AND ABS(longitude - ?) <= ?
                """
                
                cursor = conn.execute(query, [lat, tolerance, lon, tolerance])
                row = cursor.fetchone()
                
                return {
                    "record_count": row[0] if row else 0,
                    "earliest_date": row[1] if row and row[1] else None,
                    "latest_date": row[2] if row and row[2] else None,
                    "has_data": (row[0] if row else 0) > 0
                }
                
        except Exception as e:
            logger.error("Failed to get data coverage: %s", e)
            return {"record_count": 0, "has_data": False}

    def store_weather_data(self, lat: float, lon: float, df) -> int:
        """Store weather data from a pandas DataFrame (when pandas is available).
        
        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees  
            df: DataFrame-like object with weather data
            
        Returns:
            Number of records stored
        """
        try:
            # Try to handle pandas DataFrame if available
            weather_records = []
            
            # Check if it has pandas-like interface
            if hasattr(df, 'iterrows'):
                # Pandas DataFrame
                df_copy = df.copy()
                
                # Ensure time column exists
                if "time" not in df_copy.columns and hasattr(df_copy.index, 'strftime'):
                    df_copy = df_copy.reset_index()
                
                for _, row in df_copy.iterrows():
                    record = {}
                    # Handle time column
                    if "time" in row:
                        record["time"] = row["time"]
                    elif hasattr(df_copy.index, 'strftime'):
                        record["time"] = row.name  # Use index as time
                    
                    # Copy all weather columns
                    for col in ["tavg", "tmin", "tmax", "prcp", "snow", "wdir", "wspd", "wpgt", "pres", "tsun"]:
                        if col in row:
                            val = row[col]
                            # Handle pandas NA/NaN values
                            if hasattr(val, 'isna') and val.isna():
                                record[col] = None
                            elif str(val).lower() in ['nan', 'none', '']:
                                record[col] = None
                            else:
                                record[col] = float(val) if val is not None else None
                    
                    weather_records.append(record)
            
            elif isinstance(df, list):
                # Already a list of records
                weather_records = df
            
            else:
                # Try to convert dict-like object
                weather_records = [dict(df)]
            
            return self.store_weather_data_raw(lat, lon, weather_records)
            
        except Exception as e:
            logger.error("Failed to store weather data: %s", e)
            return 0

    def get_weather_data(self, lat: float, lon: float, start_date: date, end_date: date, tolerance: float = 0.01):
        """Retrieve weather data as pandas-compatible format (when pandas is available).
        
        Returns a pandas DataFrame if pandas is available, otherwise returns raw data.
        """
        records = self.get_weather_data_raw(lat, lon, start_date, end_date, tolerance)
        
        if records is None:
            return None
        
        # Try to import pandas and return DataFrame if available
        try:
            import pandas as pd
            df = pd.DataFrame(records)
            if "time" in df.columns:
                df["time"] = pd.to_datetime(df["time"])
                df = df.set_index("time")
            return df
        except ImportError:
            # Return raw data if pandas not available
            return records

    def close(self) -> None:
        """Close database connection (SQLite auto-closes, but kept for interface)."""
        pass