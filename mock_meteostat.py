# Mock meteostat for testing without external dependencies
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

class Point:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

class Daily:
    def __init__(self, location, start, end):
        self.location = location
        self.start = start
        self.end = end
    
    def fetch(self):
        # Generate mock weather data with some trend
        days = (self.end - self.start).days + 1
        dates = pd.date_range(start=self.start, periods=days, freq='D')
        
        # Create synthetic temperature data with a slight upward trend to test regression
        base_temp = 10.0  # Base temperature in Celsius
        trend_slope = 0.02  # Small warming trend per day
        noise_scale = 3.0   # Random variation
        
        np.random.seed(42)  # For reproducible data
        temps = base_temp + trend_slope * np.arange(days) + np.random.normal(0, noise_scale, days)
        
        return pd.DataFrame({
            'tavg': temps,
            'tmin': temps - np.random.uniform(2, 5, days),
            'tmax': temps + np.random.uniform(2, 5, days),
            'prcp': np.random.exponential(1.0, days),
            'snow': np.where(temps < 0, np.random.exponential(0.5, days), 0),
            'wdir': np.random.uniform(0, 360, days),
            'wspd': np.random.uniform(5, 25, days),
            'wpgt': np.random.uniform(10, 40, days),
            'pres': 1013 + np.random.normal(0, 10, days),
            'tsun': np.random.uniform(0, 12, days),
        }, index=dates)