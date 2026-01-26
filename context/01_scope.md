# Scope

This document clarifies what is **in scope** and **out of scope** for the
DemandCast project at this stage.

## In scope

- Using the Kaggle **Store Item Demand Forecasting Challenge** dataset  
  (`demand-forecasting-kernels-only`) as the primary data source.
- Building a modular Python package under `src/demandcast/` with clear
  separation between:
  - Data loading and preprocessing
  - Feature engineering
  - Forecasting models (classical + ML)
  - Inventory optimization
  - Evaluation and metrics
- Creating a **Streamlit** dashboard:
  - Lightweight landing page and navigation
  - Forecast visualization and configuration pages
  - Inventory decision support pages
  - Backtesting and metrics pages
- Environment and reproducibility tooling:
  - Requirements files (`requirements.txt`, `requirements-extra.txt`)
  - Environment verification script (`scripts/verify_env.py`)
  - Kaggle download scaffolding (`scripts/download_kaggle_competition.*`)
- Documentation:
  - Context files (this folder)
  - Root `README.md`
  - Notebook templates for EDA

## Out of scope (for now)

These may be considered in later iterations but are not required for the core
project:

- Paid services or managed platforms that require non-free tiers.
- Complex orchestration / workflow engines (e.g., Airflow, Prefect).
- Real-time streaming ingestion or online learning.
- Highly opinionated MLOps stacks (e.g., heavy experiment tracking, feature
  stores, or multi-environment CI/CD).
- Enterprise-grade authentication/authorization in the Streamlit app.

## Assumptions

- Python 3.10+ environment is available.
- Users can install dependencies via `pip` and use the Kaggle CLI.
- The primary deployment target is a **single-node** environment (developer
  laptop, simple VM, or free Streamlit hosting), not a distributed cluster.