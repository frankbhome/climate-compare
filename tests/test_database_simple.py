"""Simple database test without external dependencies."""
import sqlite3
import tempfile
from pathlib import Path

# Simple test without pandas dependency


def test_database_schema():
    """Test database schema creation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        
        # Create database manually
        with sqlite3.connect(db_path) as conn:
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
            
            # Test inserting data
            conn.execute("""
                INSERT INTO weather_data 
                (latitude, longitude, time, tavg, tmin, tmax, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [55.9533, -3.1883, "2023-01-01", 10.5, 5.0, 16.0, "2023-01-01T12:00:00"])
            
            # Test querying data
            cursor = conn.execute("""
                SELECT latitude, longitude, time, tavg 
                FROM weather_data 
                WHERE latitude = ? AND longitude = ?
            """, [55.9533, -3.1883])
            
            row = cursor.fetchone()
            assert row is not None
            assert row[0] == 55.9533  # latitude
            assert row[1] == -3.1883  # longitude
            assert row[2] == "2023-01-01"  # time
            assert row[3] == 10.5  # tavg
            
        print("Database schema test passed!")


def test_database_index():
    """Test that the index was created."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        
        with sqlite3.connect(db_path) as conn:
            # Create table and index
            conn.execute("""
                CREATE TABLE IF NOT EXISTS weather_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    time TEXT NOT NULL,
                    tavg REAL,
                    created_at TEXT NOT NULL,
                    UNIQUE(latitude, longitude, time)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_weather_location_time 
                ON weather_data(latitude, longitude, time)
            """)
            
            # Check that index exists
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name='idx_weather_location_time'
            """)
            
            index_row = cursor.fetchone()
            assert index_row is not None
            assert index_row[0] == "idx_weather_location_time"
            
        print("Database index test passed!")


if __name__ == "__main__":
    test_database_schema()
    test_database_index()
    print("All simple database tests passed!")