# Standard library imports
from datetime import datetime

import plotly.express as px
# Third-party imports
import streamlit as st

# Local application imports
from src.fetch import get_historical_weather


def main():
    """Run the Streamlit application."""
    setup_page()
    user_inputs = get_user_inputs()
    handle_data_fetching(user_inputs)


def setup_page():
    """Setup the page title and description."""
    # --- Page title ---
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
        help="Latitude coordinate (-90 to 90). Default: Edinburgh, Scotland",
    )
    lon = st.number_input(
        "Longitude",
        value=-3.1883,
        min_value=-180.0,
        max_value=180.0,
        help="Longitude coordinate (-180 to 180). Default: Edinburgh, Scotland",
    )
    from datetime import date

    start_date = st.date_input("Start Date", value=date(2023, 1, 1))
    end_date = st.date_input("End Date", value=date(2023, 1, 15))

    # Calculate the date range in days
    date_range = (end_date - start_date).days

    # Warn if date range is too large
    if date_range > 30:
        st.warning(
            f"Selected date range is {date_range} days. Large date ranges may result in slower performance."
        )
    # Validate date range
    if end_date < start_date:
        st.warning("End date was before start date. Dates have been swapped.")
        start_date, end_date = end_date, start_date

    return {"lat": lat, "lon": lon, "start_date": start_date, "end_date": end_date}


def handle_data_fetching(inputs):
    """Handle data fetching and visualization."""
    # --- Button ---
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
        data = get_historical_weather(
            inputs["lat"],
            inputs["lon"],
            datetime.combine(inputs["start_date"], datetime.min.time()),
            datetime.combine(inputs["end_date"], datetime.min.time()),
            timeout=5,  # seconds
        )
        return data
    except TimeoutError:
        st.error(
            "Request timed out. Please try again or check your internet connection."
        )
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None


def visualize_weather_data(data):
    """Create and display visualizations for weather data."""
    # --- Metric selection widget ---
    metric_columns = [col for col in data.columns if col != "time"]
    if metric_columns:
        default_index = 0
        if metric_columns and "tavg" in metric_columns:
            default_index = metric_columns.index("tavg")

    selected_metric = st.selectbox(
        "Select metric to plot:", metric_columns, index=default_index
    )

    # Ensure data is properly formatted
    if not data.index.is_all_dates:
        st.warning(
            "Data index is not in datetime format. Visualization may not be accurate."
        )

    # Check for missing values in the selected metric
    if data[selected_metric].isna().any():
        st.warning(
            f"Selected metric '{selected_metric}' contains missing values which may affect visualization."
        )

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
