# tests/test_fetch_errors.py
import datetime as dt

import pandas as pd

import src.fetch as fetch


def _maybe_setattr(obj, name, value, monkeypatch):
    """Set attr if present; ignore if the symbol doesn't exist in src.fetch."""
    if hasattr(fetch, name):
        monkeypatch.setattr(fetch, name, value, raising=True)


def test_get_historical_weather_timeout(monkeypatch):
    """Force a TimeoutError from the underlying fetch to hit the timeout handler."""

    class _DailyBoom:
        def __init__(self, *a, **k):
            pass

        def fetch(self):
            raise TimeoutError("simulated timeout")

    # Some implementations use Daily, others Hourly – patch whichever exists.
    _maybe_setattr(fetch, "Daily", _DailyBoom, monkeypatch)
    _maybe_setattr(fetch, "Hourly", _DailyBoom, monkeypatch)

    start = dt.date(2023, 1, 1)
    end = dt.date(2023, 1, 3)
    out = fetch.get_historical_weather(55.95, -3.19, start, end)

    # Your implementation returns None on error; accept either None or empty DataFrame
    assert out is None or (isinstance(out, pd.DataFrame) and out.empty)


def test_get_historical_weather_generic_exception(monkeypatch):
    """Force a generic exception to hit the broad exception handler."""

    class _DailyBoom:
        def __init__(self, *a, **k):
            pass

        def fetch(self):
            raise RuntimeError("kaboom")

    _maybe_setattr(fetch, "Daily", _DailyBoom, monkeypatch)
    _maybe_setattr(fetch, "Hourly", _DailyBoom, monkeypatch)

    start = dt.date(2023, 1, 1)
    end = dt.date(2023, 1, 3)
    out = fetch.get_historical_weather(55.95, -3.19, start, end)

    # Accept None or empty DataFrame on error
    assert out is None or (isinstance(out, pd.DataFrame) and out.empty)
