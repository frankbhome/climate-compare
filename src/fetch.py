from meteostat import Point, Daily
from datetime import datetime

def get_historical_weather(lat, lon, start, end):
    location = Point(lat, lon)
    data = Daily(location, start, end)
    data = data.fetch()
    return data
