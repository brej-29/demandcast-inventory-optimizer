# Components

This document lists the main components of the DemandCast project and their
responsibilities.

## Streamlit app (`app/`)

- `Home.py`
  - Landing page with project description and local quickstart.
  - Must render quickly even when no data or models are present.
- `pages/1_Overview.py`
  - High-level project overview and links to documentation.
- `pages/2_Forecast.py`
  - Interface for configuring and visualizing forecasts.
- `pages/3_Inventory.py`
  - Interface for exploring inventory policies based on forecasts.
- `pages/4_Backtests.py`
  - Interface for backtests, metrics, and comparison of forecasting approaches.

## Core library (`src/demandcast/`)

- `config.py`
  - Centralized configuration objects (data paths, defaults, horizon, etc.).
- `logging_utils.py`
  - `get_logger(name)` helper with standard formatting.
- `paths.py`
  - Canonical paths for data and artifacts relative to the repo root.

### Data (`src/demandcast/data/`)

- `load_data.py`
  - Functions for loading competition datasets from `data/raw/`.
  - Responsible for logging clear errors when data is missing.

### Features (`src/demandcast/features/`)

- `build_features.py`
  - Placeholder for feature engineering logic (lags, rolling stats, calendar features).
  - Will eventually host reusable pipelines for both training and inference.

### Models (`src/demandcast/models/`)

- `arima_sarimax.py`
- `ets.py`
- `prophet_fallback.py`
- `lgbm.py`
- `ensemble.py`

Each module exposes one or more model classes, currently as **placeholders**.
Implementations will be added in later steps and should adhere to a simple,
consistent interface (`fit`, `predict`, possibly `save`/`load`).

### Inventory (`src/demandcast/inventory/`)

- `optimizer.py`
  - Placeholder for EOQ, ROP, safety stock, and related logic.
  - Will consume demand forecasts and uncertainty estimates.

### Evaluation (`src/demandcast/evaluation/`)

- `metrics.py`
  - Implementations of RMSE, MAPE, sMAPE and related metrics.
  - Used both in notebooks and in the app’s backtesting views.

## Scripts (`scripts/`)

- `verify_env.py`
  - Prints environment details and dependency status.
- `download_kaggle_competition.sh` / `.ps1`
  - Convenience scripts for downloading and extracting Kaggle data.

## Analysis (`notebooks/`)

- `00_eda_template.ipynb`
  - Structured starting point for dataset exploration.
- `README.md`
  - Notebook conventions and guidelines.

## Data and artifacts

- `data/raw/` – raw Kaggle files.
- `data/processed/` – cleaned and transformed data.
- `artifacts/models/` – saved model artifacts.
- `artifacts/reports/` – generated reports and plots.

These paths are referenced by `src/demandcast/paths.py` and are **gitignored**
to keep the repository lightweight.