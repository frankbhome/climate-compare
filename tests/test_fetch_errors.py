# tests/test_fetch_errors.py
import datetime as dt

import src.fetch as fetch


def _maybe_setattr(obj, name, value, monkeypatch):
    if hasattr(obj, name):
        monkeypatch.setattr(obj, name, value, raising=True)


def test_get_historical_weather_timeout(monkeypatch):
    """Force a TimeoutError from the underlying fetch to hit the timeout handler."""
    # Ensure we don't hit a previous cached value
    fetch.get_historical_weather.cache_clear()

    class _DailyBoom:
        def __init__(self, *a, **k):
            pass

        def fetch(self):
            raise TimeoutError("simulated timeout")

    # Some implementations use Daily, others Hourly – patch whichever exists.
    _maybe_setattr(fetch, "Daily", _DailyBoom, monkeypatch)
    _maybe_setattr(fetch, "Hourly", _DailyBoom, monkeypatch)

    out = fetch.get_historical_weather(
        55.95, -3.19, dt.date(2023, 1, 1), dt.date(2023, 1, 2)
    )
    assert out is None


def test_get_historical_weather_generic_exception(monkeypatch):
    """Force a generic exception to hit the broad exception handler."""
    # Ensure we don't hit a previous cached value
    fetch.get_historical_weather.cache_clear()

    class _DailyBoom:
        def __init__(self, *a, **k):
            pass

        def fetch(self):
            raise RuntimeError("kaboom")

    _maybe_setattr(fetch, "Daily", _DailyBoom, monkeypatch)
    _maybe_setattr(fetch, "Hourly", _DailyBoom, monkeypatch)

    out = fetch.get_historical_weather(
        55.95, -3.19, dt.date(2023, 1, 1), dt.date(2023, 1, 2)
    )
    assert out is None
