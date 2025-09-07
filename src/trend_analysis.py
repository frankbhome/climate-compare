# src/trend_analysis.py
"""
Trend analysis utilities for climate data.
Provides functions to calculate regression lines and trend indicators.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from typing import Tuple, Dict, Any


def calculate_linear_trend(dates: pd.Series, values: pd.Series) -> Dict[str, Any]:
    """
    Calculate linear trend for time series data.
    
    Args:
        dates: Pandas Series of datetime values
        values: Pandas Series of numeric values
    
    Returns:
        Dictionary containing trend statistics:
        - slope: trend slope per day
        - intercept: y-intercept
        - r_value: correlation coefficient
        - p_value: statistical significance
        - std_err: standard error
        - trend_line: Series with trend line values
        - trend_direction: 'warming', 'cooling', or 'stable'
        - trend_description: human-readable description
    """
    # Filter out NaN values
    valid_mask = ~(pd.isna(dates) | pd.isna(values))
    if valid_mask.sum() < 2:
        return _empty_trend_result(dates)
    
    clean_dates = dates[valid_mask]
    clean_values = values[valid_mask]
    
    # Convert dates to numeric (days since first date)
    date_numeric = (clean_dates - clean_dates.min()).dt.total_seconds() / (24 * 3600)
    
    # Calculate linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(date_numeric, clean_values)
    
    # Generate trend line for all original dates
    all_date_numeric = (dates - clean_dates.min()).dt.total_seconds() / (24 * 3600)
    trend_line = pd.Series(slope * all_date_numeric + intercept, index=dates)
    
    # Determine trend direction
    trend_direction = _classify_trend_direction(slope, p_value)
    
    # Create human-readable description
    trend_description = _create_trend_description(slope, r_value, p_value, len(clean_dates))
    
    return {
        'slope': slope,
        'intercept': intercept,
        'r_value': r_value,
        'p_value': p_value,
        'std_err': std_err,
        'trend_line': trend_line,
        'trend_direction': trend_direction,
        'trend_description': trend_description,
        'valid_points': len(clean_values),
        'total_points': len(dates)
    }


def _empty_trend_result(dates: pd.Series) -> Dict[str, Any]:
    """Return empty trend result when insufficient data."""
    return {
        'slope': 0.0,
        'intercept': 0.0,
        'r_value': 0.0,
        'p_value': 1.0,
        'std_err': 0.0,
        'trend_line': pd.Series([np.nan] * len(dates), index=dates),
        'trend_direction': 'stable',
        'trend_description': 'Insufficient data for trend analysis',
        'valid_points': 0,
        'total_points': len(dates)
    }


def _classify_trend_direction(slope: float, p_value: float, significance_level: float = 0.05) -> str:
    """Classify trend direction based on slope and statistical significance."""
    if p_value > significance_level:
        return 'stable'
    
    if slope > 0:
        return 'warming'
    elif slope < 0:
        return 'cooling'
    else:
        return 'stable'


def _create_trend_description(slope: float, r_value: float, p_value: float, n_points: int) -> str:
    """Create human-readable trend description."""
    # Convert slope from per-day to per-year for better readability
    slope_per_year = slope * 365.25
    
    if p_value > 0.05:
        return f"No significant trend (p={p_value:.3f})"
    
    direction = "warming" if slope > 0 else "cooling"
    strength = "strong" if abs(r_value) > 0.7 else "moderate" if abs(r_value) > 0.4 else "weak"
    
    return (f"{strength.title()} {direction} trend: "
            f"{abs(slope_per_year):.2f}°C/year "
            f"(r={r_value:.3f}, p={p_value:.3f}, n={n_points})")


def add_trend_lines_to_chart_data(chart_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add trend line columns to chart DataFrame for temperature data.
    
    Args:
        chart_df: DataFrame with Date column and temperature columns
        
    Returns:
        DataFrame with additional trend line columns
    """
    if "Date" not in chart_df.columns:
        return chart_df
    
    df = chart_df.copy()
    
    # Add trend lines for temperature columns
    temp_columns = [
        "Average Temperature (°C)",
        "Lowest Temperature (°C)", 
        "Highest Temperature (°C)"
    ]
    
    for col in temp_columns:
        if col in df.columns:
            trend_result = calculate_linear_trend(df["Date"], df[col])
            trend_col_name = f"{col} Trend"
            df[trend_col_name] = trend_result['trend_line']
            
            # Store trend metadata for potential UI display
            df.attrs[f"{col}_trend_info"] = {
                'direction': trend_result['trend_direction'],
                'description': trend_result['trend_description'],
                'slope_per_year': trend_result['slope'] * 365.25,
                'r_value': trend_result['r_value'],
                'p_value': trend_result['p_value']
            }
    
    return df


def get_trend_summary(chart_df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Get summary of trends for all temperature columns.
    
    Args:
        chart_df: DataFrame with Date column and temperature columns
        
    Returns:
        Dictionary mapping column names to trend information
    """
    if "Date" not in chart_df.columns:
        return {}
    
    temp_columns = [
        "Average Temperature (°C)",
        "Lowest Temperature (°C)", 
        "Highest Temperature (°C)"
    ]
    
    trends = {}
    
    for col in temp_columns:
        if col in chart_df.columns:
            trend_result = calculate_linear_trend(chart_df["Date"], chart_df[col])
            trends[col] = trend_result
    
    return trends