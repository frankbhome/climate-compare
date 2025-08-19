# src/formatters.py
# Utilities to convert a raw weather dataframe into a layperson-friendly table.
from __future__ import annotations
from typing import Optional, Union

import math
import pandas as pd

# Mapping from raw column names to layperson-friendly labels
COLUMN_MAP: dict[str, str] = {
    "time": "Date",
    "tavg": "Average Temperature (°C)",
    "tmin": "Lowest Temperature (°C)",
    "tmax": "Highest Temperature (°C)",
    "prcp": "Rainfall (mm)",
    "snow": "Snowfall (mm)",
    "wdir": "Wind Direction (°)",
    "wspd": "Wind Speed (km/h)",
    "wpgt": "Wind Gusts (km/h)",
    "pres": "Air Pressure (hPa)",
    "tsun": "Sunshine Duration (hours)",
}

# 16-wind compass rose labels
COMPASS = [
    "N","NNE","NE","ENE","E","ESE","SE","SSE",
    "S","SSW","SW","WSW","W","WNW","NW","NNW"
]

def _is_nan(x) -> bool:
    try:
        return x is None or (isinstance(x, float) and math.isnan(x))
    except Exception:
        return False

def deg_to_compass(deg: Optional[Union[float, int]]) -> str:
    """Convert wind direction in degrees to a 16-point compass label."""
    if _is_nan(deg):
        return "—"
    assert deg is not None
    deg_f: float = float(deg)  # safe after guard
    idx = int((deg_f % 360) / 22.5 + 0.5) % 16
    return COMPASS[idx]

def to_kmh(x: Optional[Union[float, int]]) -> Optional[float]:
    """Convert wind speed to km/h if needed.
    If your data is already km/h, just return x.
    If it's m/s, uncomment the conversion.
    """
    if _is_nan(x):
        return None
    assert x is not None
    xf: float = float(x)  # safe after guard
    # return xf * 3.6  # <- enable if your source is m/s
    return xf

def build_user_view(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Return (user_friendly_df, column_config_meta)."""
    out = df.copy()

    # Parse & format date
    if "time" in out.columns:
        out["time"] = pd.to_datetime(out["time"], errors="coerce").dt.strftime("%b %d, %Y")

    # Rounding
    for c in ["tavg", "tmin", "tmax", "prcp", "snow", "pres", "tsun"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce").round(1)

    # Wind numeric conversions
    if "wspd" in out.columns:
        out["wspd"] = out["wspd"].apply(to_kmh)
        out["wspd"] = pd.to_numeric(out["wspd"], errors="coerce").round(1)

    if "wpgt" in out.columns:
        out["wpgt"] = out["wpgt"].apply(to_kmh)
        out["wpgt"] = pd.to_numeric(out["wpgt"], errors="coerce").round(1)

    # Friendly wind summary (compass + speeds)
    if "wdir" in out.columns:
        out["Wind"] = out.apply(
            lambda r: (
                f'{deg_to_compass(r.get("wdir"))} • '
                f'avg {("—" if _is_nan(r.get("wspd")) else r.get("wspd"))} km/h • '
                f'gust {("—" if _is_nan(r.get("wpgt")) else r.get("wpgt"))} km/h'
            ),
            axis=1,
        )

    # Replace None/NaN with em dash for display
    out = out.replace({None: "—"})
    out = out.fillna("—")

    # Rename columns to friendly labels
    out = out.rename(columns=COLUMN_MAP)

    # Optionally drop detailed wind columns (kept summarized in "Wind")
    drop_cols = [COLUMN_MAP.get("wdir", "wdir"),
                 COLUMN_MAP.get("wspd", "wspd"),
                 COLUMN_MAP.get("wpgt", "wpgt")]
    for dc in drop_cols:
        if dc in out.columns and "Wind" in out.columns:
            out = out.drop(columns=[dc])

    # Column config metadata for Streamlit
    col_cfg = {
        "Date": {"help": "Date of the observation"},
        "Average Temperature (°C)": {"help": "Mean temperature for the day", "format": "%.1f"},
        "Lowest Temperature (°C)": {"help": "Coldest temperature recorded", "format": "%.1f"},
        "Highest Temperature (°C)": {"help": "Warmest temperature recorded", "format": "%.1f"},
        "Rainfall (mm)": {"help": "Total precipitation (rain/snow water equivalent)", "format": "%.1f"},
        "Snowfall (mm)": {"help": "Total snowfall depth", "format": "%.1f"},
        "Air Pressure (hPa)": {"help": "Atmospheric pressure at sea level", "format": "%.1f"},
        "Sunshine Duration (hours)": {"help": "Total hours of bright sunshine", "format": "%.1f"},
        "Wind": {"help": "Compass direction, average speed, and maximum gust (km/h)"},
    }
    return out, col_cfg
