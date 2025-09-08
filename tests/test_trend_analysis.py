# tests/test_trend_analysis.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.trend_analysis import (
    calculate_linear_trend, 
    add_trend_lines_to_chart_data,
    get_trend_summary,
    _classify_trend_direction,
    _create_trend_description
)


def test_calculate_linear_trend_warming():
    """Test trend calculation for warming data."""
    # Create synthetic warming trend data
    dates = pd.Series(pd.date_range('2020-01-01', periods=100, freq='D'))
    values = pd.Series(10 + 0.05 * np.arange(100) + np.random.normal(0, 0.1, 100))
    
    result = calculate_linear_trend(dates, values)
    
    assert result['slope'] > 0, "Should detect warming trend"
    assert result['trend_direction'] == 'warming'
    assert len(result['trend_line']) == len(dates)
    assert result['valid_points'] == 100
    assert 'warming' in result['trend_description'].lower()


def test_calculate_linear_trend_cooling():
    """Test trend calculation for cooling data."""
    # Create synthetic cooling trend data
    dates = pd.Series(pd.date_range('2020-01-01', periods=100, freq='D'))
    values = pd.Series(10 - 0.05 * np.arange(100) + np.random.normal(0, 0.1, 100))
    
    result = calculate_linear_trend(dates, values)
    
    assert result['slope'] < 0, "Should detect cooling trend"
    assert result['trend_direction'] == 'cooling'
    assert 'cooling' in result['trend_description'].lower()


def test_calculate_linear_trend_stable():
    """Test trend calculation for stable data."""
    # Create synthetic stable data (just noise)
    dates = pd.Series(pd.date_range('2020-01-01', periods=50, freq='D'))
    values = pd.Series(10 + np.random.normal(0, 0.1, 50))
    
    result = calculate_linear_trend(dates, values)
    
    # With pure noise, trend should be weak/stable
    assert abs(result['slope']) < 0.01 or result['p_value'] > 0.05
    

def test_calculate_linear_trend_with_nans():
    """Test trend calculation with missing values."""
    dates = pd.Series(pd.date_range('2020-01-01', periods=10, freq='D'))
    values = pd.Series([1, 2, np.nan, 4, 5, np.nan, 7, 8, 9, 10])
    
    result = calculate_linear_trend(dates, values)
    
    assert result['valid_points'] == 8  # Should skip NaN values
    assert result['total_points'] == 10
    assert len(result['trend_line']) == 10


def test_calculate_linear_trend_insufficient_data():
    """Test trend calculation with insufficient data."""
    dates = pd.Series(pd.date_range('2020-01-01', periods=1, freq='D'))
    values = pd.Series([10])
    
    result = calculate_linear_trend(dates, values)
    
    assert result['valid_points'] == 0
    assert result['trend_direction'] == 'stable'
    assert 'Insufficient data' in result['trend_description']


def test_classify_trend_direction():
    """Test trend direction classification."""
    assert _classify_trend_direction(0.05, 0.01) == 'warming'
    assert _classify_trend_direction(-0.05, 0.01) == 'cooling'
    assert _classify_trend_direction(0.05, 0.1) == 'stable'  # Not significant
    assert _classify_trend_direction(0.0, 0.01) == 'stable'


def test_create_trend_description():
    """Test trend description generation."""
    desc = _create_trend_description(0.01, 0.8, 0.001, 100)
    assert 'warming' in desc.lower()
    assert 'strong' in desc.lower()
    assert '3.65°C/year' in desc  # 0.01 * 365.25
    
    desc = _create_trend_description(0.01, 0.5, 0.1, 50)
    assert 'No significant trend' in desc


def test_add_trend_lines_to_chart_data():
    """Test adding trend lines to chart data."""
    # Create test data
    dates = pd.date_range('2020-01-01', periods=10, freq='D')
    df = pd.DataFrame({
        'Date': dates,
        'Average Temperature (°C)': [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
        'Highest Temperature (°C)': [15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
        'Rainfall (mm)': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Non-temperature column
    })
    
    result_df = add_trend_lines_to_chart_data(df)
    
    # Should add trend columns for temperature data
    assert 'Average Temperature (°C) Trend' in result_df.columns
    assert 'Highest Temperature (°C) Trend' in result_df.columns
    assert 'Rainfall (mm) Trend' not in result_df.columns  # Should not add for non-temp
    
    # Should have trend metadata
    assert 'Average Temperature (°C)_trend_info' in result_df.attrs


def test_add_trend_lines_no_date_column():
    """Test adding trend lines when no Date column exists."""
    df = pd.DataFrame({
        'Temperature': [10, 11, 12],
        'Rainfall': [1, 2, 3]
    })
    
    result_df = add_trend_lines_to_chart_data(df)
    
    # Should return unchanged if no Date column
    pd.testing.assert_frame_equal(result_df, df)


def test_get_trend_summary():
    """Test getting trend summary for temperature columns."""
    dates = pd.date_range('2020-01-01', periods=10, freq='D')
    df = pd.DataFrame({
        'Date': dates,
        'Average Temperature (°C)': [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
        'Lowest Temperature (°C)': [5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
    })
    
    trends = get_trend_summary(df)
    
    assert 'Average Temperature (°C)' in trends
    assert 'Lowest Temperature (°C)' in trends
    assert trends['Average Temperature (°C)']['trend_direction'] == 'warming'
    assert trends['Lowest Temperature (°C)']['trend_direction'] == 'warming'


def test_get_trend_summary_no_date():
    """Test trend summary with no Date column."""
    df = pd.DataFrame({
        'Temperature': [10, 11, 12],
    })
    
    trends = get_trend_summary(df)
    
    assert trends == {}  # Should return empty dict if no Date column