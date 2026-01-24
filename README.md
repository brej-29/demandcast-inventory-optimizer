# DemandCast

Time Series Forecasting + Inventory Optimization Dashboard built with Streamlit.

This repository is structured for a production-quality, **free-to-deploy** workflow around the Kaggle competition:

> Store Item Demand Forecasting Challenge (`demand-forecasting-kernels-only`)

The initial step (this repo state) focuses on project scaffolding, data download helpers, and a minimal Streamlit app that runs even before any data or models are implemented.

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

Upgrade `pip` (optional but recommended):

```bash
pip install --upgrade pip
```

### 2. Install dependencies

Base dependencies (Streamlit + core analytics stack):

```bash
pip install -r requirements.txt
```

Optional (models to be enabled in later steps):

```bash
pip install -r requirements-extra.txt
```

### 3. Verify your environment

This script prints basic environment information and checks whether key dependencies are importable.  
It always exits with status code `0` so it is safe to run in CI or local shells.

```bash
python scripts/verify_env.py
```

### 4. Run the Streamlit app

From the project root:

```bash
streamlit run app/Home.py
```

The app should start at http://localhost:8501 and display the **Hello DemandCast** landing page.  
The app is designed to load quickly even if you have not yet downloaded any data.

---

## Kaggle dataset: Store Item Demand Forecasting Challenge

This project uses the Kaggle competition:

- **Slug:** `demand-forecasting-kernels-only`
- **Competition page:** https://www.kaggle.com/c/demand-forecasting-kernels-only

### Downloading the data

Data is downloaded via the Kaggle CLI into `data/raw/`.

#### 1. Configure the Kaggle API token (once per machine)

1. Go to your Kaggle account settings and create a new API token.
2. This downloads a `kaggle.json` file.
3. Place `kaggle.json` in one of the supported locations (for example):

   - macOS / Linux: `~/.kaggle/kaggle.json`
   - Windows: `C:\Users\<USERNAME>\.kaggle\kaggle.json`

4. Ensure the file is readable only by your user (Kaggle recommends `chmod 600 ~/.kaggle/kaggle.json` on Unix-like systems).

**Important:** `kaggle.json` must never be committed to this repository. See `.gitignore`.

#### 2. Install the Kaggle CLI

```bash
pip install kaggle
```

#### 3. Run the download helper script

For Bash (macOS/Linux, WSL, Git Bash, etc.):

```bash
bash scripts/download_kaggle_competition.sh
```

For PowerShell (Windows):

```powershell
pwsh scripts/download_kaggle_competition.ps1
# or
powershell -ExecutionPolicy Bypass -File scripts/download_kaggle_competition.ps1
```

These scripts:

- Validate that the `kaggle` CLI is installed.
- Download the competition files into `data/raw/`.
- Extract the zip(s) into `data/raw/`.
- Print a listing of the resulting files.
- Fail gracefully with clear error messages if something goes wrong.

---

## Repository layout

High-level layout (simplified):

```text
app/
  Home.py                # Main Streamlit landing page
  pages/
    1_Overview.py
    2_Forecast.py
    3_Inventory.py
    4_Backtests.py

src/
  demandcast/
    config.py            # Configuration skeleton
    logging_utils.py     # get_logger() helper
    paths.py             # Common filesystem paths
    data/
      load_data.py       # Placeholder data loading helpers
    features/
      build_features.py  # Placeholder feature engineering
    models/
      ...                # Model placeholders (no implementations yet)
    inventory/
      optimizer.py       # Inventory optimization placeholder
    evaluation/
      metrics.py         # Forecasting metrics utilities

scripts/
  download_kaggle_competition.sh   # Bash helper for Kaggle download
  download_kaggle_competition.ps1  # PowerShell helper for Kaggle download
  verify_env.py                    # Environment check script

data/
  raw/        # Downloaded data from Kaggle (gitignored)
  processed/  # Cleaned / transformed data (gitignored)

artifacts/
  models/     # Saved models (gitignored)
  reports/    # Generated reports, plots, backtest outputs (gitignored)

notebooks/
  00_eda_template.ipynb  # EDA template notebook
  README.md              # Notebook usage notes

context/
  README.md              # How to use the context files
  00_goal.md             # Project goal
  01_scope.md            # In/out of scope
  02_dataset.md          # Dataset notes & download instructions
  03_architecture.md     # Architecture overview
  04_components.md       # Component breakdown
  05_decisions.md        # Decision log
  06_metrics_and_targets.md
  07_cosine_task_log.md  # Cosine-specific task log
  08_change_log.md       # Changelog
```

---

## Data and artifacts

- Raw and processed data live under `data/`.
- Models and reports live under `artifacts/`.

These directories are **not tracked in git**:

- `data/raw/`
- `data/processed/`
- `artifacts/models/`
- `artifacts/reports/`

You are free to create any subdirectories or files inside them locally without affecting version control.

---

## Next steps (beyond this scaffold)

Future steps (not yet implemented in this repo state) will include:

- Implementing forecasting models (ARIMA/SARIMAX, ETS, Prophet fallback, LightGBM, ensembles).
- Designing feature engineering pipelines for time series (lags, rolling windows, calendar features).
- Building inventory optimization logic (EOQ, safety stock, reorder points).
- Adding backtesting workflows and metrics dashboards in Streamlit.
- Integrating experiment tracking and model/report artifact management.

See the `context/` folder for the evolving design and decision log.