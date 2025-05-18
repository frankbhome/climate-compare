# tests/test_streamlit_ui.py

from streamlit.testing.v1 import AppTest


def test_ui_renders_and_fetches_data():
    at = AppTest.from_file("src/streamlit_app.py")

    # Provide user input
    at.number_input[0].set_value(55.9533)  # lat
    at.number_input[1].set_value(-3.1883)  # lon
    at.date_input[0].set_value("2023-01-01")  # start
    at.date_input[1].set_value("2023-01-10")  # end

    # Simulate button click
    at.button[0].click()

    # Re-run Streamlit app
    at.run()

    # Assertions
    assert (
        at.success[0].value.startswith("Found") or at.warning
    ), "Should return data or show warning"
