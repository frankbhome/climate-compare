# climate-compare

[![CI](https://github.com/frankbhome/climate-compare/actions/workflows/ci.yml/badge.svg)](https://github.com/frankbhome/climate-compare/actions/workflows/ci.yml)
[![Tests](https://github.com/frankbhome/climate-compare/actions/workflows/test.yml/badge.svg)](https://github.com/frankbhome/climate-compare/actions/workflows/test.yml)

> Fetch and visualize weather station data (live + historical) for environmental insight and comparison.

---

## 🔍 Project Overview

`climate-compare` is a lightweight Streamlit app that allows users to:
- Retrieve historical weather data using the [Meteostat](https://dev.meteostat.net/) API
- Visualize data using interactive Plotly charts
- Compare climate patterns over time or location

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/frankbhome/climate-compare.git
cd climate-compare
```

### 2. Set up Python environment

```bash
python3 -m venv venv
source venv/bin/activate   # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### 3. Run the Streamlit app

```bash
streamlit run src/streamlit_app.py
```

---

## 🧪 Run Tests

Tests are written with `pytest`. To run:

```bash
pip install -r requirements-dev.txt
pytest
```

---

## 🧰 Developer Notes

- **Testable UI Mode:**  
  You can run the app in non-interactive mode for tests or automation using:

  ```python
  from src.streamlit_app import main
  from datetime import date

  test_inputs = {
      "lat": 55.9533,
      "lon": -3.1883,
      "start_date": date(2023, 1, 1),
      "end_date": date(2023, 1, 15)
  }
  main(test_inputs=test_inputs)
  ```

- **Weather Data Caching:**  
  Historical weather queries are cached using `@lru_cache` for efficiency.

---

## 🔗 GitHub + JIRA Integration

Use JIRA issue keys (e.g., `DOC-101`) in:
- Branch names: `feature/DOC-101-update-readme`
- Commits: `Update README.md with setup instructions DOC-101`
- PR titles: `DOC-101: Update README for project setup`

This ensures your GitHub activity is linked automatically to JIRA issues.

---

## 📁 Project Structure

```
climate-compare/
│
├── src/
│   ├── fetch.py             # Weather data fetch logic
│   └── streamlit_app.py     # Web UI and visualization
│
├── tests/                   # Unit tests
├── .github/                 # GitHub Actions workflows
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
└── README.md                # You are here
```

---

## 📄 License

Copyright © 2025 Francis Bain

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
