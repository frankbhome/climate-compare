# climate-compare

[![CI](https://github.com/frankbhome/climate-compare/actions/workflows/ci.yml/badge.svg)](https://github.com/frankbhome/climate-compare/actions/workflows/ci.yml)
[![Tests](https://github.com/frankbhome/climate-compare/actions/workflows/test.yml/badge.svg)](https://github.com/frankbhome/climate-compare/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/frankbhome/climate-compare/branch/develop/graph/badge.svg)](https://codecov.io/gh/frankbhome/climate-compare)

> Fetch and visualize weather station data (live + historical) for environmental insight and comparison.

## 🔍 Project Overview

`climate-compare` is a lightweight Streamlit app that allows users to:
- Retrieve historical weather data using the [Meteostat](https://dev.meteostat.net/) API
- Store weather data locally in a SQLite database for faster access and offline use
- Visualize data using interactive Plotly charts
- Compare climate patterns over time or location

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/frankbhome/climate-compare.git
cd climate-compare
```

### 2. Set up Python environment

#### 🔧 Required System Packages (Linux/WSL only)

Before installing Python packages, make sure the following system libraries are installed:

```bash
sudo apt update
sudo apt install -y libjpeg-dev zlib1g-dev
```

These are needed for image processing support via Pillow and other dependencies.

```bash
python3 -m venv venv
source venv/bin/activate   # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### 3. Run the Streamlit app

```bash
streamlit run src/streamlit_app.py
```

## 🧪 Run Tests

Tests are written with `pytest`. To run:

```bash
pip install -r requirements.txt
pytest
```

## 🐳 Running with Docker

You can run the Climate Compare app in a container using Docker.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- (Optional) [Docker Compose](https://docs.docker.com/compose/) if using the compose setup

### 📦 Build and Run (Single Container)

```bash
docker build -t climate-compare .
docker run -p 8501:8501 climate-compare
```

### 📦 Using Docker Compose

```bash
docker-compose up --build
```

Then open your browser to: <http://localhost:8501>

### 🔄 Auto Reloading
If you're actively developing, the docker-compose.yml mounts your local source code into the container. Just edit files locally and reload the browser.

### 🧹 Clean Up

```bash
docker-compose down
```

Or if you used docker directly:

```bash
docker ps
docker stop <container-id>
```

## 🧰 Developer Notes

- **Pre-commit hooks (cross-platform coverage):**
  The pre-commit hook for running `pytest` with `coverage` is now set up using a `local` hook in `.pre-commit-config.yaml` with cross-platform compatibility:

  ```yaml
  - repo: local
    hooks:
      - id: pytest
        name: Run pytest with coverage
        entry: python -m coverage run -m pytest
        language: system
        types: [python]
        pass_filenames: false
  ```

  Make sure your virtual environment is activated before committing or running hooks:

  ```bash
  # On WSL or Linux/macOS
  source .venv/bin/activate

  # On Windows PowerShell
  .\.venv\Scripts\Activate

  pre-commit install
  pre-commit run --all-files
  ```

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

- **Database Storage:**
  Weather data is automatically stored in a local SQLite database (`climate_data.db`) for faster access and offline use. Use `python manage_db.py info` to see what data is stored.

- **Database Management:**
  Use the `manage_db.py` script to manage your local weather database:

  ```bash
  # Show database information
  python manage_db.py info
  
  # List all locations with data
  python manage_db.py locations
  
  # Initialize a fresh database
  python manage_db.py init
  
  # Clean up duplicate records
  python manage_db.py clean
  ```

## 🔗 GitHub + JIRA Integration

Use JIRA issue keys (e.g., `CPG-101`) in:
- Branch names: `feature/CPG-101`
- Commits: `CPG-101: Update README.md with setup instructions`
- PR titles: `CPG-101: Update README for project setup`

This ensures your GitHub activity is linked automatically to JIRA issues.

## YAML style and linting

We enforce YAML style with [yamllint]. Key rules:
- 2-space indentation; consistent sequence indentation
- LF newlines, no trailing spaces, newline at EOF
- GitHub Actions-friendly: `truthy` disabled, `document-start` not required

Run locally:
```bash
pre-commit run yamllint --all-files
```
CI also runs yamllint on every pull request.
## 📁 Project Structure

```
climate-compare/
│
├── src/
│   ├── database.py           # Database backend for climate data
│   ├── fetch.py             # Weather data fetch logic (with database integration)
│   └── streamlit_app.py     # Web UI and visualization
│
├── tests/                   # Unit tests
├── docs/                    # Documentation
│   └── database.md         # Database system documentation
├── .github/                 # GitHub Actions workflows
├── manage_db.py            # Database management CLI tool
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
└── README.md                # You are here
```

## ⚠️Troubleshooting

### 🧰 Pre-commit hook not found?

If you see an error like:

```text
pre-commit: not found. Did you forget to activate your virtualenv?
```

You can solve it by installing `pre-commit` globally using [`pipx`](https://pipx.pypa.io/):

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
# Restart your terminal, then run:
pipx install pre-commit
```

This makes `pre-commit` available in all Git environments (e.g. VS Code, GitHub Desktop) without requiring a virtualenv.

## 📄 License

Copyright © 2025 Francis Bain

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

---
