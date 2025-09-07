"""Tests for database functionality."""
from __future__ import annotations

import sqlite3
import tempfile
from datetime import date
from pathlib import Path

import pandas as pd

from src.database import ClimateDatabase


def test_database_initialization():
    """Test that database initializes correctly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = ClimateDatabase(db_path)
        
        # Check that database file was created
        assert db_path.exists()
        
        # Check that table was created
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='weather_data'"
            )
            assert cursor.fetchone() is not None


def test_store_and_retrieve_weather_data():
    """Test storing and retrieving weather data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = ClimateDatabase(db_path)
        
        # Create sample weather data
        sample_data = {
            "time": pd.date_range("2023-01-01", periods=3, freq="D"),
            "tavg": [10.5, 12.0, 8.5],
            "tmin": [5.0, 7.0, 3.0],
            "tmax": [16.0, 17.0, 14.0],
            "prcp": [0.0, 2.5, 0.0],
        }
        df = pd.DataFrame(sample_data)
        df = df.set_index("time")
        
        # Store the data
        lat, lon = 55.9533, -3.1883  # Edinburgh
        records_stored = db.store_weather_data(lat, lon, df)
        assert records_stored == 3
        
        # Retrieve the data
        start_date = date(2023, 1, 1)
        end_date = date(2023, 1, 3)
        retrieved_df = db.get_weather_data(lat, lon, start_date, end_date)
        
        assert retrieved_df is not None
        assert len(retrieved_df) == 3
        assert "tavg" in retrieved_df.columns
        assert retrieved_df["tavg"].iloc[0] == 10.5


def test_get_data_coverage():
    """Test data coverage functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = ClimateDatabase(db_path)
        
        # Check coverage for empty database
        lat, lon = 55.9533, -3.1883
        coverage = db.get_data_coverage(lat, lon)
        assert coverage["record_count"] == 0
        assert not coverage["has_data"]
        
        # Add some data
        sample_data = {
            "time": pd.date_range("2023-01-01", periods=2, freq="D"),
            "tavg": [10.5, 12.0],
        }
        df = pd.DataFrame(sample_data).set_index("time")
        db.store_weather_data(lat, lon, df)
        
        # Check coverage after adding data
        coverage = db.get_data_coverage(lat, lon)
        assert coverage["record_count"] == 2
        assert coverage["has_data"]
        assert coverage["earliest_date"] == "2023-01-01"
        assert coverage["latest_date"] == "2023-01-02"


def test_location_tolerance():
    """Test location tolerance functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = ClimateDatabase(db_path)
        
        # Store data at a specific location
        lat, lon = 55.9533, -3.1883
        sample_data = {
            "time": pd.date_range("2023-01-01", periods=1, freq="D"),
            "tavg": [10.5],
        }
        df = pd.DataFrame(sample_data).set_index("time")
        db.store_weather_data(lat, lon, df)
        
        # Try to retrieve with slightly different coordinates (within tolerance)
        nearby_lat, nearby_lon = 55.9540, -3.1890  # About 100m away
        start_date = date(2023, 1, 1)
        end_date = date(2023, 1, 1)
        
        retrieved_df = db.get_weather_data(nearby_lat, nearby_lon, start_date, end_date)
        assert retrieved_df is not None
        assert len(retrieved_df) == 1


if __name__ == "__main__":
    test_database_initialization()
    test_store_and_retrieve_weather_data()
    test_get_data_coverage()
    test_location_tolerance()
    print("All database tests passed!")