#!/usr/bin/env python3
"""CLI utility for managing the climate database."""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

try:
    from src.database import ClimateDatabase, DEFAULT_DB_PATH
except ImportError:
    # Handle running from different directories
    sys.path.append(str(Path(__file__).parent / "src"))
    from database import ClimateDatabase, DEFAULT_DB_PATH  # type: ignore


def init_database(db_path: Path) -> None:
    """Initialize a new database."""
    if db_path.exists():
        response = input(f"Database {db_path} already exists. Recreate? (y/N): ")
        if response.lower() != "y":
            print("Initialization cancelled.")
            return
        db_path.unlink()
    
    db = ClimateDatabase(db_path)
    print(f"Database initialized at {db_path}")


def database_info(db_path: Path) -> None:
    """Show information about the database."""
    if not db_path.exists():
        print(f"Database {db_path} does not exist.")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Get table info
            cursor = conn.execute("""
                SELECT COUNT(*) FROM weather_data
            """)
            total_records = cursor.fetchone()[0]
            
            # Get location count
            cursor = conn.execute("""
                SELECT COUNT(DISTINCT latitude || ',' || longitude) FROM weather_data
            """)
            unique_locations = cursor.fetchone()[0]
            
            # Get date range
            cursor = conn.execute("""
                SELECT MIN(time), MAX(time) FROM weather_data
            """)
            date_range = cursor.fetchone()
            
            print(f"Database: {db_path}")
            print(f"Total records: {total_records}")
            print(f"Unique locations: {unique_locations}")
            if date_range[0] and date_range[1]:
                print(f"Date range: {date_range[0]} to {date_range[1]}")
            else:
                print("No weather data found.")
                
    except Exception as e:
        print(f"Error reading database: {e}")


def list_locations(db_path: Path) -> None:
    """List all locations in the database."""
    if not db_path.exists():
        print(f"Database {db_path} does not exist.")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    latitude, 
                    longitude, 
                    COUNT(*) as record_count,
                    MIN(time) as earliest,
                    MAX(time) as latest
                FROM weather_data 
                GROUP BY latitude, longitude
                ORDER BY record_count DESC
            """)
            
            print("Locations in database:")
            print("Lat      Lon       Records  Date Range")
            print("-" * 50)
            
            for row in cursor:
                lat, lon, count, earliest, latest = row
                print(f"{lat:8.4f} {lon:9.4f} {count:7d}  {earliest} to {latest}")
                
    except Exception as e:
        print(f"Error reading database: {e}")


def clean_database(db_path: Path) -> None:
    """Clean up duplicate or old records."""
    if not db_path.exists():
        print(f"Database {db_path} does not exist.")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Remove exact duplicates (keep the most recent)
            cursor = conn.execute("""
                DELETE FROM weather_data 
                WHERE id NOT IN (
                    SELECT MAX(id) 
                    FROM weather_data 
                    GROUP BY latitude, longitude, time
                )
            """)
            duplicates_removed = cursor.rowcount
            
            # Vacuum to reclaim space
            conn.execute("VACUUM")
            conn.commit()
            
            print(f"Removed {duplicates_removed} duplicate records")
            print("Database cleaned and compacted")
            
    except Exception as e:
        print(f"Error cleaning database: {e}")


def main() -> None:
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Manage climate database")
    parser.add_argument(
        "--db", 
        type=Path, 
        default=DEFAULT_DB_PATH,
        help=f"Database path (default: {DEFAULT_DB_PATH})"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Init command
    subparsers.add_parser("init", help="Initialize a new database")
    
    # Info command
    subparsers.add_parser("info", help="Show database information")
    
    # List command
    subparsers.add_parser("locations", help="List all locations in database")
    
    # Clean command
    subparsers.add_parser("clean", help="Clean up duplicate records")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "init":
        init_database(args.db)
    elif args.command == "info":
        database_info(args.db)
    elif args.command == "locations":
        list_locations(args.db)
    elif args.command == "clean":
        clean_database(args.db)


if __name__ == "__main__":
    main()