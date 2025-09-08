# Copyright (c) 2025 Francis Bain
# SPDX-License-Identifier: GPL-3.0-or-later

# tests/test_fetch_errors.py
import datetime as dt

import pytest

import src.fetch as fetch


def _maybe_setattr(obj, name, value, monkeypatch):
    if hasattr(obj, name):
        monkeypatch.setattr(obj, name, value, raising=True)


@pytest.mark.parametrize(
    "exc_cls,msg",
    [
        (TimeoutError, "simulated timeout"),
        (RuntimeError, "kaboom"),
    ],
)
def test_get_historical_weather_handles_exceptions(monkeypatch, exc_cls, msg):
    """get_historical_weather should return None when underlying fetch raises.

    This single parametrized test covers both TimeoutError and generic RuntimeError
    cases by monkeypatching either `Daily` or `Hourly` implementation to a
    dummy that raises the requested exception.
    """
    # Ensure we don't hit a previous cached value
    fetch.get_historical_weather.cache_clear()

    class _Boom:
        def __init__(self, *a, **k):
            pass

        def fetch(self):
            raise exc_cls(msg)

    # Patch whichever implementation exists in this environment
    _maybe_setattr(fetch, "Daily", _Boom, monkeypatch)
    _maybe_setattr(fetch, "Hourly", _Boom, monkeypatch)

    out = fetch.get_historical_weather(
        55.95, -3.19, dt.date(2023, 1, 1), dt.date(2023, 1, 2)
    )
    assert out is None
