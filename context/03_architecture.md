# Architecture Overview

This section describes the high-level architecture of the DemandCast project.

## Layers and responsibilities

The repository is organized into several logical layers:

1. **Interface layer (`app/`)**
   - Streamlit pages for:
     - Project overview (`Home.py`, `1_Overview.py`)
     - Forecast configuration and visualization (`2_Forecast.py`)
     - Inventory planning (`3_Inventory.py`)
     - Backtesting and evaluation (`4_Backtests.py`)
   - Keeps UI logic thin; delegates data, modeling, and optimization to the
     `src/demandcast/` package.

2. **Core library (`src/demandcast/`)**
   - **`config.py`** – central configuration objects (data locations, defaults).
   - **`logging_utils.py`** – `get_logger(name)` for consistent logging.
   - **`paths.py`** – canonical filesystem paths (repo root, data, artifacts).
   - **`data/`** – data loading utilities (e.g., `load_competition_train`).
   - **`features/`** – feature engineering (lags, rolling windows, calendar features).
   - **`models/`** – forecasting model wrappers (ARIMA/SARIMAX, ETS, Prophet, LightGBM, ensembles).
   - **`inventory/`** – inventory optimization logic (EOQ, safety stock, ROP).
   - **`evaluation/`** – metrics and evaluation helpers (RMSE, MAPE, sMAPE).

3. **Scripts (`scripts/`)**
   - Environment verification (`verify_env.py`).
   - Kaggle download helpers (`download_kaggle_competition.sh` / `.ps1`).
   - Future CLI utilities can live here.

4. **Analysis (`notebooks/`)**
   - EDA notebooks and experiments built on top of `src/demandcast/`.

5. **Data & artifacts**
   - **`data/raw/`** – raw Kaggle downloads (CSV files, etc.).
   - **`data/processed/`** – cleaned and feature-enriched datasets.
   - **`artifacts/models/`** – trained model objects.
   - **`artifacts/reports/`** – plots, evaluation reports, backtest outputs.

These folders are **gitignored** to keep the repo lightweight and free of large
binary files.

## Dataflow (conceptual)

1. **Ingestion**
   - Kaggle CLI downloads competition data into `data/raw/`.
   - `src/demandcast/data/load_data.py` provides loading functions.

2. **Feature engineering**
   - `src/demandcast/features/build_features.py` transforms raw data into
     model-ready features.

3. **Modeling**
   - `src/demandcast/models/` modules fit forecasting models and generate
     predictions at the desired horizon.

4. **Evaluation & backtesting**
   - `src/demandcast/evaluation/metrics.py` implements metrics such as RMSE,
     MAPE, and sMAPE.
   - Backtesting logic (when implemented) will coordinate data splits, model
     runs, and metric computation.

5. **Inventory optimization**
   - `src/demandcast/inventory/optimizer.py` consumes forecasts, uncertainty
     estimates, and business constraints to produce inventory recommendations.

6. **Presentation**
   - Streamlit pages in `app/` orchestrate calls into the core library and
     visualize results.

## Non-goals

- This project does **not** attempt to be a full-featured MLOps platform.
- Instead, it focuses on being a clear, well-structured reference for
  forecasting + inventory optimization in a single repository.