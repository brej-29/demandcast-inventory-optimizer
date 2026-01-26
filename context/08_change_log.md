# Change Log

All notable changes to this project should be documented in this file.

The format loosely follows [Keep a Changelog](https://keepachangelog.com/),
with dates in `YYYY-MM-DD` format and versions incremented as the project
evolves.

## [Unreleased]

- Placeholder for upcoming changes.

## [0.2.0] - 2026-01-26

### Added

- End-to-end data → forecast → inventory workflow:
  - Robust Kaggle data loading, processed series saving, and validation.
  - Time-series feature engineering (calendar, lags, rolling stats).
  - Forecasting models: SARIMAX, ETS, Prophet-or-fallback, LightGBM with MAPIE-based intervals.
  - Weighted ensemble forecaster with conservative interval aggregation.
  - Rolling-origin backtesting utilities and reporting helpers.
- Inventory optimization engine:
  - EOQ, ROP, safety stock, annual cost calculations, and scenario presets.
  - CLI script to generate inventory recommendations and scenario tables.
- Streamlit UI refactor:
  - Root-level `app.py` and `pages/` directory for Hugging Face Spaces.
  - Shared UI components under `src/demandcast/ui/` for Home, Overview, Forecast, Inventory, Backtests.
- Demo mode assets and builder script:
  - Synthetic demo series and small artifact set under `assets/demo/` and `assets/demo_artifacts/`.
  - `scripts/build_demo_assets.py` for regenerating demo artifacts.
- New notebooks:
  - `01_kaggle_eda_and_feature_analysis.ipynb` for initial data + feature exploration.
  - `02_modeling_ensemble_inventory.ipynb` documenting models, ensembles, intervals, and inventory logic.
- CI and tests:
  - GitHub Actions workflow `.github/workflows/ci.yml`.
  - Unit tests for metrics, backtesting, Prophet fallback, LightGBM, ensemble, and inventory optimizer.

### Changed

- `README.md` updated with full pipeline instructions, demo vs Kaggle modes, and deployment guidance.
- `requirements.txt` now includes all runtime dependencies (LightGBM, MAPIE, Prophet).

### Notes

- Data (`data/`) and runtime artifacts (`artifacts/`) remain gitignored by design.
- All new functionality is designed to run in demo mode without Kaggle credentials.

## [0.1.0] - 2026-01-24

### Added

- Initial repository structure and configuration:
  - `app/` with `Home.py` and basic Streamlit pages under `app/pages/`.
  - `src/demandcast/` core package with config, logging, paths, and placeholders.
  - `scripts/` for environment verification and Kaggle data download.
  - `notebooks/` with an EDA template.
  - `context/` files for goals, scope, architecture, decisions, and logs.
  - Root `README.md`, `.gitignore`, `requirements*.txt`, and `pyproject.toml`.

### Notes

- No forecasting models or inventory optimization logic are implemented yet.
- Data and artifact directories are gitignored by design.