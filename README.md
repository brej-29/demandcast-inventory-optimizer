# DemandCast

Time Series Forecasting + Inventory Optimization Dashboard built with Streamlit.

This repository implements a production-quality, **free-to-deploy** workflow around the Kaggle competition:

> Store Item Demand Forecasting Challenge (`demand-forecasting-kernels-only`)

Key capabilities:

- Classical and ML forecasting models: SARIMAX, ETS, Prophet-or-fallback, LightGBM.
- Weighted ensemble forecaster with prediction intervals.
- Inventory optimization (EOQ, ROP, safety stock) with scenario presets.
- Streamlit dashboard that runs **in demo mode** even without Kaggle data.
- CLI scripts for end-to-end pipelines.
- CI + tests so changes are easy to trust.

---

## Quickstart

### 1. Create and activate a virtual environment (Python 3.10+)

```bash
python -m venv .venv
# On macOS/Linux
source .venv/bin/activate
# On Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

Upgrade `pip` (recommended):

```bash
pip install --upgrade pip
```

### 2. Install dependencies

All deploy dependencies are in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Verify your environment

This script prints basic environment info and checks core/optional packages.  
It always exits with status code `0`.

```bash
python scripts/verify_env.py
```

---

## Running the full pipeline

You can run DemandCast in two broad modes:

- **Demo mode (no Kaggle required)** – uses tiny synthetic assets under `assets/`.
- **Kaggle mode** – uses the full competition dataset.

### 4. (Optional) Download Kaggle data

If you want to run the full Kaggle-based pipeline:

1. Configure your Kaggle API token (`kaggle.json`) as described in `context/02_dataset.md`.
2. Install the Kaggle CLI:

   ```bash
   pip install kaggle
   ```

3. Run a download helper:

   ```bash
   # macOS / Linux / WSL
   bash scripts/download_kaggle_competition.sh

   # Windows (PowerShell)
   pwsh scripts/download_kaggle_competition.ps1
   ```

This will populate `data/raw/train.csv`.

### 5. Step 1 – Prepare data

Build a cleaned, resampled univariate series (single SKU by default) and a summary report:

```bash
python scripts/run_step1_prepare_data.py
```

Outputs:

- `data/processed/series_default.*` – processed series.
- `artifacts/reports/data_summary.json` – diagnostics (date range, monotonicity, etc.).

### 6. Step 2 – Train baseline models

Train SARIMAX, ETS, and Prophet-or-fallback on the processed series:

```bash
python scripts/run_step2_train_models.py
```

Outputs:

- `artifacts/models/sarimax.pkl`
- `artifacts/models/ets.pkl`
- `artifacts/models/prophet_or_fallback.pkl`
- `artifacts/reports/train_step2_models.json`

### 7. Step 2 – Backtest baseline models

Run rolling-origin backtests and collect metrics:

```bash
python scripts/run_step2_backtest_models.py
```

Outputs:

- `artifacts/reports/predictions_sarimax.csv`
- `artifacts/reports/predictions_ets.csv`
- `artifacts/reports/predictions_prophet_or_fallback.csv`
- `artifacts/reports/summary_table.csv`
- `artifacts/reports/backtest_metrics.json`

### 8. Step 3 – LightGBM + ensemble

Train the LightGBM forecaster and compute feature importances:

```bash
python scripts/run_step3_train_lgbm.py
```

Outputs:

- `artifacts/models/lgbm.pkl`
- `artifacts/reports/lgbm_feature_importance_gain.csv`
- `artifacts/reports/lgbm_permutation_importance.csv`

Train the ensemble forecaster (weights derived from backtest WAPE):

```bash
python scripts/run_step3_train_ensemble.py
```

Outputs:

- `artifacts/models/ensemble.pkl`
- `artifacts/reports/ensemble_weights.json`

Backtest LightGBM and Ensemble and build the model comparison table:

```bash
python scripts/run_step3_backtest_lgbm_ensemble.py
```

Outputs (in addition to the baseline ones):

- `artifacts/reports/predictions_lgbm.csv`
- `artifacts/reports/predictions_ensemble.csv`
- `artifacts/reports/model_comparison.csv` – metrics for SARIMAX, ETS, Prophet-or-fallback, LGBM, and Ensemble.

### 9. Step 4 – Inventory planning

Compute EOQ, ROP, safety stock, cost breakdown, and scenario presets based on the ensemble forecast:

```bash
python scripts/run_step4_inventory_planning.py
```

Outputs:

- `artifacts/reports/inventory_recommendations.csv` – optimized policy for the default series.
- `artifacts/reports/inventory_scenarios.csv` – conservative / balanced / aggressive scenarios.

### 10. (Optional) Build fresh demo assets

If you want to regenerate tiny demo artifacts under `assets/`:

```bash
python scripts/build_demo_assets.py
```

This uses `generate_demo_series()` to create a synthetic series, runs quick backtests, and writes:

- `assets/demo/demo_series.csv`
- `assets/demo_artifacts/model_comparison.csv`
- `assets/demo_artifacts/predictions_*.csv`
- `assets/demo_artifacts/ensemble_weights.json`

---

## Streamlit app

### Root entrypoint

For local development or Hugging Face Spaces, run:

```bash
streamlit run app.py
```

The app exposes four main pages:

1. **Home** – project description and quickstart.
2. **Overview** – data status, model leaderboard, and KPIs.
3. **Forecast** – model selector, actual vs forecast plot, CSV download.
4. **Inventory** – EOQ/ROP/safety stock, cost breakdown, scenario analysis.
5. **Backtests** – fold-by-fold error and interval coverage visualizations.

### Demo mode vs Kaggle mode

- If `data/processed/series_default.*` is present, the app uses the Kaggle-based series.
- If not, it falls back to demo assets under `assets/demo/` and `assets/demo_artifacts/`.
- All pages are designed to **fail soft**:
  - When artifacts are missing, they show clear messages and recommend which scripts to run.

---

## Hugging Face Spaces deployment

A minimal setup on HF Streamlit Spaces:

1. Create a new **Streamlit Space**.
2. Point it to this repository.
3. Ensure the Space uses `app.py` as the entrypoint (default for Streamlit Spaces).
4. The platform will automatically run:

   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

5. In demo mode (no Kaggle data), the Space will use the committed assets under `assets/`.

For more details, see `README_SPACE.md` (deployment notes for HF Spaces).

---

## Repository layout (updated)

```text
app/
  Home.py                # Legacy Streamlit entrypoint (delegates to ui.home)
  pages/                 # Legacy multipage entrypoints (delegate to ui.*)

pages/
  1_Overview.py          # Root-level Streamlit pages (HF Spaces friendly)
  2_Forecast.py
  3_Inventory.py
  4_Backtests.py

src/
  demandcast/
    __init__.py
    config.py            # Central configuration + env overrides
    logging_utils.py     # get_logger() helper
    paths.py             # Canonical filesystem paths (+ assets/demo paths)
    data/
      __init__.py
      load_data.py       # Kaggle CSV loading + target series builder
      preprocess.py      # Save/load processed series
      synthetic.py       # Synthetic demo series generator
      validate.py        # Basic series diagnostics
    features/
      build_features.py  # Time-series feature engineering
    models/
      arima_sarimax.py   # SARIMAX wrapper
      ets.py             # ETS wrapper
      prophet_fallback.py# Prophet-or-SARIMAX
      lgbm.py            # LightGBM forecaster + MAPIE intervals
      ensemble.py        # Weighted ensemble forecaster
      intervals.py       # MAPIE EnbPI helper
    evaluation/
      metrics.py         # RMSE/MAE/MAPE/sMAPE/WAPE + interval metrics
      backtest.py        # Rolling-origin backtest utilities
      reporting.py       # Helpers for saving reports
    inventory/
      optimizer.py       # EOQ/ROP/safety stock + scenarios
      policies.py        # Core policy formulas
      costing.py         # Annual cost calculations
      scenarios.py       # Conservative/balanced/aggressive presets
      service_levels.py  # Service-level → z-score mapping
    ui/
      home.py            # Streamlit render functions
      overview.py
      forecast.py
      inventory.py
      backtests.py

scripts/
  verify_env.py
  download_kaggle_competition.sh / .ps1
  run_step1_prepare_data.py
  run_step2_train_models.py
  run_step2_backtest_models.py
  run_step3_train_lgbm.py
  run_step3_train_ensemble.py
  run_step3_backtest_lgbm_ensemble.py
  run_step4_inventory_planning.py
  build_demo_assets.py

assets/
  demo/
    demo_series.csv
  demo_artifacts/
    model_comparison.csv
    predictions_*.csv
    ensemble_weights.json
    inventory_scenarios.csv

data/
  raw/        # Kaggle downloads (gitignored)
  processed/  # Processed series (gitignored)

artifacts/
  models/     # Trained model objects (gitignored)
  reports/    # Backtests, metrics, inventory reports (gitignored)

notebooks/
  00_eda_template.ipynb
  01_kaggle_eda_and_feature_analysis.ipynb
  02_modeling_ensemble_inventory.ipynb
  README.md

context/
  00_goal.md
  01_scope.md
  02_dataset.md
  03_architecture.md
  04_components.md
  05_decisions.md
  06_metrics_and_targets.md
  07_cosine_task_log.md
  08_change_log.md
  README.md
```

---

## CI and tests

GitHub Actions workflow: `.github/workflows/ci.yml`

Pipeline steps:

- Install dependencies from `requirements.txt`.
- Run unit tests via `pytest`.
- Run `scripts/verify_env.py`.
- Run a simple import smoke test (`import demandcast`).

Tests cover:

- Metrics behavior (`tests/test_metrics.py`).
- Backtest shapes (`tests/test_backtest_shapes.py`).
- Prophet fallback behavior (`tests/test_prophet_fallback.py`).
- LightGBM forecaster (`tests/test_lgbm_forecaster.py`).
- Ensemble weighting and intervals (`tests/test_ensemble.py`).
- Inventory optimizer monotonicity / sanity checks (`tests/test_inventory_optimizer.py`).

---

For deeper design context and rationale (metrics choices, architecture, inventory assumptions), see the `context/` folder and the notebooks under `notebooks/`.