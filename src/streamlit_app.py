# Adjust sys.path for interactive Streamlit runs
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Standard library imports
from datetime import datetime

import plotly.express as px

# Third-party imports
import streamlit as st

# Local application imports
from fetch import get_historical_weather


def main(test_inputs=None):
    """
    Run the Streamlit application.
    If test_inputs is provided, use those instead of user input widgets
    (for headless/test mode).
    """
    setup_page()
    if test_inputs is not None:
        # Use provided test inputs directly (for headless/test mode)
        handle_data_fetching(test_inputs)
    else:
        # Use the widget-based user input function
        inputs = get_user_inputs()
        handle_data_fetching(inputs)


def setup_page():
    """Setup the page title and description."""
    st.title("🌦️ Climate Compare")
    st.subheader("Visualize and compare historical weather data")


def get_user_inputs():
    """Get and validate user inputs."""
    # --- Inputs ---
    lat = st.number_input(
        "Latitude",
        value=55.9533,
        min_value=-90.0,
        max_value=90.0,
        help=("Latitude coordinate (-90 to 90). Default: Edinburgh, Scotland"),
    )
    lon = st.number_input(
        "Longitude",
        value=-3.1883,
        min_value=-180.0,
        max_value=180.0,
        help=("Longitude coordinate (-180 to 180). Default: Edinburgh, Scotland"),
    )
    from datetime import date

    start_date = st.date_input("Start Date", value=date(2023, 1, 1))
    end_date = st.date_input("End Date", value=date(2023, 1, 15))

    # Calculate the date range in days
    date_range = (end_date - start_date).days

    # Warn if date range is too large
    if date_range > 30:
        st.warning(
            f"Selected date range is {date_range} days. "
            "Large date ranges may result in slower performance."
        )
    # Validate date range
    if end_date < start_date:
        st.warning("End date was before start date. Dates have been swapped.")
        start_date, end_date = end_date, start_date

    return {"lat": lat, "lon": lon, "start_date": start_date, "end_date": end_date}


def handle_data_fetching(inputs):
    """Handle data fetching and visualization."""
    # Debug: log when this function is called
    import os

    with open("app_debug.log", "a", encoding="utf-8") as f:
        f.write(f"handle_data_fetching called with: {inputs}\n")
    # In test mode, always fetch data (no button)
    if os.environ.get("STREAMLIT_HEADLESS") == "1":
        # Headless/test mode: always fetch
        data = fetch_weather_data(inputs)
        if data is None:
            return
        if hasattr(data, "empty") and data.empty:
            with open("app_debug.log", "a", encoding="utf-8") as f:
                f.write("No data found for the selected location or date range.\n")
        else:
            with open("app_debug.log", "a", encoding="utf-8") as f:
                f.write(f"Found {len(data)} days of data.\n")
    else:
        # Only run the button logic if not in headless mode
        if hasattr(st, "button"):
            if st.button("Fetch and Plot Weather Data"):
                with st.spinner("Fetching data..."):
                    data = fetch_weather_data(inputs)
                    if data is None:
                        return
                if data.empty:
                    st.warning("No data found for the selected location or date range.")
                else:
                    st.success(f"Found {len(data)} days of data.")
                    st.dataframe(data)
                    visualize_weather_data(data)


def fetch_weather_data(inputs):
    """Fetch weather data with error handling.

    Uses a timeout parameter to prevent the request from hanging indefinitely.
    """
    try:
        # Debug: log input parameters
        with open("app_debug.log", "a", encoding="utf-8") as f:
            f.write(f"fetch_weather_data called with: {inputs}\n")
        data = get_historical_weather(
            inputs["lat"],
            inputs["lon"],
            datetime.combine(inputs["start_date"], datetime.min.time()),
            datetime.combine(inputs["end_date"], datetime.min.time()),
        )
        # Debug: log data shape/info
        with open("app_debug.log", "a", encoding="utf-8") as f:
            if data is not None:
                f.write(f"Fetched data shape: {getattr(data, 'shape', None)}\n")
                f.write(f"Fetched data head: {getattr(data, 'head', lambda: None)()}\n")
            else:
                f.write("Fetched data is None\n")
        return data
    except TimeoutError:
        st.error(
            "Request timed out. Please try again or check your internet connection."
        )
        # Debug: log timeout
        with open("app_debug.log", "a", encoding="utf-8") as f:
            f.write("TimeoutError occurred in fetch_weather_data\n")
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        # Debug: log exception
        with open("app_debug.log", "a", encoding="utf-8") as f:
            f.write(f"Exception in fetch_weather_data: {e}\n")
        return None

def visualize_weather_data(data):
    """Create and display visualizations for weather data."""
    import streamlit as st
    import pandas as pd
    import plotly.express as px

    # --- Metric selection widget ---
    metric_columns = [col for col in data.columns if col != "time"]
    if not metric_columns:
        st.error("No valid metric columns found in the data.")
        return

    default_index = 0
    if "tavg" in metric_columns:
        default_index = metric_columns.index("tavg")

    selected_metric = st.selectbox(
        "Select metric to plot:", metric_columns, index=default_index
    )

    # --- Ensure data index is datetime ---
    try:
        data.index = pd.to_datetime(data.index, errors="coerce")
    except Exception as e:
        st.error(f"Failed to convert index to datetime: {e}")
        return

    if not isinstance(data.index, pd.DatetimeIndex):
        st.error("Data index is not a DatetimeIndex. Please check input format.")
        return

    if data.index.hasnans:
        st.warning("Some rows have invalid timestamps and will be dropped.")
        data = data[~data.index.isna()]

    if data.empty:
        st.error("No valid data to display after processing timestamps.")
        return

    # --- Warn about missing values in selected metric ---
    if data[selected_metric].isna().any():
        st.warning(
            f"Selected metric '{selected_metric}' contains missing values "
            "which may affect visualization."
        )

    # --- Plot the selected metric ---
    fig = px.line(
        data,
        x=data.index,
        y=selected_metric,
        title=f"Daily {selected_metric} over Time",
        labels={
            selected_metric: selected_metric.replace("_", " ").title(),
            "x": "Date",
        },
        markers=True,
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=selected_metric.replace("_", " ").title(),
        hovermode="x unified",
    )
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()
