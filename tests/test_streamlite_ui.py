from src.streamlit_app import main


def test_ui_renders_and_fetches_data():
    # Provide test inputs directly for headless/test mode
    test_inputs = {
        "lat": 55.9533,
        "lon": -3.1883,
        "start_date": __import__("datetime").date(2023, 1, 1),
        "end_date": __import__("datetime").date(2023, 1, 15),
    }
    # Call main with test_inputs to bypass widgets
    main(test_inputs=test_inputs)
    # Optionally, check for output files or logs if needed
    # For a more advanced test, you could mock Streamlit's st.dataframe,
    # st.success, etc.
