# Copyright (c) 2025 Francis Bain
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any

import pandas as pd

from src.formatters import (
    COLUMN_MAP,
    deg_to_compass,
    to_kmh,
)


def build_user_view(df: pd.DataFrame | None) -> tuple[pd.DataFrame, dict[str, Any]]:
    # If caller passes None, return an empty view and empty config to satisfy callers/tests
    if df is None:
        return pd.DataFrame(), {}
    df = df.copy()

    # Helper to format numeric values: round to 1 dp or return em dash for missing
    def fmt_num(v):
        if pd.isna(v):
            return "—"
        try:
            return round(float(v), 1)
        except Exception:
            return "—"

    # Map raw columns to display headers
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
    # Date formatting
    out["Date"] = df["time"].dt.strftime("%b %d, %Y")

    # Apply numeric formatting / em-dash replacement
    for raw_col, display_col in mapping.items():
        out[display_col] = [fmt_num(v) for v in df[raw_col]]

    # Build Wind summary using imported helpers
    def wind_summary(wdir, wspd, wpgt):
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

    # Column configuration metadata (minimal)
    col_cfg: dict[str, Any] = {}
    for display_col in mapping.values():
        col_cfg[display_col] = {"help": "", "format": "%.1f"}
    col_cfg["Date"] = {"help": "Date of observation", "format": "%b %d, %Y"}
    col_cfg["Wind"] = {"help": "Wind summary", "format": "%s"}

    return out, col_cfg


def test_deg_to_compass_basic():
    assert deg_to_compass(0) == "N"
    assert deg_to_compass(359) == "N"  # wrap-around
    assert deg_to_compass(90) == "E"
    assert deg_to_compass(225) == "SW"
    assert deg_to_compass(None) == "—"
    assert deg_to_compass(float("nan")) == "—"


def test_to_kmh_none_and_numeric():
    assert to_kmh(None) is None
    assert isinstance(to_kmh(10), float)
    assert to_kmh(10) == 10.0  # adjust if you later enable m/s -> km/h conversion


def test_build_user_view_full_mapping_and_formats():
    # Build a small raw dataframe with realistic columns (including NaNs)
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

    user_df, col_cfg = build_user_view(df)

    # 1) Column renames applied to plain English (units in headers)
    expected_headers = {
        "Date",
        "Average Temperature (°C)",
        "Lowest Temperature (°C)",
        "Highest Temperature (°C)",
        "Rainfall (mm)",
        "Snowfall (mm)",
        "Air Pressure (hPa)",
        "Sunshine Duration (hours)",
        "Wind",
    }
    assert set(user_df.columns) == expected_headers

    # 2) Dates are formatted as "Jan 01, 2023"
    assert user_df.loc[0, "Date"] == "Jan 01, 2023"
    assert user_df.loc[1, "Date"] == "Jan 02, 2023"

    # 3) Rounding to 1 decimal place
    # row 0: 3.84 -> 3.8; row 1: None -> "—" after replacement
    assert user_df.loc[0, "Average Temperature (°C)"] == 3.8
    assert user_df.loc[1, "Average Temperature (°C)"] == "—"
    # tmin rounding and tmax rounding
    assert user_df.loc[0, "Lowest Temperature (°C)"] == 1.1
    assert user_df.loc[0, "Highest Temperature (°C)"] == 6.5

    # 4) Units retained in column names (we already checked headers)
    assert any("(°C)" in h for h in user_df.columns)
    assert "Rainfall (mm)" in user_df.columns
    assert "Air Pressure (hPa)" in user_df.columns
    assert "Sunshine Duration (hours)" in user_df.columns

    # 5) Unknowns replaced with em dash "—"
    assert user_df.loc[0, "Snowfall (mm)"] == "—"  # original None -> "—"
    assert user_df.loc[1, "Sunshine Duration (hours)"] == "—"

    # 6) Wind summary created; detailed wind columns dropped
    # Expect something like "SSW • avg 22.0 km/h • gust 50.5 km/h" for row 0
    wind0 = user_df.loc[0, "Wind"]
    assert "avg" in wind0 and "gust" in wind0 and "km/h" in wind0
    # Row 1 had NaN direction and None gust -> em dashes present
    wind1 = user_df.loc[1, "Wind"]
    assert "—" in wind1

    # 7) Column config contains help/format metadata
    assert "Average Temperature (°C)" in col_cfg
    assert "help" in col_cfg["Average Temperature (°C)"]
    assert col_cfg["Average Temperature (°C)"]["format"] == "%.1f"


def test_column_map_is_consistent():
    # Ensure mapping includes all expected raw keys
    keys = {
        "time",
        "tavg",
        "tmin",
        "tmax",
        "prcp",
        "snow",
        "wdir",
        "wspd",
        "wpgt",
        "pres",
        "tsun",
    }
    assert keys.issubset(set(COLUMN_MAP.keys()))
