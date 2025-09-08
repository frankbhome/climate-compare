#!/usr/bin/env python3
# Demo script to show trend analysis functionality working
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from trend_analysis import add_trend_lines_to_chart_data, get_trend_summary

def create_demo_data():
    """Create demonstration data with a clear warming trend."""
    print("Creating demonstration weather data with warming trend...")
    
    # Generate 2 years of daily data with a warming trend
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2023, 12, 31)
    dates = pd.date_range(start_date, end_date, freq='D')
    
    # Create a warming trend: 2°C per year with seasonal variation
    days_since_start = (dates - dates[0]).days
    base_temp = 10.0  # Base temperature
    warming_rate = 2.0 / 365.25  # 2°C per year warming
    
    # Add seasonal pattern (sinusoidal)
    seasonal_pattern = 10 * np.sin(2 * np.pi * days_since_start / 365.25 - np.pi/2)
    
    # Add warming trend
    trend = warming_rate * days_since_start
    
    # Add random noise
    np.random.seed(42)
    noise = np.random.normal(0, 2, len(dates))
    
    # Combine all components
    avg_temp = base_temp + seasonal_pattern + trend + noise
    
    # Create min/max temperatures
    daily_range = np.random.uniform(5, 15, len(dates))
    min_temp = avg_temp - daily_range * 0.6
    max_temp = avg_temp + daily_range * 0.4
    
    # Create DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Average Temperature (°C)': avg_temp,
        'Lowest Temperature (°C)': min_temp,
        'Highest Temperature (°C)': max_temp,
    })
    
    return df

def demo_trend_analysis():
    """Demonstrate the trend analysis functionality."""
    print("Climate Compare - Trend Analysis Demo")
    print("=" * 50)
    
    # Create demo data
    chart_df = create_demo_data()
    
    print(f"Generated {len(chart_df)} days of weather data")
    print(f"Date range: {chart_df['Date'].min().date()} to {chart_df['Date'].max().date()}")
    
    # Add trend lines
    print("\nCalculating trend lines...")
    chart_df_with_trends = add_trend_lines_to_chart_data(chart_df)
    
    # Get trend summary
    trend_summary = get_trend_summary(chart_df_with_trends)
    
    print("\n🌡️ CLIMATE TREND ANALYSIS RESULTS")
    print("=" * 50)
    
    for temp_col, trend_info in trend_summary.items():
        print(f"\n📊 {temp_col}:")
        
        direction = trend_info['trend_direction']
        slope_per_year = trend_info['slope'] * 365.25
        correlation = trend_info['r_value']
        p_value = trend_info['p_value']
        
        # Choose appropriate emoji
        if direction == 'warming' and p_value < 0.05:
            emoji = "🔥"
            status = "SIGNIFICANT WARMING"
        elif direction == 'cooling' and p_value < 0.05:
            emoji = "❄️"
            status = "SIGNIFICANT COOLING"
        elif direction == 'stable':
            emoji = "📊"
            status = "STABLE/NO TREND"
        else:
            emoji = "🌡️"
            status = "WEAK TREND"
        
        print(f"   {emoji} Status: {status}")
        print(f"   📈 Rate: {slope_per_year:+.2f}°C per year")
        print(f"   🔗 Correlation: {correlation:.3f}")
        print(f"   📊 Significance: p = {p_value:.3f}")
        print(f"   📝 {trend_info['trend_description']}")
        
        # Interpret the result
        if p_value < 0.05:
            if abs(correlation) > 0.7:
                strength = "Strong"
            elif abs(correlation) > 0.4:
                strength = "Moderate"
            else:
                strength = "Weak"
            print(f"   ✅ {strength} and statistically significant trend detected!")
        else:
            print(f"   ⚠️  Trend not statistically significant (p > 0.05)")
    
    print("\n" + "=" * 50)
    print("✅ Demo completed successfully!")
    print("\nThis demonstrates the trend analysis functionality that has been")
    print("integrated into the Climate Compare Streamlit app.")
    print("\nKey features:")
    print("• Linear regression trend analysis")
    print("• Statistical significance testing")
    print("• Visual trend lines on temperature charts")
    print("• User-friendly trend indicators and descriptions")
    
    return chart_df_with_trends

def create_visualization(df):
    """Create a sample visualization showing the trend lines."""
    print("\nCreating sample visualization...")
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
    fig.suptitle('Climate Compare - Temperature Trends Demo', fontsize=16, fontweight='bold')
    
    temp_cols = ['Average Temperature (°C)', 'Lowest Temperature (°C)', 'Highest Temperature (°C)']
    trend_cols = [f'{col} Trend' for col in temp_cols]
    axes = [ax1, ax2, ax3]
    colors = ['blue', 'green', 'red']
    
    for i, (temp_col, trend_col, ax, color) in enumerate(zip(temp_cols, trend_cols, axes, colors)):
        # Plot actual data
        ax.plot(df['Date'], df[temp_col], alpha=0.7, color=color, linewidth=1, label='Actual Data')
        
        # Plot trend line
        ax.plot(df['Date'], df[trend_col], color='red', linewidth=2, label='Trend Line')
        
        ax.set_title(temp_col)
        ax.set_ylabel('Temperature (°C)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add trend info as text
        slope_per_year = (df[trend_col].iloc[-1] - df[trend_col].iloc[0]) / len(df) * 365.25
        ax.text(0.02, 0.98, f'Trend: {slope_per_year:+.1f}°C/year', 
                transform=ax.transAxes, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7),
                verticalalignment='top')
    
    plt.xlabel('Date')
    plt.tight_layout()
    plt.savefig('/tmp/climate_trends_demo.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("✅ Visualization saved to /tmp/climate_trends_demo.png")

if __name__ == "__main__":
    df_with_trends = demo_trend_analysis()
    create_visualization(df_with_trends)
    print("\n🎉 Climate Compare trend analysis demonstration complete!")