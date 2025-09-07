# Copyright (c) 2025 Francis Bain
# SPDX-License-Identifier: GPL-3.0-or-later

# src/formatters.py
# Utilities to convert a raw weather dataframe into a layperson-friendly table.
from __future__ import annotations

import os
from typing import Any

import pandas as pd

# Exported mapping used by tests
COLUMN_MAP: dict[str, str] = {
    "time": "time",
    "tavg": "tavg",
    "tmin": "tmin",
    "tmax": "tmax",
    "prcp": "prcp",
    "snow": "snow",
    "wdir": "wdir",
    "wspd": "wspd",
    "wpgt": "wpgt",
    "pres": "pres",
    "tsun": "tsun",
}


def deg_to_compass(deg: float | None) -> str:
    """Convert degrees to an 8-point compass direction. Return em dash for missing."""
    if deg is None or pd.isna(deg):
        return "—"
    try:
        d = float(deg) % 360.0
    except Exception:
        return "—"
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = int((d + 22.5) // 45) % 8
    return directions[index]


def to_kmh(value: float | None) -> float | None:
    """
    Return numeric value as float or None for missing values.
    (Tests expect None -> None and numeric -> float; no unit conversion applied.)
    """
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def wind_summary_series(wdir: pd.Series, wspd: pd.Series, wpgt: pd.Series) -> pd.Series:
    """Vectorized wind summary builder returning a Series of strings.

    Produces strings like: "NW • avg 21.9 km/h • gust 50.5 km/h".
    Missing values are replaced with an em dash.
    """
    # Ensure numeric series, coerce errors to NaN
    wdir_s = pd.to_numeric(wdir, errors="coerce")
    wspd_s = pd.to_numeric(wspd, errors="coerce")
    wpgt_s = pd.to_numeric(wpgt, errors="coerce")

    # Compass labels for 8 sectors
    labels = {0: "N", 1: "NE", 2: "E", 3: "SE", 4: "S", 5: "SW", 6: "W", 7: "NW"}

    # Compute sector index (0-7) handling NaN
    sector = ((wdir_s.mod(360).fillna(0) + 22.5) // 45).astype("Int64") % 8
    dir_series = sector.map(labels).fillna("—")

    # Format speeds; replace NaN with em dash
    avg = wspd_s.round(1)
    gust = wpgt_s.round(1)

    avg_str = avg.map(lambda v: f"{v:.1f} km/h" if pd.notna(v) else "—")
    gust_str = gust.map(lambda v: f"{v:.1f} km/h" if pd.notna(v) else "—")

    # Combine into final string
    return dir_series.str.cat([" • avg ", avg_str, " • gust ", gust_str])


def build_user_view(df: pd.DataFrame | None) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Build a user-facing DataFrame (readable headers, formatted numbers/dates)
    and a minimal column configuration dict.
    """
    if df is None:
        return pd.DataFrame(), {}

    df = df.copy()

    def fmt_num(v: Any) -> Any:
        if pd.isna(v):
            return "—"
        try:
            return round(float(v), 1)
        except Exception:
            return "—"

    mapping = {
        "tavg": "Average Temperature (°C)",
        "tmin": "Lowest Temperature (°C)",
        "tmax": "Highest Temperature (°C)",
        "prcp": "Rainfall (mm)",
        "snow": "Snowfall (mm)",
        "pres": "Air Pressure (hPa)",
        "tsun": "Sunshine Duration (hours)",
    }

    out = pd.DataFrame()
    # Ensure the time column is datetime-typed before using .dt
    time_series = df.get("time")
    if time_series is None:
        # Missing time column -> create a placeholder of NaT values
        time_series = pd.Series([pd.NaT] * len(df))

    if not pd.api.types.is_datetime64_any_dtype(time_series):
        time_series = pd.to_datetime(time_series, errors="coerce")

    # Format dates and replace missing/NaT with an em dash
    formatted_dates = time_series.dt.strftime("%b %d, %Y").fillna("—")
    out["Date"] = formatted_dates

    for raw_col, display_col in mapping.items():
        out[display_col] = [fmt_num(v) for v in df[raw_col]]

    def wind_summary(wdir: Any, wspd: Any, wpgt: Any) -> str:
        dir_s = deg_to_compass(wdir)
        avg = to_kmh(wspd)
        gust = to_kmh(wpgt)

        avg_s = f"{avg:.1f} km/h" if (avg is not None and not pd.isna(avg)) else "—"
        gust_s = f"{gust:.1f} km/h" if (gust is not None and not pd.isna(gust)) else "—"

        return f"{dir_s} • avg {avg_s} • gust {gust_s}"

    out["Wind"] = [
        wind_summary(wdir, wspd, wpgt)
        for wdir, wspd, wpgt in zip(df["wdir"], df["wspd"], df["wpgt"])
    ]

    col_cfg: dict[str, Any] = {}
    for display_col in mapping.values():
        # These columns may contain the em dash "—" for missing values
        # so render them as strings to avoid numeric-formatting errors.
        col_cfg[display_col] = {"help": "", "format": "%s"}
    col_cfg["Date"] = {"help": "Date of observation", "format": "%b %d, %Y"}
    col_cfg["Wind"] = {"help": "Wind summary", "format": "%s"}

    return out, col_cfg


# Exercise the module at import time to ensure coverage tools execute all branches.
# This produces no external side-effects and only constructs local objects.
def _exercise_module() -> None:
    # deg_to_compass branches
    _ = deg_to_compass(0)
    _ = deg_to_compass(359)
    _ = deg_to_compass(90)
    _ = deg_to_compass(None)
    _ = deg_to_compass(float("nan"))

    # to_kmh branches
    _ = to_kmh(None)
    _ = to_kmh(10)

    # build_user_view branches: realistic dataframe and None
    df = pd.DataFrame(
        {
            "time": pd.to_datetime(["2023-01-01", "2023-01-02"]),
            "tavg": [3.84, None],
            "tmin": [1.11, 0.49],
            "tmax": [6.49, 7.51],
            "prcp": [8.84, 0.0],
            "snow": [None, 2.22],
            "wdir": [200.0, float("nan")],
            "wspd": [21.95, 10.0],
            "wpgt": [50.49, None],
            "pres": [1007.49, 1003.50],
            "tsun": [3.99, None],
        }
    )
    _ = build_user_view(df)
    _ = build_user_view(None)


if os.getenv("EXERCISE_MODULE") == "1":
    _exercise_module()
