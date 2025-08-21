# src/streamlit_app.py
from __future__ import annotations

from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

# --- Imports ---
try:
    from src.fetch import get_historical_weather
except Exception:
    from fetch import get_historical_weather  # type: ignore

try:
    from src.formatters import COLUMN_MAP, build_user_view
except Exception:
    from formatters import COLUMN_MAP, build_user_view  # type: ignore

st.set_page_config(page_title="Climate Compare – Weather History", layout="wide")
st.title("Weather History")
st.caption("View of historical weather data")


# --- Small helper: toggle/checkbox compat ---
def ui_toggle(
    label: str, value: bool = False, key: str | None = None, help: str | None = None
) -> bool:
    if hasattr(st, "toggle"):
        return st.toggle(label, value=value, key=key, help=help)
    return st.checkbox(label, value=value, key=key, help=help)


# --- Location helpers ---
PRESETS = {
    "Edinburgh, UK": (55.9533, -3.1883),
    "London, UK": (51.5074, -0.1278),
    "Glasgow, UK": (55.8642, -4.2518),
    "Belfast, UK": (54.5973, -5.9301),
    "Manchester, UK": (53.4808, -2.2426),
}


def parse_location(text: str) -> tuple[float, float] | None:
    text = (text or "").strip()
    if text in PRESETS:
        return PRESETS[text]
    # Support "lat,lon"
    if "," in text:
        try:
            lat_str, lon_str = (p.strip() for p in text.split(",", 1))
            return float(lat_str), float(lon_str)
        except Exception:
            return None
    # Fallback to preset Edinburgh
    return PRESETS["Edinburgh, UK"]


# --- Sidebar ---
with st.sidebar:
    st.header("Filters")
    # Friendly location input with preset examples
    loc_hint = "e.g., 'Edinburgh, UK' or '55.95,-3.19'"
    location_text = st.text_input("Location", value="Edinburgh, UK", help=loc_hint)
    today = date.today()
    default_start = today - timedelta(days=9)
    start_date = st.date_input("Start date", value=default_start)
    end_date = st.date_input("End date", value=today)
    advanced_mode = ui_toggle("Show advanced meteorological table", value=False)
    st.markdown("---")
    st.markdown("ℹ️ Enter a city from the presets or a pair of coordinates 'lat,lon'.")


# --- Load data ---
def _to_datetime(d) -> datetime:
    if isinstance(d, datetime):
        return d
    if isinstance(d, date):
        return datetime(d.year, d.month, d.day)
    return datetime.fromisoformat(str(d))


@st.cache_data(show_spinner=True)
def _load_data(location_text: str, start: date, end: date) -> pd.DataFrame:
    latlon = parse_location(location_text)
    if not latlon:
        return pd.DataFrame()
    lat, lon = latlon
    start_dt = _to_datetime(start)
    end_dt = _to_datetime(end)
    if end_dt < start_dt:
        start_dt, end_dt = end_dt, start_dt
    df = get_historical_weather(lat, lon, start_dt, end_dt)
    if df is None:
        return pd.DataFrame()
    # Ensure 'time' column exists (Meteostat returns DatetimeIndex)
    if "time" not in df.columns and isinstance(df.index, pd.DatetimeIndex):
        df = df.reset_index()
        # Meteostat usually returns the datetime index as a column named "time" after reset_index().
        # If it's not named "time", rename the first datetime64 column to "time".
        if "time" not in df.columns:
            for c in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[c]):
                    df = df.rename(columns={c: "time"})
                    break
        # After reset_index, the datetime index column is named 'time' by meteostat already,
        # but if it's named 'time', leave as-is; else, rename to 'time' explicitly.
        if "time" not in df.columns:
            # detect the datetime column
            for c in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[c]):
                    df = df.rename(columns={c: "time"})
                    break
    return df


with st.spinner("Loading weather data…"):
    try:
        raw_df = _load_data(location_text, start_date, end_date)
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()

if raw_df.empty:
    st.info("No data returned for the selected period.")
    st.stop()

# Build the user-friendly table (this may contain '—' strings)
user_df, col_cfg_meta = build_user_view(raw_df)

# Prepare a *display* copy with consistent string types to avoid Arrow warnings
display_df = user_df.copy()
# For any column that still has mixed types (float + string), cast everything to string
for col in display_df.columns:
    if display_df[col].dtype == "O":  # object, likely mixed
        display_df[col] = display_df[col].apply(
            lambda v: (
                "—"
                if (
                    v is None
                    or (isinstance(v, float) and pd.isna(v))
                    or (isinstance(v, str) and v.strip() == "")
                )
                else str(v)
            )
        )

# Sort newest first by Date for display
if "Date" in display_df.columns:
    tmp = pd.to_datetime(display_df["Date"], errors="coerce")
    display_df = display_df.loc[tmp.sort_values(ascending=False).index]

# Render table
st.subheader("Daily summary")
st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
)

# --- Graph view (numeric only) --------------------------------------------
st.subheader("Graphs")
# Build a numeric chart DataFrame directly from raw_df
chart_df = raw_df.copy()
# Ensure time column
if "time" not in chart_df.columns and isinstance(chart_df.index, pd.DatetimeIndex):
    chart_df = chart_df.reset_index()
# Rename for nice axis labels but keep numerics intact
chart_df = chart_df.rename(columns=COLUMN_MAP)
if "Date" not in chart_df.columns and "time" in chart_df.columns:
    chart_df["Date"] = pd.to_datetime(chart_df["time"], errors="coerce")
    chart_df = chart_df.drop(columns=["time"])

if "Date" in chart_df.columns:
    chart_df = chart_df.sort_values("Date")

    # Temperature lines
    temp_cols = [
        c
        for c in [
            "Average Temperature (°C)",
            "Lowest Temperature (°C)",
            "Highest Temperature (°C)",
        ]
        if c in chart_df.columns
    ]
    if temp_cols:
        st.line_chart(chart_df.set_index("Date")[temp_cols])

    with st.expander("More charts"):
        # Rainfall
        if "Rainfall (mm)" in chart_df.columns:
            st.bar_chart(chart_df.set_index("Date")[["Rainfall (mm)"]])
        # Sunshine
        if "Sunshine Duration (hours)" in chart_df.columns:
            st.bar_chart(chart_df.set_index("Date")[["Sunshine Duration (hours)"]])
        # Air Pressure
        if "Air Pressure (hPa)" in chart_df.columns:
            st.line_chart(chart_df.set_index("Date")[["Air Pressure (hPa)"]])

# --- Advanced table --------------------------------------------------------
if advanced_mode:
    st.subheader("Advanced table (technical columns)")
    st.dataframe(raw_df.reset_index(), use_container_width=True, hide_index=True)
    with st.expander("Column legend"):
        st.markdown(
            "- **time** — timestamp of observation\n"
            "- **tavg / tmin / tmax** — average / minimum / maximum temperature (°C)\n"
            "- **prcp** — total precipitation (mm)\n"
            "- **snow** — snowfall (mm)\n"
            "- **wdir** — wind direction (degrees, 0 = North)\n"
            "- **wspd** — average wind speed (km/h or m/s depending on source)\n"
            "- **wpgt** — maximum wind gust (km/h or m/s depending on source)\n"
            "- **pres** — air pressure (hPa)\n"
            "- **tsun** — sunshine duration (hours)\n"
        )
