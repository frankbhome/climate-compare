#!/usr/bin/env python3
# Test the trend analysis functionality without streamlit
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fetch import get_historical_weather
from formatters import COLUMN_MAP, build_user_view
from trend_analysis import add_trend_lines_to_chart_data, get_trend_summary

def test_integration():
    print("Testing climate trend analysis integration...")
    
    # Test with mock data
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 2, 28)  # Two months for better trend detection
    
    print(f"Fetching data from {start_date.date()} to {end_date.date()}...")
    df = get_historical_weather(55.9533, -3.1883, start_date, end_date)
    
    if df is None or df.empty:
        print("ERROR: No data returned")
        return False
    
    print(f"Data loaded successfully: {len(df)} rows")
    print("Columns:", list(df.columns))
    
    # Prepare chart data
    chart_df = df.copy()
    if "time" not in chart_df.columns and isinstance(chart_df.index, pd.DatetimeIndex):
        chart_df = chart_df.reset_index()
        # The index becomes a column named 'time' after reset_index with DatetimeIndex
        if chart_df.columns[0] != 'time':
            # If the first column is the datetime, rename it to time
            chart_df = chart_df.rename(columns={chart_df.columns[0]: 'time'})
    
    chart_df = chart_df.rename(columns=COLUMN_MAP)
    if "Date" not in chart_df.columns and "time" in chart_df.columns:
        chart_df["Date"] = pd.to_datetime(chart_df["time"], errors="coerce")
        chart_df = chart_df.drop(columns=["time"])
    
    print("Chart df columns after processing:", list(chart_df.columns))
    print("Chart df sample:")
    print(chart_df.head())
    
    if "Date" in chart_df.columns:
        chart_df = chart_df.sort_values("Date")
        
        print("\nAdding trend lines...")
        chart_df_with_trends = add_trend_lines_to_chart_data(chart_df)
        
        print("Columns after adding trends:", list(chart_df_with_trends.columns))
        
        # Get trend summary
        trend_summary = get_trend_summary(chart_df_with_trends)
        
        print("\nTrend Analysis Summary:")
        print("-" * 50)
        
        for temp_col, trend_info in trend_summary.items():
            print(f"\n{temp_col}:")
            print(f"  Direction: {trend_info['trend_direction']}")
            print(f"  Slope: {trend_info['slope'] * 365.25:.3f}°C/year")
            print(f"  Correlation: {trend_info['r_value']:.3f}")
            print(f"  P-value: {trend_info['p_value']:.3f}")
            print(f"  Description: {trend_info['trend_description']}")
        
        print("\nTrend analysis integration test PASSED!")
        return True
    else:
        print("ERROR: No Date column found")
        return False

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)